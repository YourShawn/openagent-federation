from fastapi import FastAPI

from .api import router as api_router
from .core.config import settings
from .db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="OpenAgent Federation API", version="0.3.0")

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    app.include_router(api_router)
    return app


app = create_app()
