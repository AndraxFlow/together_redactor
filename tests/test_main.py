from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

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

def test_register() -> None:
    client = build_test_client()
    response = client.post(
        "/auth/register",
        json={"email": "test@test.com", "password": "123456"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"
    assert "id" in response.json()


def test_login() -> None:
    client = build_test_client()
    client.post("/auth/register", json={"email": "test@test.com", "password": "123456"})

    response = client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "123456"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_protected_me() -> None:
    client = build_test_client()
    client.post("/auth/register", json={"email": "test@test.com", "password": "123456"})
    login_response = client.post(
        "/auth/login",
        json={"email": "test@test.com", "password": "123456"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"