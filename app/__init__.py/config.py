from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    gemini_api_key: str | None = None
    hf_token: str | None = None

    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    image_backend: str = "hf"
    image_model: str = "black-forest-labs/FLUX.1-schnell"
    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    mock_ai: bool = False

    max_panels: int = 5

    image_width: int = 768
    image_height: int = 768

    data_dir: str = "app/static"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return Path(self.data_dir)

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"

    def ensure_directories(self) -> None:
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.panels_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings