from app.config import Settings
from app.schemas import (
    ComicOutline,
    ComicStory,
    PromptRequest,
)


class GeminiProService:
    """
    Expands the outline into narration,
    captions, dialogue and refined image prompts.
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

    def generate_story(
        self,
        request: PromptRequest,
        outline: ComicOutline
    ) -> ComicStory:

        # -----------------------------------------
        # MOCK MODE
        # -----------------------------------------

        if self.settings.mock_ai:
            return ComicStory(
                panels=[
                    {
                        "panel_number": panel.panel_number,
                        "title": panel.title,
                        "scene_description": panel.scene_description,
                        "caption": "A new chapter begins.",
                        "narration": (
                            f"{request.character_name} "
                            f"takes another step through "
                            f"the {request.setting}."
                        ),
                        "dialogue": "We can do this!",
                        "image_prompt": panel.image_prompt,
                    }
                    for panel in outline.panels
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

        outline_json = outline.model_dump_json(
            indent=2
        )

        # -----------------------------------------
        # PROMPT
        # -----------------------------------------

        prompt = f"""
Write the complete panel-by-panel comic story
using this outline.

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

Outline:
{outline_json}

Requirements:

- Preserve the same panel numbers and titles.
- Every panel needs:
  - scene description
  - ambient caption
  - narration
  - natural dialogue
  - refined image prompt
- Keep character identity consistent.
- Keep story continuity consistent.
- Keep dialogue suitable for a general audience.
- Image prompts must describe visuals only.
- Do not include speech bubbles or written text
  inside image prompts.
"""

        from google.genai import types

        response = self.client.models.generate_content(
            model=self.settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicStory,
                temperature=0.9,
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty story."
            )

        return ComicStory.model_validate_json(
            response.text
        )