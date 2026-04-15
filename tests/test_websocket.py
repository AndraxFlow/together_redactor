from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from starlette.websockets import WebSocketDisconnect

import app.dependencies as dependencies_module
import app.services.auth_service as auth_service_module
import app.services.document_service as document_service_module
from app.db.base import metadata
from app.main import app
import app.services.access_service as access_service_module


def build_test_client() -> TestClient:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(test_engine)
    auth_service_module.engine = test_engine
    document_service_module.engine = test_engine
    access_service_module.engine = test_engine
    dependencies_module.get_user_by_id = (
        lambda user_id: auth_service_module.get_user_by_id(user_id, db_engine=test_engine)
    )
    return TestClient(app)


def _register_and_login(client: TestClient, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    return login_response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def test_websocket_broadcast_to_another_connection():
    client = build_test_client()

    owner_token = _register_and_login(client, "owner@test.com", "123456")
    editor_token = _register_and_login(client, "editor@test.com", "123456")

    doc = client.post(
        "/documents/",
        json={"title": "Realtime doc"},
        headers=_auth_header(owner_token),
    ).json()

    doc_id = doc["id"]

    with client.websocket_connect(f"/ws/{doc_id}?token={owner_token}") as ws_owner:
        with client.websocket_connect(f"/ws/{doc_id}?token={editor_token}") as ws_editor:

            # 1. initial snapshots
            owner_snapshot = ws_owner.receive_bytes()
            editor_snapshot = ws_editor.receive_bytes()

            assert isinstance(owner_snapshot, (bytes, bytearray))
            assert isinstance(editor_snapshot, (bytes, bytearray))

            # 2. owner sends update
            ws_owner.send_bytes(b'{"type":"edit","content":"Hello"}')

            # 3. editor receives it
            data = ws_editor.receive_bytes()

            assert b"Hello" in data

def test_websocket_rejects_user_without_access() -> None:
    client = build_test_client()
    owner_token = _register_and_login(client, "owner@test.com", "123456")
    other_token = _register_and_login(client, "other@test.com", "123456")

    doc = client.post(
        "/documents/",
        json={"title": "Private realtime doc"},
        headers=_auth_header(owner_token),
    ).json()
    document_id = doc["id"]

    try:
        with client.websocket_connect(f"/ws/{document_id}?token={other_token}"):
            assert False, "WebSocket should be rejected for non-owner"
    except WebSocketDisconnect as exc:
        assert exc.code == 1008
