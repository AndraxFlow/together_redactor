from typing import Optional
from sqlalchemy import select
from sqlalchemy.engine import Engine

from app.db.session import engine
from app.models.documents import document_access


def _resolve_engine(db_engine: Optional[Engine]) -> Engine:
    return db_engine or engine


def get_user_role(user_id: int, document_id: int, db_engine: Optional[Engine] = None) -> str:
    current_engine = _resolve_engine(db_engine)

    with current_engine.connect() as conn:
        row = conn.execute(
            select(document_access.c.role).where(
                document_access.c.user_id == user_id,
                document_access.c.document_id == document_id,
            )
        ).fetchone()

        return row[0] if row else None


def can_edit(user_id: int, document_id: int, db_engine: Optional[Engine] = None) -> bool:
    role = get_user_role(user_id, document_id, db_engine)
    return role in ("owner", "editor")


def can_view(user_id: int, document_id: int, db_engine: Optional[Engine] = None) -> bool:
    return get_user_role(user_id, document_id, db_engine) is not None