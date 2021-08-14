import logging
from pathlib import Path
from typing import Optional as Opt, Sequence as Seq

import click
from youtube_dl import DownloadError, YoutubeDL

from . import exceptions, operations, tables
from .constants import DEFAULT_FILE_NAME
from .logger import logger


def get_title_from_url(url: str) -> Opt[str]:
    """Return a fitting title for the URL. None if not found."""
    try:
        opts = {"quiet": True, "simulate": True}
        with YoutubeDL(opts) as ydl:
            video_info = ydl.extract_info(url)
            return video_info.get("title", None)
    except DownloadError:
        return None


@click.group()
@click.option("-f", "--file", type=click.Path(), help="Target file")
@click.option("-v", "--verbose", count=True, help="Increase the verbosity")
def main_group(file: Opt[str], verbose: int) -> None:
    # Set the logger verbosity
    if verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(logging.INFO)
    # Use the proper file
    file_name: str = file or DEFAULT_FILE_NAME
    file_path = Path().joinpath(file_name).absolute().resolve()
    tables.use_database(file_path)


@main_group.command(name="add", help="Create a new Edium")
@click.argument("title", nargs=-1)
@click.option("-k", "--kind", help="Optional kind for the Edium")
@click.option("-u", "--url", help="Optional URL for the Edium")
@click.option("-c", "--comment", help="Optional comment for the Edium")
def add_edium(
    title: Seq[str],
    kind: Opt[str],
    url: Opt[str],
    comment: Opt[str]
) -> None:
    # Infer title from options
    new_title: Opt[str] = None
    if len(title) > 0:
        new_title = " ".join(title)
    elif url is not None:
        click.echo("Extract title from the URL")
        new_title = get_title_from_url(url)
        click.echo(f"Title : {new_title}")
    if new_title is None:
        raise click.UsageError("Couldn't infer title from options")

    # Create and save the Edium
    operations.create_edium(new_title, kind, url, comment)


@main_group.command(name="show", help="Display an Edium")
@click.argument("edium_id", type=int)
def show_edium(edium_id: int) -> None:
    # Fetch the Edium and a summary of its elements
    try:
        edium, element_summaries = operations.show_edium(edium_id)
    except exceptions.ObjectNotFound:
        raise click.UsageError(f"No Edium found with ID {edium_id}")
    # Print all the infos
    click.echo(f"Edium n°{edium.id}: {edium.title} ({edium.kind})")
    click.echo("=" * 10)
    for element in element_summaries:
        click.echo(
            f"{element.name:<10} = {element.value} ({element.type.name})"
        )
