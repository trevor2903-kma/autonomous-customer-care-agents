"""Cấu hình logging tối thiểu (scaffold).

TODO (PRD §18 NFR-8): tích hợp Langfuse cho token cost/latency/error rate ở phase sau.
"""

from __future__ import annotations

import logging

from .config import settings

_CONFIGURED = False


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s :: %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
