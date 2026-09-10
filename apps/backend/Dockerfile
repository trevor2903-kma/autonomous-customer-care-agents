# Backend Dockerfile (scaffold) — managed-first nên container chỉ để dự phòng/deploy sau.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# uv để quản deps (khớp dev)
RUN pip install --no-cache-dir uv

# Cài deps trước (cache layer)
COPY pyproject.toml ./
COPY uv.lock* ./
RUN uv sync --no-dev || true

COPY . .
RUN uv sync --no-dev

EXPOSE 8000
# --ws-max-size: trần 64 KiB mỗi frame WebSocket (SEC-XC.2) — tin khách đã cap max_message_chars, frame to hơn chỉ tốn CPU.
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --ws-max-size 65536"]
