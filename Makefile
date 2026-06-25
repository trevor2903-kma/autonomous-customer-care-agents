# Makefile — autonomous-customer-support-system (scaffold)
# Nguồn chân lý: PRD.md. Quy ước: CLAUDE.md.
# Lưu ý Windows: GNU make gọi cmd.exe; mỗi recipe phải tự `cd` (state không giữ giữa dòng).
# Backend dùng uv (Python 3.12 managed). Frontend/mobile dùng pnpm workspaces.

.DEFAULT_GOAL := help
.PHONY: help install dev-backend dev-dashboard dev-mobile migrate makemigration \
        health check-conn test build local-infra-up local-infra-down

help:
	@echo Targets:
	@echo   install            - cai dat deps (backend uv sync + pnpm install)
	@echo   dev-backend        - chay FastAPI (uvicorn --reload :8000)
	@echo   dev-dashboard      - chay Next.js dashboard (:3000)
	@echo   dev-mobile         - chay Expo (mobile admin)
	@echo   migrate            - alembic upgrade head
	@echo   makemigration      - alembic revision --autogenerate
	@echo   health             - curl /api/health
	@echo   check-conn         - kiem tra ket noi Neon/Upstash/Qdrant (Phase 1)
	@echo   test               - pytest backend (graph compile + 2 nhanh)
	@echo   build              - pnpm -r build
	@echo   local-infra-up     - docker compose local (du phong)
	@echo   local-infra-down   - dung docker compose local

install:
	cd apps/backend && uv sync
	pnpm install

dev-backend:
	cd apps/backend && uv run uvicorn app.main:app --reload --port 8000

dev-dashboard:
	pnpm --filter dashboard dev

dev-mobile:
	pnpm --filter mobile start

migrate:
	cd apps/backend && uv run alembic upgrade head

makemigration:
	cd apps/backend && uv run alembic revision --autogenerate -m "$(m)"

health:
	curl -s http://localhost:8000/api/health

check-conn:
	uv run --python 3.12 --with asyncpg --with redis --with qdrant-client --with python-dotenv scripts/check_connections.py

test:
	cd apps/backend && uv run pytest -q

build:
	pnpm -r build

local-infra-up:
	docker compose -f docker-compose.local.yml up -d

local-infra-down:
	docker compose -f docker-compose.local.yml down
