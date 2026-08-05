"""order table (mock orders for scoped lookup)

Revision ID: 03d885372df8
Revises: e5b93c27a10f
Create Date: 2026-08-05 20:55:40.146588

Bảng `order` (đơn mock) cho tích hợp đơn hàng: Agent 2 tra đơn SCOPED theo `customer_id` → Agent 4 báo
trạng thái grounded. FK → user ON DELETE CASCADE (xoá khách thì đơn mock đi theo). Dữ liệu nạp bằng
`scripts/seed_orders.py` (idempotent) — KHÔNG seed trong migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03d885372df8'
down_revision: Union[str, None] = 'e5b93c27a10f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('order',
    sa.Column('order_code', sa.String(length=32), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('items_summary', sa.String(length=255), nullable=False),
    sa.Column('region', sa.String(length=64), nullable=False),
    sa.Column('ordered_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('shipped_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('estimated_delivery', sa.DateTime(timezone=True), nullable=True),
    sa.Column('tracking_code', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_customer_id'), 'order', ['customer_id'], unique=False)
    op.create_index(op.f('ix_order_order_code'), 'order', ['order_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_order_order_code'), table_name='order')
    op.drop_index(op.f('ix_order_customer_id'), table_name='order')
    op.drop_table('order')
