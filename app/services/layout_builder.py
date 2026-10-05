from app.schemas import ComicPanel, ComicStory


def build_comic_layout(
    story: ComicStory,
    image_urls: list[str]
) -> list[ComicPanel]:

    if len(story.panels) != len(image_urls):
        raise ValueError(
            "The number of generated images "
            "does not match the story panels."
        )

    panels = []

    for index, panel in enumerate(
        story.panels
    ):

        panels.append(
            ComicPanel(
                panel_number=panel.panel_number,
                title=panel.title,
                image_url=image_urls[index],
                scene_description=(
                    panel.scene_description
                ),
                caption=panel.caption,
                narration=panel.narration,
                dialogue=panel.dialogue,
                image_prompt=panel.image_prompt,
            )
        )

    return panels