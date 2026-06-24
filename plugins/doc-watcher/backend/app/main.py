from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import build_router
from app.config import settings
from app.database.session import init_db


def create_app(*, include_legacy_routes: bool | None = None) -> FastAPI:
    legacy_routes_enabled = (
        settings.docwatcher_enable_legacy_routes
        if include_legacy_routes is None
        else include_legacy_routes
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if legacy_routes_enabled:
            init_db()
        yield

    app = FastAPI(title="DocWatcher", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(build_router(include_legacy_routes=legacy_routes_enabled))

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
