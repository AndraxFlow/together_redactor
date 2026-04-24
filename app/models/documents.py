import sqlalchemy
from app.db.base import metadata


documents = sqlalchemy.Table(
    "documents",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(), server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime(),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column("owner_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.LargeBinary, nullable=True),
)

documents_snapshot = sqlalchemy.Table(
    "documents_snapshot",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("document_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True),
    sqlalchemy.Column(
        "data",
        sqlalchemy.LargeBinary(),
        nullable=False,
    ),
    sqlalchemy.Column("version", sqlalchemy.Integer, nullable=False, server_default="1"),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime(),
        server_default=sqlalchemy.func.now(),
        nullable=False,
    ),
)

document_updates = sqlalchemy.Table(
    "document_updates",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.BigInteger, primary_key=True),
    sqlalchemy.Column(
        "document_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    sqlalchemy.Column(
        "data",
        sqlalchemy.LargeBinary(),
        nullable=False,
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime(),
        server_default=sqlalchemy.func.now(),
        nullable=False,
    ),
)

document_access = sqlalchemy.Table(
    "document_access",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),

    sqlalchemy.Column(
        "document_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),

    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),

    sqlalchemy.Column(
        "role",
        sqlalchemy.String(20),
        nullable=False,  # owner / editor / viewer
    ),
)