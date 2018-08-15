"""instablog."""

import logging
import os
import re
from collections import defaultdict
from typing import DefaultDict, Dict, List, Tuple  # noqa

import maya
import pkg_resources
from instalooter.looters import ProfileLooter
from jinja2 import Template

ImageStore = DefaultDict[str, List[Tuple[str, str]]]


def download(username: str, image_dir: str) -> None:
    """Downloading images from instagram."""
    logging.info("Downloading...")
    looter = ProfileLooter(username, template="insta-{datetime}-{id}")
    looter.download(image_dir)
    logging.info("Done downloading.")


def parse_datetime(datetime_str: str) -> Dict[str, str]:
    """Eats a string of datetime and returns a parsed dict."""
    datetime_dict = {}  # type: Dict[str, str]
    parsed = maya.parse(datetime_str).datetime()
    datetime_dict["date"] = parsed.strftime("%Y-%m-%d")
    datetime_dict["time"] = parsed.strftime("%H:%M")

    return datetime_dict


def parse_images(image_dir: str) -> ImageStore:
    """Parse images in directory."""
    image_store = defaultdict(list)  # type: ImageStore
    re_image_date = (
        r"insta-"
        r"(?P<datetime>\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}h\d{1,2}m\d{1,2}s0)"
        r"-(?P<id>\d+).jpg"
    )

    logging.info("Parsing images...")
    for image_file in os.listdir(image_dir):
        logging.info("parsing: %s", image_file)
        matched_image = re.search(re_image_date, image_file)
        if matched_image:
            logging.debug("matched: %s", matched_image.groups())
            datetime_dict = parse_datetime(matched_image.group("datetime"))
            image_store[datetime_dict["date"]].append(
                (image_file, datetime_dict["time"])
            )
        else:
            logging.debug("did not matched: %s", image_file)
    logging.info("Done parsing.")

    return image_store


def create_markdown(markdown_dir: str, data: ImageStore) -> None:
    """Create markdown files."""
    with open(
        pkg_resources.resource_filename(__name__, "data/blogentry.md.j2"), "r"
    ) as blogentry_template:
        entry_template = blogentry_template.read()
        for date, images in data.items():
            logging.info("Writing blogfile for %s...", date)
            logging.debug("date: %s", date)
            logging.debug("images: %s", images)
            # find oldest time to use as publish time in the blog entry
            last_time = max([i[1] for i in images])
            Template(entry_template).stream(
                date=date, images=[i[0] for i in images], last_time=last_time
            ).dump(f"{markdown_dir}/{date}-in-bildern.md")
