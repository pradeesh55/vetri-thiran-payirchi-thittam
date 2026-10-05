import re
from pathlib import Path

from PIL import Image, ImageDraw

from app.config import Settings


class ImageGenerator:

    def __init__(
        self,
        settings: Settings
    ):
        self.settings = settings
        self._local_pipeline = None

    @staticmethod
    def _safe_name(text: str) -> str:
        value = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "-",
            text
        )

        value = value.strip("-").lower()

        return value[:60] or "panel"

    def generate_image(
        self,
        prompt: str,
        panel_number: int
    ) -> str:

        filename = (
            f"panel-{panel_number:02d}-"
            f"{self._safe_name(prompt)}.png"
        )

        output = (
            self.settings.panels_dir /
            filename
        )

        # -----------------------------------------
        # MOCK
        # -----------------------------------------

        if self.settings.mock_ai:
            self._create_mock_image(
                output,
                prompt,
                panel_number
            )

        # -----------------------------------------
        # LOCAL DIFFUSERS
        # -----------------------------------------

        elif (
            self.settings.image_backend.lower()
            == "local"
        ):
            self._generate_local(
                prompt,
                output
            )

        # -----------------------------------------
        # HUGGING FACE
        # -----------------------------------------

        else:
            self._generate_hf(
                prompt,
                output
            )

        return (
            f"/static/panels/{output.name}"
        )

    def _generate_hf(
        self,
        prompt: str,
        output: Path
    ) -> None:

        if not self.settings.hf_token:
            raise RuntimeError(
                "HF_TOKEN is not configured. "
                "Set it in .env, or use "
                "IMAGE_BACKEND=local."
            )

        from huggingface_hub import (
            InferenceClient
        )

        client = InferenceClient(
            api_key=self.settings.hf_token
        )

        image = client.text_to_image(
            prompt=prompt,
            model=self.settings.image_model,
            width=self.settings.image_width,
            height=self.settings.image_height,
        )

        image.save(output)

    def _generate_local(
        self,
        prompt: str,
        output: Path
    ) -> None:

        try:
            import torch

            from diffusers import (
                StableDiffusionPipeline
            )

        except ImportError as exc:
            raise RuntimeError(
                "Local image generation requires "
                "torch and diffusers. "
                "Install requirements-local.txt."
            ) from exc

        if self._local_pipeline is None:

            device = (
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

            dtype = (
                torch.float16
                if device == "cuda"
                else torch.float32
            )

            self._local_pipeline = (
                StableDiffusionPipeline
                .from_pretrained(
                    self.settings.local_image_model,
                    torch_dtype=dtype,
                )
                .to(device)
            )

        result = self._local_pipeline(
            prompt,
            width=self.settings.image_width,
            height=self.settings.image_height,
            num_inference_steps=25,
        )

        image = result.images[0]

        image.save(output)

    @staticmethod
    def _create_mock_image(
        output: Path,
        prompt: str,
        panel_number: int
    ) -> None:

        image = Image.new(
            "RGB",
            (768, 768),
            "#f4efe6"
        )

        draw = ImageDraw.Draw(image)

        # Border
        draw.rectangle(
            (18, 18, 750, 750),
            outline="#222",
            width=6
        )

        # Head
        draw.ellipse(
            (250, 150, 520, 420),
            outline="#222",
            width=7
        )

        # Body
        draw.line(
            (385, 420, 385, 620),
            fill="#222",
            width=7
        )

        # Left arm
        draw.line(
            (385, 470, 280, 540),
            fill="#222",
            width=7
        )

        # Right arm
        draw.line(
            (385, 470, 490, 540),
            fill="#222",
            width=7
        )

        # Left leg
        draw.line(
            (385, 620, 300, 690),
            fill="#222",
            width=7
        )

        # Right leg
        draw.line(
            (385, 620, 470, 690),
            fill="#222",
            width=7
        )

        draw.text(
            (45, 45),
            f"ComicCraft - Panel {panel_number}",
            fill="#222"
        )

        short_prompt = (
            prompt[:100]
            + ("..." if len(prompt) > 100 else "")
        )

        draw.text(
            (45, 705),
            short_prompt,
            fill="#222"
        )

        image.save(output)