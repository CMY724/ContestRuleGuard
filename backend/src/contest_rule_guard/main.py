from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from contest_rule_guard.core.config import Settings, get_settings
from contest_rule_guard.core.deepseek_provider import DeepSeekProvider
from contest_rule_guard.core.model_budget import BudgetExceeded
from contest_rule_guard.db.session import build_engine, build_session_factory
from contest_rule_guard.evidence.api import router as evidence_router
from contest_rule_guard.graph.api import router as graph_router
from contest_rule_guard.ingestion.api import router as ingestion_router
from contest_rule_guard.ingestion.registry import UnsupportedDocumentError
from contest_rule_guard.projects.dependencies import build_project_cleanup_registry
from contest_rule_guard.projects.router import router as projects_router
from contest_rule_guard.rules.api import router as rules_router


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()

    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        yield
        provider = getattr(_app.state, "model_provider", None)
        if isinstance(provider, DeepSeekProvider):
            await provider.close()

    app = FastAPI(title=resolved.app_name, version="0.1.0", lifespan=_lifespan)
    app.state.settings = resolved
    if resolved.deepseek_api_key:
        app.state.model_provider = DeepSeekProvider(
            api_key=resolved.deepseek_api_key,
            model=resolved.deepseek_model,
            timeout_s=resolved.deepseek_timeout_s,
        )
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
    app.include_router(evidence_router)
    app.include_router(rules_router)
    app.include_router(graph_router)

    @app.exception_handler(BudgetExceeded)
    async def budget_exceeded_handler(request: Request, exc: BudgetExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=402,
            content={"detail": str(exc), "type": "budget_exceeded"},
        )

    @app.exception_handler(UnsupportedDocumentError)
    async def unsupported_document_handler(
        request: Request, exc: UnsupportedDocumentError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=415,
            content={"detail": str(exc), "type": "unsupported_document"},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc), "type": "value_error"},
        )

    return app


app = create_app()
