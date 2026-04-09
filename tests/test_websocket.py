from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from starlette.websockets import WebSocketDisconnect

import app.dependencies as dependencies_module
import app.services.auth_service as auth_service_module
import app.services.document_service as document_service_module
from app.db.base import metadata
from app.main import app


def build_test_client() -> TestClient:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(test_engine)
    auth_service_module.engine = test_engine
    document_service_module.engine = test_engine
    dependencies_module.get_user_by_id = (
        lambda user_id: auth_service_module.get_user_by_id(user_id, db_engine=test_engine)
    )
    return TestClient(app)


def _register_and_login(client: TestClient, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    return login_response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_websocket_broadcast_to_another_connection() -> None:
    client = build_test_client()
    owner_token = _register_and_login(client, "owner@test.com", "123456")
    doc = client.post(
        "/documents/",
        json={"title": "Realtime doc"},
        headers=_auth_header(owner_token),
    ).json()
    document_id = doc["id"]

    with client.websocket_connect(f"/ws/{document_id}?token={owner_token}") as ws_1:
        with client.websocket_connect(f"/ws/{document_id}?token={owner_token}") as ws_2:
            ws_1.send_text('{"type":"edit","content":"Hello"}')
            data = ws_2.receive_text()
            assert data == '{"type":"edit","content":"Hello"}'


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
