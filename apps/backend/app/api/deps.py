"""Dependencies dùng chung cho route.

Scaffold: chỉ DB session. TODO (PRD §18 NFR-5): JWT auth + RBAC (Admin) ở phase sau.
"""

from __future__ import annotations

from ..core.database import get_session

__all__ = ["get_session"]
