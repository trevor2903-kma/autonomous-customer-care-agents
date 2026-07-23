"""knowledge_document: doc_type/intent/chunks + unique file_ref (sổ tài liệu console)

Revision ID: d4a71fe5c806
Revises: b8d2f60c4e19
Create Date: 2026-07-23 00:20:00.000000

Slice RAG P3. Bảng có sẵn từ scaffold nhưng CHƯA được ghi (rag_service chỉ đẩy Qdrant). Thêm cột để
`GET /rag/documents` liệt kê được tài liệu thật: `doc_type` (faq|case|reference|promotion|upload),
`intent` (frontmatter), `chunks` (số point). `file_ref` = payload.source ở Qdrant → khoá UNIQUE để
reindex upsert theo nguồn thay vì nhân bản dòng.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4a71fe5c806'
down_revision: Union[str, None] = 'b8d2f60c4e19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('knowledge_document', sa.Column('doc_type', sa.String(length=16), nullable=True))
    op.add_column('knowledge_document', sa.Column('intent', sa.String(length=64), nullable=True))
    op.add_column(
        'knowledge_document',
        sa.Column('chunks', sa.Integer(), server_default='0', nullable=False),
    )
    # Bảng chưa từng được ghi -> không cần dọn trùng trước khi tạo UNIQUE.
    op.create_unique_constraint('uq_knowledge_document_file_ref', 'knowledge_document', ['file_ref'])


def downgrade() -> None:
    op.drop_constraint('uq_knowledge_document_file_ref', 'knowledge_document', type_='unique')
    op.drop_column('knowledge_document', 'chunks')
    op.drop_column('knowledge_document', 'intent')
    op.drop_column('knowledge_document', 'doc_type')
