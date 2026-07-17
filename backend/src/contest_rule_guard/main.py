from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contest_rule_guard.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    app = FastAPI(title=resolved.app_name, version="0.1.0")
    app.state.settings = resolved
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

    return app


app = create_app()
