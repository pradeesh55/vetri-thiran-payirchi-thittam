from app.config import Settings
from app.schemas import (
    ComicPanel,
    PromptRequest,
)

from app.services.exporters import save_pdf
from app.services.gemini_flash import (
    GeminiFlashService,
)
from app.services.gemini_pro import (
    GeminiProService,
)
from app.services.image_generator import (
    ImageGenerator,
)
from app.services.layout_builder import (
    build_comic_layout,
)


class ComicService:

    def __init__(
        self,
        settings: Settings
    ):
        self.settings = settings

        self.flash = GeminiFlashService(
            settings
        )

        self.pro = GeminiProService(
            settings
        )

        self.images = ImageGenerator(
            settings
        )

    def generate(
        self,
        request: PromptRequest
    ) -> tuple[list[ComicPanel], str]:

        # Step 1
        outline = (
            self.flash.generate_outline(
                request
            )
        )

        # Step 2
        story = (
            self.pro.generate_story(
                request,
                outline
            )
        )

        # Step 3
        image_urls = []

        for panel in story.panels:

            image_url = (
                self.images.generate_image(
                    panel.image_prompt,
                    panel.panel_number
                )
            )

            image_urls.append(image_url)

        # Step 4
        panels = build_comic_layout(
            story,
            image_urls
        )

        # Step 5
        pdf_url = save_pdf(
            panels,
            self.settings
        )

        return panels, pdf_url

    def generate_test_image(
        self,
        prompt: str
    ) -> str:

        return self.images.generate_image(
            prompt,
            999
        )