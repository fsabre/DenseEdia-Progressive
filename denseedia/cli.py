from typing import Optional as Opt, Sequence as Seq

import click
from youtube_dl import DownloadError, YoutubeDL

from . import storage


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
def main_group():
    pass


@main_group.command(name="add", help="Create a new Edium")
@click.argument("title", nargs=-1)
@click.option("-k", "--kind", help="Optional kind for the Edium")
@click.option("-u", "--url", help="Optional URL for the Edium")
def add_edium(title: Seq[str], kind: Opt[str], url: Opt[str]) -> None:
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

    storage.add_edium(new_title, kind, url)
