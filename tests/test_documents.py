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

def _register_and_login(client: TestClient, email: str, password: str) -> str:
    client.post("/auth/register", json={"email": email, "password": password})
    login_response = client.post("/auth/login", json={"email": email, "password": password})
    return login_response.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_document() -> None:
    client = build_test_client()
    token = _register_and_login(client, "owner@test.com", "123456")

    response = client.post(
        "/documents/",
        json={"title": "My document"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    assert response.json()["title"] == "My document"
    assert response.json()["owner_id"] == 1


def test_get_documents_list() -> None:
    client = build_test_client()
    token = _register_and_login(client, "owner@test.com", "123456")

    client.post("/documents/", json={"title": "Doc 1"}, headers=_auth_header(token))
    client.post("/documents/", json={"title": "Doc 2"}, headers=_auth_header(token))

    response = client.get("/documents/", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_single_document() -> None:
    client = build_test_client()
    token = _register_and_login(client, "owner@test.com", "123456")

    created = client.post(
        "/documents/",
        json={"title": "Single Doc"},
        headers=_auth_header(token),
    ).json()
    doc_id = created["id"]

    response = client.get(f"/documents/{doc_id}", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


def test_update_document() -> None:
    client = build_test_client()
    token = _register_and_login(client, "owner@test.com", "123456")

    created = client.post(
        "/documents/",
        json={"title": "Old title"},
        headers=_auth_header(token),
    ).json()

    response = client.patch(
        f"/documents/{created['id']}",
        json={"title": "New title"},
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"


def test_delete_document() -> None:
    client = build_test_client()
    token = _register_and_login(client, "owner@test.com", "123456")

    created = client.post(
        "/documents/",
        json={"title": "Delete me"},
        headers=_auth_header(token),
    ).json()

    delete_response = client.delete(
        f"/documents/{created['id']}",
        headers=_auth_header(token),
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/documents/{created['id']}", headers=_auth_header(token))
    assert get_response.status_code == 404


def test_access_denied_for_other_user() -> None:
    client = build_test_client()
    owner_token = _register_and_login(client, "owner@test.com", "123456")
    other_token = _register_and_login(client, "other@test.com", "123456")

    created = client.post(
        "/documents/",
        json={"title": "Private doc"},
        headers=_auth_header(owner_token),
    ).json()
    doc_id = created["id"]

    response = client.get(f"/documents/{doc_id}", headers=_auth_header(other_token))
    assert response.status_code == 403