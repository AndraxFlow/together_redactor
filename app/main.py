from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from jose import jwt, JWTError
from y_py import apply_update, encode_state_as_update

from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.services.document_service import (
    save_document_to_db,
    get_document_from_db,
)
from app.services.auth_service import get_user_by_id
from app.services.access_service import get_user_role, can_edit
from app.crdt.ydoc_manager import ydoc_manager
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(documents_router, prefix="/documents")


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
        print("WS ENTER")

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

        print('[DOCUMENT]', doc)

        role = "owner" if doc["owner_id"] == user_id else get_user_role(user_id, document_id)
        if not role:
            await websocket.close(1008)
            return

        if not can_edit(user_id, document_id):
            await websocket.close(1008)
            return

        # ✅ один YDoc на документ
        state = await ydoc_manager.get(document_id, snapshot=doc["content"])

        await websocket.accept()
        state.clients.add(websocket)

        # ✅ отправляем snapshot
        await websocket.send_bytes(state.snapshot())

        try:
            while True:
                update = await websocket.receive_bytes()

                async with state.lock:
                    apply_update(state.ydoc, update)

                # ✅ рассылаем update
                for ws in list(state.clients):
                    if ws != websocket:
                        await ws.send_bytes(update)

        except WebSocketDisconnect:
            print("WS DISCONNECT")
            state.clients.discard(websocket)

            if not state.clients:
                try:
                    save_document_to_db(document_id, state.snapshot())
                finally:
                    await ydoc_manager.remove_if_empty(document_id)

    except Exception as e:
        print("WS ERROR:", e)
        await websocket.close(1011)

@app.on_event("startup")
def startup():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@app.get("/health")
async def health():
    return {"status": "ok"}