from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=3,
        max_length=2000
    )

    character_name: str = Field(
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        min_length=1,
        max_length=80
    )

    art_style: str = Field(
        min_length=1,
        max_length=100
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style"
    )
    @classmethod
    def strip_values(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: list[PanelOutline] = Field(
        min_length=1,
        max_length=10
    )


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicStory(BaseModel):
    panels: list[PanelStory] = Field(
        min_length=1,
        max_length=10
    )


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    image_url: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicLayout(BaseModel):
    panels: list[ComicPanel]
    pdf_url: str


class GenerateResponse(BaseModel):
    success: bool
    panels: list[ComicPanel]
    pdf_url: str