"""audit_log: turn_id (khóa gom lượt) + duration_ms + index created_at

Revision ID: e5b93c27a10f
Revises: d4a71fe5c806
Create Date: 2026-07-30 00:00:00.000000

Slice observability P1. `audit_log` là NGUỒN của tab Báo cáo nhưng đang thiếu hai thứ để dùng được:

- `turn_id`: khoá GOM một lượt khách. Không có nó thì không nối được dòng `intent` với dòng `decision`
  của CÙNG lượt → không tính được "%auto theo intent", và drill-down 4 agent không dựng lại được.
- `duration_ms`: thời gian của BƯỚC đó (dòng `delivery` mang end-to-end cả lượt cho NFR-1 ≤ 5s).

Kèm index `created_at`: mọi truy vấn báo cáo đều lọc theo khoảng thời gian (hôm nay/7 ngày); bảng chỉ
có sẵn index `conversation_id` nên thiếu index này là full-scan mỗi lần mở tab.

Cả hai cột NULL được: dòng audit CŨ (do task nền REST ghi) không có giá trị, và dòng `customer` cũng
không có `duration_ms`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e5b93c27a10f'
down_revision: Union[str, None] = 'd4a71fe5c806'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audit_log', sa.Column('turn_id', sa.UUID(), nullable=True))
    op.add_column('audit_log', sa.Column('duration_ms', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_audit_log_turn_id'), 'audit_log', ['turn_id'], unique=False)
    op.create_index(op.f('ix_audit_log_created_at'), 'audit_log', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_log_created_at'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_turn_id'), table_name='audit_log')
    op.drop_column('audit_log', 'duration_ms')
    op.drop_column('audit_log', 'turn_id')
