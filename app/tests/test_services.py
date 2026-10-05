from pathlib import Path

from app.config import Settings
from app.schemas import PromptRequest
from app.services.comic_service import ComicService


def test_mock_generation_end_to_end(
    tmp_path: Path
):

    settings = Settings(
        mock_ai=True,
        data_dir=str(
            tmp_path / "static"
        ),
        max_panels=5,
    )

    settings.ensure_directories()

    service = ComicService(
        settings
    )

    request = PromptRequest(
        story_prompt=(
            "A fox discovers "
            "a hidden library."
        ),
        character_name="Luna",
        setting="Enchanted forest",
        tone="Funny",
        art_style="Comic book",
    )

    panels, pdf_url = (
        service.generate(
            request
        )
    )

    assert len(panels) == 5

    assert pdf_url.startswith(
        "/static/exports/"
    )

    assert (
        settings.exports_dir /
        Path(pdf_url).name
    ).exists()

    assert all(
        (
            settings.panels_dir /
            Path(panel.image_url).name
        ).exists()
        for panel in panels
    )