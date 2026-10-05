from app.config import Settings
from app.schemas import (
    ComicOutline,
    PanelOutline,
    PromptRequest,
)


class GeminiFlashService:
    """
    Creates a compact structured comic outline.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None

        if (
            settings.gemini_api_key
            and not settings.mock_ai
        ):
            from google import genai

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    def generate_outline(
        self,
        request: PromptRequest
    ) -> ComicOutline:

        # -----------------------------------------
        # MOCK MODE
        # -----------------------------------------

        if self.settings.mock_ai:
            return ComicOutline(
                panels=[
                    PanelOutline(
                        panel_number=i,
                        title=f"Panel {i}",
                        scene_description=(
                            f"{request.character_name} explores "
                            f"the {request.setting} in a "
                            f"{request.tone} moment."
                        ),
                        image_prompt=(
                            f"{request.art_style} comic panel, "
                            f"{request.character_name} in "
                            f"{request.setting}, "
                            f"scene {i}, "
                            f"cohesive character design"
                        ),
                    )
                    for i in range(
                        1,
                        self.settings.max_panels + 1
                    )
                ]
            )

        # -----------------------------------------
        # API KEY CHECK
        # -----------------------------------------

        if not self.client:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in .env or enable MOCK_AI "
                "for local UI testing."
            )

        # -----------------------------------------
        # PROMPT
        # -----------------------------------------

        prompt = f"""
Create a cohesive
{self.settings.max_panels}-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Return exactly {self.settings.max_panels} panels.
- Keep the same main character and visual identity across panels.
- Each panel needs:
  - panel number
  - concise title
  - scene description
  - image generation prompt
- Image prompts must describe:
  - visible subjects
  - environment
  - composition
  - lighting
  - requested art style
- Do not put dialogue inside image prompts.
"""

        from google.genai import types

        response = self.client.models.generate_content(
            model=self.settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicOutline,
                temperature=0.8,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty outline."
            )

        return ComicOutline.model_validate_json(
            response.text
        )