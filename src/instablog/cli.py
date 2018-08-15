"""Client interface."""

import logging

import click

from instablog import core


@click.command()
@click.option(
    "--image_dir",
    "-i",
    type=click.Path(exists=True, writable=True),
    help="Directory for image files",
    prompt=True,
)
@click.option(
    "--post_dir",
    "-p",
    type=click.Path(exists=True, writable=True),
    help="Directory for markdown files",
    prompt=True,
)
@click.option("--username", "-u", help="Instagram username", prompt=True)
@click.option("--verbose", "-v", count=True)
def main(image_dir: str, post_dir: str, username: str, verbose: int) -> None:
    """Creates Markdown blog files out of Instagram images."""
    if verbose >= 1:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    try:
        core.download(username, image_dir)
    except BaseException as exception_output:
        logging.exception("%s", str(exception_output))
    data = core.parse_images(image_dir)
    core.create_markdown(post_dir, data)
