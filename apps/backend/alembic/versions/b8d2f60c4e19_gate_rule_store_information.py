"""gate_intent_rule cho intent store_information

Revision ID: b8d2f60c4e19
Revises: a7e4c1b93d52
Create Date: 2026-07-23 00:10:00.000000

Slice RAG P1.5. Hỏi giờ mở cửa/địa chỉ/hotline là TRONG phạm vi shop nhưng 14 intent trước đó không có
chỗ chứa → rơi vào `other` → cờ `out_of_domain` → escalate oan (đúng lỗi vừa sửa cho "xin chào").
Intent thông tin, không nhạy cảm → `send_directly=True`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b8d2f60c4e19'
down_revision: Union[str, None] = 'a7e4c1b93d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    gate_intent_rule = sa.table(
        'gate_intent_rule',
        sa.column('intent', sa.String),
        sa.column('label', sa.String),
        sa.column('sensitive', sa.Boolean),
        sa.column('send_directly', sa.Boolean),
    )
    op.bulk_insert(
        gate_intent_rule,
        [{'intent': 'store_information', 'label': 'Thông tin cửa hàng', 'sensitive': False, 'send_directly': True}],
    )


def downgrade() -> None:
    op.execute("DELETE FROM gate_intent_rule WHERE intent = 'store_information'")
