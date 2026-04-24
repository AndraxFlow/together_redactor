"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-09 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "documents_snapshot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documents_snapshot_document_id"),
        "documents_snapshot",
        ["document_id"],
        unique=False,
    )

    op.create_table(
        "document_updates",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_document_updates_document_id"),
        "document_updates",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_document_updates_document_id"), table_name="document_updates")
    op.drop_table("document_updates")
    op.drop_index(op.f("ix_documents_snapshot_document_id"), table_name="documents_snapshot")
    op.drop_table("documents_snapshot")
    op.drop_table("documents")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
