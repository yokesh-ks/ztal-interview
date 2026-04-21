from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from recruitment_agent.adapters.inbound.http.chat_routes import build_chat_router
from recruitment_agent.container import build_container


def create_app() -> FastAPI:
    app = FastAPI(title="Recruitment Agent Assignment")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    data_dir = Path(__file__).resolve().parents[3] / "data"
    app.include_router(build_chat_router(build_container(data_dir)))
    return app


app = create_app()
