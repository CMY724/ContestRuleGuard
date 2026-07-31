# ContestRuleGuard - Docker deployment
FROM python:3.12-slim AS backend

WORKDIR /app
COPY backend/pyproject.toml backend/README.md ./
RUN pip install --no-cache-dir -e ".[dev]"

COPY backend/src ./src
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

EXPOSE 8000
CMD ["uvicorn", "src.contest_rule_guard.main:app", "--host", "0.0.0.0", "--port", "8000"]
