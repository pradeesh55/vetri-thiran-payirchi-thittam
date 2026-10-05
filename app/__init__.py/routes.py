from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.schemas import GenerateResponse, PromptRequest
from app.services.comic_service import ComicService


def create_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    templates = Jinja2Templates(
        directory="app/templates"
    )

    service = ComicService(settings)

    @router.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": settings.app_name
            }
        )

    @router.post("/generate", response_class=HTMLResponse)
    async def generate_form(
        request: Request,
        story_prompt: str = Form(...),
        character_name: str = Form(...),
        setting: str = Form(...),
        tone: str = Form(...),
        art_style: str = Form(...),
    ):
        try:
            payload = PromptRequest(
                story_prompt=story_prompt,
                character_name=character_name,
                setting=setting,
                tone=tone,
                art_style=art_style,
            )

            panels, pdf_url = service.generate(payload)

            return templates.TemplateResponse(
                request=request,
                name="comic_preview.html",
                context={
                    "app_name": settings.app_name,
                    "panels": panels,
                    "pdf_url": pdf_url,
                },
            )

        except Exception as exc:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "app_name": settings.app_name,
                    "error": str(exc),
                },
                status_code=500,
            )

    @router.post(
        "/generate-comic/json",
        response_model=GenerateResponse
    )
    async def generate_json(
        payload: PromptRequest
    ):
        try:
            panels, pdf_url = service.generate(payload)

            return GenerateResponse(
                success=True,
                panels=panels,
                pdf_url=pdf_url,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc)
            ) from exc

    @router.get(
        "/export-success",
        response_class=HTMLResponse
    )
    async def export_success(
        request: Request,
        pdf: str | None = None
    ):
        return templates.TemplateResponse(
            request=request,
            name="export_success.html",
            context={
                "app_name": settings.app_name,
                "pdf_url": pdf,
            },
        )

    @router.post("/test-image")
    async def test_image(
        prompt: str = Form(...)
    ):
        try:
            image_url = service.generate_test_image(prompt)

            return {
                "success": True,
                "image_url": image_url,
            }

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=str(exc)
            ) from exc

    return router