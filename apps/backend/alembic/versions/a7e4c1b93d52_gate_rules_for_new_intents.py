"""gate_intent_rule cho 4 intent mới (greeting, return_exchange_policy, payment, membership)

Revision ID: a7e4c1b93d52
Revises: c3f1a9d47b28
Create Date: 2026-07-23 00:00:00.000000

Slice RAG P1. Taxonomy mở rộng 10 → 14 intent. ⚠️ GOTCHA: `send_directly_for` trả False cho intent
KHÔNG có luật → intent mới mà thiếu dòng ở đây sẽ bị GIỮ NHÁP OAN. Cả 4 đều là intent THÔNG TIN
(không nhạy cảm) → `send_directly=True`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a7e4c1b93d52'
down_revision: Union[str, None] = 'c3f1a9d47b28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_INTENTS = ('greeting', 'return_exchange_policy', 'payment', 'membership')


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
        [
            {'intent': 'payment', 'label': 'Thanh toán', 'sensitive': False, 'send_directly': True},
            {'intent': 'return_exchange_policy', 'label': 'Chính sách đổi/trả', 'sensitive': False, 'send_directly': True},
            {'intent': 'membership', 'label': 'Thành viên', 'sensitive': False, 'send_directly': True},
            {'intent': 'greeting', 'label': 'Chào hỏi', 'sensitive': False, 'send_directly': True},
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text('DELETE FROM gate_intent_rule WHERE intent IN :intents').bindparams(
            sa.bindparam('intents', value=_NEW_INTENTS, expanding=True)
        )
    )
