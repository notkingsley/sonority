"""create User table

Revision ID: f427ab3b0151
Revises: 
Create Date: 2023-12-15 04:39:51.856230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f427ab3b0151"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "email", sa.String(length=255), unique=True, index=True, nullable=False
        ),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("username", sa.String(length=255), nullable=False, unique=True),
        sa.Column("pwd_hash", sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
