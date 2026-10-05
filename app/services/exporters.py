from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF

from app.config import Settings
from app.schemas import ComicPanel


class ComicPDF(FPDF):

    def footer(self):

        self.set_y(-12)

        self.set_font(
            "Helvetica",
            size=8
        )

        self.cell(
            0,
            8,
            f"ComicCraft - Page {self.page_no()}",
            align="C"
        )


def _pdf_text(value: str) -> str:
    """
    Keep generated text compatible with
    FPDF core Helvetica fonts.
    """

    return (
        value
        .encode(
            "latin-1",
            "replace"
        )
        .decode("latin-1")
    )


def _asset_path(
    settings: Settings,
    image_url: str
) -> Path:

    parsed = urlparse(image_url)

    relative = parsed.path.removeprefix(
        "/static/"
    )

    path = (
        settings.static_dir /
        relative
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Generated image not found: {path}"
        )

    return path


def save_pdf(
    panels: list[ComicPanel],
    settings: Settings
) -> str:

    if not panels:
        raise ValueError(
            "Cannot export an empty comic."
        )

    filename = (
        "comic-"
        + datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d-%H%M%S-%f"
        )
        + ".pdf"
    )

    output = (
        settings.exports_dir /
        filename
    )

    pdf = ComicPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=14
    )

    for panel in panels:

        pdf.add_page()

        # Title
        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            0,
            10,
            _pdf_text(
                f"Panel {panel.panel_number}: "
                f"{panel.title}"
            )
        )

        pdf.ln(2)

        # Image
        image_path = _asset_path(
            settings,
            panel.image_url
        )

        pdf.image(
            str(image_path),
            x=15,
            y=42,
            w=180,
            h=120
        )

        pdf.set_y(168)

        sections = [
            (
                "Scene",
                panel.scene_description
            ),
            (
                "Caption",
                panel.caption
            ),
            (
                "Narration",
                panel.narration
            ),
            (
                "Dialogue",
                panel.dialogue
            ),
        ]

        for label, value in sections:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.cell(
                0,
                7,
                _pdf_text(label)
            )

            pdf.ln(6)

            pdf.set_font(
                "Helvetica",
                size=10
            )

            pdf.multi_cell(
                0,
                6,
                _pdf_text(value)
            )

            pdf.ln(1)

    pdf.output(
        str(output)
    )

    return (
        f"/static/exports/{filename}"
    )