from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from jose import jwt, JWTError
# from y_py import apply_update, encode_state_as_update
from collections import defaultdict

from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.services.document_service import (
    save_document_to_db,
    get_document_from_db,
)
from app.services.auth_service import get_user_by_id
from app.services.access_service import get_user_role, can_edit
# from app.crdt.ydoc_manager import ydoc_manager
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.services.document_service import save_update, get_updates
from app.models.documents import document_updates
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(documents_router, prefix="/documents")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: dict[int, set[WebSocket]] = defaultdict(set)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except Exception:
        raise Exception("Invalid token")

@app.get("/")
def root():
    return {"msg": "OK"}


@app.websocket("/ws/{document_id}")
async def ws_doc(websocket: WebSocket, document_id: int):
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(1008)
            return

        user_id = decode_token(token)
        user = get_user_by_id(user_id)
        if not user:
            await websocket.close(1008)
            return

        doc = get_document_from_db(document_id)
        if not doc:
            await websocket.close(1008)
            return

        role = "owner" if doc["owner_id"] == user_id else get_user_role(user_id, document_id, engine)

        if not role or not can_edit(user_id, document_id, engine):
            print("WS ACCESS DENIED:", {
                "user_id": user_id,
                "document_id": document_id,
                "role": role
            })
            await websocket.close(1008)
            return
        if not role:
            print("NO ROLE")
        if not can_edit(user_id, document_id, engine):
            print("NO EDIT PERMISSION")

        await websocket.accept()
        connections[document_id].add(websocket)

        # # 1. snapshot
        # if doc["content"]:
        #     await websocket.send_bytes(doc["content"])

        # 2. updates
        updates = get_updates(document_id)

        for u in updates:
            try:
                await websocket.send_bytes(u["data"])
            except Exception:
                # Client disconnected before we finished sending backlog.
                return

        try:
            while True:
                try:
                    update = await websocket.receive_bytes()
                except WebSocketDisconnect:
                    break
                except Exception as exc:
                    print("WS receive error:", exc)
                    break

                save_update(document_id, update)

                for ws in list(connections[document_id]):
                    if ws == websocket:
                        continue
                    try:
                        await ws.send_bytes(update)
                    except Exception:
                        connections[document_id].discard(ws)

        finally:
            connections[document_id].discard(websocket)
            if not connections[document_id]:
                del connections[document_id]

    except Exception as e:
        print("WS ERROR:", e)
        try:
            await websocket.close(1011)
        except Exception:
            pass

@app.on_event("startup")
def startup():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@app.get("/health")
async def health():
    return {"status": "ok"}