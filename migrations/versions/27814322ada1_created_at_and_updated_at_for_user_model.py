"""created_at and updated_at for User model

Revision ID: 27814322ada1
Revises: bc531810d645
Create Date: 2023-12-24 14:18:33.244197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27814322ada1"
down_revision: Union[str, None] = "bc531810d645"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=False))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
