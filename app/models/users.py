import sqlalchemy
from app.db.base import metadata


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True, index=True, nullable=False),
    sqlalchemy.Column("hashed_password", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(), server_default=sqlalchemy.func.now(), nullable=False),
)