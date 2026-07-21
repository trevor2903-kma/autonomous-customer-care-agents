"""auth user + gate_config/gate_intent_rule + conversation.customer_id + seed gate

Revision ID: c3f1a9d47b28
Revises: 0080e6c2bf8f
Create Date: 2026-07-21 00:00:00.000000

Slice 11 P0. Bảng `user` (RBAC), gate động DB (gate_config singleton + gate_intent_rule),
cột conversation.customer_id (FK → user, NULL cho guest). Kèm data seed gate (khớp plan §3.3).
Admin seed nằm ở scripts/seed_admin.py (đọc env) — KHÔNG nhét secret vào migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3f1a9d47b28'
down_revision: Union[str, None] = '0080e6c2bf8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user (RBAC admin|customer) ────────────────────────────────────────────
    op.create_table(
        'user',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    # ── gate_config (singleton id=1) ──────────────────────────────────────────
    op.create_table(
        'gate_config',
        sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
        sa.Column('auto_reply_enabled', sa.Boolean(), nullable=False),
        sa.Column('auto_resolve_enabled', sa.Boolean(), nullable=False),
        sa.Column('auto_resolve_minutes', sa.Integer(), nullable=False),
        sa.Column('retrieval_threshold', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── gate_intent_rule (PK=intent) ──────────────────────────────────────────
    op.create_table(
        'gate_intent_rule',
        sa.Column('intent', sa.String(length=64), nullable=False),
        sa.Column('label', sa.String(length=64), nullable=False),
        sa.Column('sensitive', sa.Boolean(), nullable=False),
        sa.Column('send_directly', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('intent'),
    )

    # ── conversation.customer_id (FK → user, NULL cho guest/legacy) ───────────
    op.add_column('conversation', sa.Column('customer_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_conversation_customer_id'), 'conversation', ['customer_id'], unique=False)
    op.create_foreign_key(
        'fk_conversation_customer_id_user',
        'conversation', 'user',
        ['customer_id'], ['id'],
        ondelete='SET NULL',
    )

    # ── Data seed: gate_config + 10 intent rule (plan §3.3) ───────────────────
    gate_config = sa.table(
        'gate_config',
        sa.column('id', sa.Integer),
        sa.column('auto_reply_enabled', sa.Boolean),
        sa.column('auto_resolve_enabled', sa.Boolean),
        sa.column('auto_resolve_minutes', sa.Integer),
        sa.column('retrieval_threshold', sa.Float),
    )
    op.bulk_insert(
        gate_config,
        [{
            'id': 1,
            'auto_reply_enabled': True,
            'auto_resolve_enabled': True,
            'auto_resolve_minutes': 30,
            'retrieval_threshold': 0.35,
        }],
    )

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
            {'intent': 'product_price', 'label': 'Giá sản phẩm', 'sensitive': False, 'send_directly': True},
            {'intent': 'product_information', 'label': 'Thông tin sản phẩm', 'sensitive': False, 'send_directly': True},
            {'intent': 'size_consulting', 'label': 'Tư vấn size', 'sensitive': False, 'send_directly': True},
            {'intent': 'shipping', 'label': 'Vận chuyển', 'sensitive': False, 'send_directly': True},
            {'intent': 'order_status', 'label': 'Trạng thái đơn', 'sensitive': False, 'send_directly': True},
            {'intent': 'promotion', 'label': 'Khuyến mãi', 'sensitive': False, 'send_directly': True},
            {'intent': 'refund', 'label': 'Hoàn tiền', 'sensitive': True, 'send_directly': False},
            {'intent': 'exchange', 'label': 'Đổi hàng', 'sensitive': True, 'send_directly': False},
            {'intent': 'complaint', 'label': 'Khiếu nại', 'sensitive': True, 'send_directly': False},
            {'intent': 'other', 'label': 'Khác', 'sensitive': False, 'send_directly': False},
        ],
    )


def downgrade() -> None:
    op.drop_constraint('fk_conversation_customer_id_user', 'conversation', type_='foreignkey')
    op.drop_index(op.f('ix_conversation_customer_id'), table_name='conversation')
    op.drop_column('conversation', 'customer_id')
    op.drop_table('gate_intent_rule')
    op.drop_table('gate_config')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
