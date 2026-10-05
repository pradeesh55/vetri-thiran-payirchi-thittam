from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import create_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_directories()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI comic story creator using Gemini and AI image generation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(settings.static_dir)),
    name="static",
)

app.include_router(create_router(settings))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "mock_ai": settings.mock_ai,
        "image_backend": settings.image_backend,
    }