from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.engine import Engine

from app.db.session import engine
from app.models.documents import documents
from app.services.access_service import get_user_role, can_edit
from app.models.documents import document_access


def _resolve_engine(db_engine: Optional[Engine]) -> Engine:
    return db_engine or engine


# =========================
# ACCESS LAYER (единая точка)
# =========================
def _get_accessible_document(user: dict, document_id: int, db_engine: Optional[Engine]):
    current_engine = _resolve_engine(db_engine)

    with current_engine.connect() as conn:
        doc = conn.execute(
            select(documents).where(documents.c.id == document_id)
        ).mappings().first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    role = get_user_role(user["id"], document_id, current_engine)

    if not role:
        raise HTTPException(status_code=403, detail="No access")

    return dict(doc), role


# =========================
# PUBLIC API
# =========================
def create_document(user: dict, data: dict, db_engine: Optional[Engine] = None) -> dict:
    current_engine = _resolve_engine(db_engine)

    query = (
        documents.insert()
        .values(title=data["title"], owner_id=user["id"])
        .returning(
            documents.c.id,
            documents.c.title,
            documents.c.owner_id,
            documents.c.created_at,
            documents.c.updated_at,
        )
    )

    with current_engine.begin() as conn:
        result = conn.execute(query).mappings().first()

        conn.execute(
            document_access.insert().values(
                document_id=result["id"],
                user_id=user["id"],
                role="owner",
            )
        )

    return dict(result)

def get_documents(user: dict, db_engine=None) -> list[dict]:
    current_engine = _resolve_engine(db_engine)

    query = (
        select(
            documents.c.id,
            documents.c.title,
            documents.c.owner_id,
            documents.c.created_at,
            documents.c.updated_at,
        )
        .select_from(
            documents.join(
                document_access,
                document_access.c.document_id == documents.c.id
            )
        )
        .where(document_access.c.user_id == user["id"])
    )

    with current_engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    return [dict(r) for r in rows]

def get_document_by_id(user: dict, document_id: int, db_engine: Optional[Engine] = None) -> dict:
    doc, _ = _get_accessible_document(user, document_id, db_engine)
    return doc


def update_document(user: dict, document_id: int, data: dict, db_engine: Optional[Engine] = None) -> dict:
    current_engine = _resolve_engine(db_engine)

    doc, _ = _get_accessible_document(user, document_id, current_engine)

    if not can_edit(user["id"], document_id, current_engine):
        raise HTTPException(status_code=403, detail="Read-only access")

    update_data = {}

    if data.get("title"):
        update_data["title"] = data["title"]

    if not update_data:
        return doc

    query = (
        update(documents)
        .where(documents.c.id == document_id)
        .values(**update_data)
        .returning(
            documents.c.id,
            documents.c.title,
            documents.c.owner_id,
            documents.c.created_at,
            documents.c.updated_at,
        )
    )

    with current_engine.begin() as conn:
        updated = conn.execute(query).mappings().first()

    return dict(updated)


def delete_document(user: dict, document_id: int, db_engine: Optional[Engine] = None) -> None:
    current_engine = _resolve_engine(db_engine)

    _, role = _get_accessible_document(user, document_id, current_engine)

    if role != "owner":
        raise HTTPException(status_code=403, detail="Only owner can delete")

    with current_engine.begin() as conn:
        conn.execute(delete(documents).where(documents.c.id == document_id))


# =========================
# SNAPSHOT STORAGE (OK оставить здесь)
# =========================
def save_document_to_db(document_id: int, content: bytes):
    with engine.begin() as conn:
        conn.execute(
            documents.update()
            .where(documents.c.id == document_id)
            .values(content=content)
        )


def get_document_from_db(document_id: int):
    with engine.connect() as conn:
        return conn.execute(
            documents.select().where(documents.c.id == document_id)
        ).mappings().first()