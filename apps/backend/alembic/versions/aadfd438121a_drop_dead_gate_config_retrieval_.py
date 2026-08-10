"""drop dead gate_config.retrieval_threshold

Revision ID: aadfd438121a
Revises: 03d885372df8
Create Date: 2026-08-10 22:08:21.251439

Cột CHẾT: pipeline chưa bao giờ đọc nó (Agent 2 dùng `settings.retrieval_threshold`), nên giá trị 0.35 trong
DB chỉ khiến màn Cấu hình Gate hiển thị một con số KHÁC con số đang chạy (0.40). Ngưỡng là giá trị ĐO
(`scripts/measure_threshold.py`) → thuộc về config/env, không phải nút UI.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aadfd438121a'
down_revision: Union[str, None] = '03d885372df8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('gate_config', 'retrieval_threshold')


def downgrade() -> None:
    # `server_default` là BẮT BUỘC ở đây: bảng đã có hàng (singleton id=1) nên thêm cột NOT NULL mà không có
    # default sẽ lỗi. Bỏ default ngay sau đó để khớp schema gốc (cột không có server_default).
    op.add_column(
        'gate_config',
        sa.Column('retrieval_threshold', sa.Float(), nullable=False, server_default='0.35'),
    )
    op.alter_column('gate_config', 'retrieval_threshold', server_default=None)
