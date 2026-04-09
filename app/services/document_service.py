from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.engine import Engine

from app.db.session import engine
from app.models.documents import documents


def _resolve_engine(db_engine: Optional[Engine]) -> Engine:
    return db_engine or engine


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
    with current_engine.begin() as connection:
        result = connection.execute(query).mappings().first()
    return dict(result)


def get_documents(user: dict, db_engine: Optional[Engine] = None) -> list[dict]:
    current_engine = _resolve_engine(db_engine)
    query = (
        select(
            documents.c.id,
            documents.c.title,
            documents.c.owner_id,
            documents.c.created_at,
            documents.c.updated_at,
        )
        .where(documents.c.owner_id == user["id"])
        .order_by(documents.c.id.desc())
    )
    with current_engine.connect() as connection:
        rows = connection.execute(query).mappings().all()
    return [dict(row) for row in rows]


def _get_owned_document(user: dict, document_id: int, db_engine: Optional[Engine]) -> dict:
    current_engine = _resolve_engine(db_engine)
    with current_engine.connect() as connection:
        doc = (
            connection.execute(select(documents).where(documents.c.id == document_id))
            .mappings()
            .first()
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc["owner_id"] != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return dict(doc)


def get_document_by_id(user: dict, document_id: int, db_engine: Optional[Engine] = None) -> dict:
    return _get_owned_document(user, document_id, db_engine)


def update_document(
    user: dict, document_id: int, data: dict, db_engine: Optional[Engine] = None
) -> dict:
    current_engine = _resolve_engine(db_engine)
    _get_owned_document(user, document_id, current_engine)

    update_data = {}
    if data.get("title") is not None:
        update_data["title"] = data["title"]

    if not update_data:
        return _get_owned_document(user, document_id, current_engine)

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
    with current_engine.begin() as connection:
        updated = connection.execute(query).mappings().first()
    return dict(updated)


def delete_document(user: dict, document_id: int, db_engine: Optional[Engine] = None) -> None:
    current_engine = _resolve_engine(db_engine)
    _get_owned_document(user, document_id, current_engine)
    with current_engine.begin() as connection:
        connection.execute(delete(documents).where(documents.c.id == document_id))
