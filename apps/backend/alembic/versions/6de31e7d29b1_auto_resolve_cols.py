"""auto_resolve cols

Revision ID: 6de31e7d29b1
Revises: aadfd438121a
Create Date: 2026-08-28 13:39:51.162999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6de31e7d29b1'
down_revision: Union[str, None] = 'aadfd438121a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversation",
        sa.Column("auto_resolve_reminded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "gate_config",
        sa.Column(
            "auto_resolve_grace_minutes", sa.Integer(), nullable=False, server_default="15"
        ),
    )


def downgrade() -> None:
    op.drop_column("gate_config", "auto_resolve_grace_minutes")
    op.drop_column("conversation", "auto_resolve_reminded_at")
