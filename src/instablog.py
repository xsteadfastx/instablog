"""instablog."""

import logging
import os
import re
from collections import defaultdict
from typing import DefaultDict, Dict, List  # noqa

import click
from instalooter.looters import ProfileLooter
from jinja2 import Template

logging.basicConfig(level=logging.DEBUG)

IMAGE_DIR = "./images"
MARKDOWN_DIR = "./markdown"

ImageStore = Dict[str, List[str]]


def download() -> None:
    """Downloading images from instagram."""
    logging.info("Downloading...")
    looter = ProfileLooter("marvinxsteadfast", template="insta-{date}-{id}")
    looter.download(IMAGE_DIR)
    logging.info("Done downloading")


def parse_images() -> ImageStore:
    """Parse images in directory."""
    image_store = defaultdict(list)  # type: DefaultDict[str, List[str]]
    re_image_date = r"insta-(?P<date>\d\d\d\d-\d\d-\d\d)-(?P<id>\d+).jpg"

    for image_file in os.listdir(IMAGE_DIR):
        matched_image = re.search(re_image_date, image_file)
        if matched_image:
            image_store[matched_image.group("date")].append(image_file)

    return image_store


def create_markdown(data: ImageStore) -> None:
    """Create markdown files."""
    with open(
        os.path.join(os.path.dirname(__file__), "blogentry.md.j2"), "r"
    ) as blogentry_template:
        entry_template = blogentry_template.read()
        for date, images in data.items():
            logging.info("Writing blogfile for %s...", date)
            logging.debug("date: %s", date)
            logging.debug("images: %s", ", ".join(images))
            Template(entry_template).stream(date=date, images=images).dump(
                f"{MARKDOWN_DIR}/{date}-in-bildern.md"
            )


@click.command()
@click.argument("image_dir")
@click.argument("post_dir")
def cli(image_dir: str) -> None:
    """Creates Markdown blog files out of Instagram images."""
    pass
