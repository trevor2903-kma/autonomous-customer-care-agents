"""message.client_msg_id + partial unique index (idempotency tin nhắn)

Revision ID: 7c4e2a9f1b3d
Revises: 6de31e7d29b1
Create Date: 2026-09-10 00:00:00.000000

Audit v2 (IDEM-XC.1 / FE-01.4): client sinh `client_msg_id` (uuid v4) cho mỗi tin và dùng lại NGUYÊN VĂN khi gửi
lại. Server lưu nó cùng tin; partial unique index (conversation_id, client_msg_id) — chỉ áp khi có giá trị — là
lớp bảo đảm BỀN chống chạy pipeline hai lần cho cùng một tin (registry in-process ở WS là lớp nhanh phía trước).

NULL được: tin cũ, tin hệ thống (auto-resolve, duyệt nháp) và client legacy gửi chữ thô không có id.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7c4e2a9f1b3d'
down_revision: Union[str, None] = '6de31e7d29b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('message', sa.Column('client_msg_id', sa.String(length=64), nullable=True))
    op.create_index(
        'uq_message_conversation_client_msg_id',
        'message',
        ['conversation_id', 'client_msg_id'],
        unique=True,
        postgresql_where=sa.text('client_msg_id IS NOT NULL'),
    )


def downgrade() -> None:
    op.drop_index('uq_message_conversation_client_msg_id', table_name='message')
    op.drop_column('message', 'client_msg_id')
