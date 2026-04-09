from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from app.dependencies import get_current_user
from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.services.document_service import get_document_by_id
from app.websocket.connection_manager import ConnectionManager

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(documents_router, prefix="/documents")
manager = ConnectionManager()


@app.on_event("startup")
def startup() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):  # type: ignore
    return {"item_id": item_id, "q": q}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws/{document_id}")
async def websocket_document_sync(websocket: WebSocket, document_id: int) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        current_user = get_current_user(token)
        get_document_by_id(current_user, document_id)
    except HTTPException:
        await websocket.close(code=1008)
        return

    await manager.connect(document_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast_except_sender(document_id, message, websocket)
    except WebSocketDisconnect:
        manager.disconnect(document_id, websocket)