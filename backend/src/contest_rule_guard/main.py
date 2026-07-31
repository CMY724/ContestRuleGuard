from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contest_rule_guard.core.config import Settings, get_settings
from contest_rule_guard.db.session import build_engine, build_session_factory
from contest_rule_guard.ingestion.api import router as ingestion_router
from contest_rule_guard.projects.dependencies import build_project_cleanup_registry
from contest_rule_guard.projects.router import router as projects_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    app = FastAPI(title=resolved.app_name, version="0.1.0")
    app.state.settings = resolved
    engine = build_engine(resolved.database_url)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": resolved.app_name,
            "environment": resolved.environment,
        }

    app.state.project_cleanup_registry = build_project_cleanup_registry(resolved)
    app.include_router(projects_router)
    app.include_router(ingestion_router)
    return app


app = create_app()
