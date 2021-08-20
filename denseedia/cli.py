"""Define the command line interface."""

import datetime
import logging
from pathlib import Path
from typing import Optional as Opt, Sequence as Seq

import click

from . import exceptions, helpers, operations, tables
from .constants import DEFAULT_FILE_NAME
from .logger import logger
from .types import SupportedValue


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
        new_title = helpers.get_url_title(url)
        click.echo(f"Title : {new_title}")
    if new_title is None:
        raise click.UsageError("Couldn't infer title from options")

    # Create and save the Edium
    operations.create_edium(new_title, kind, url, comment)


@main_group.command(name="list", help="List all Edia")
def list_edia() -> None:
    # Fetch all Edia
    edia = operations.list_edia()
    # Print them
    for edium in edia:
        click.echo(f"N°{edium.id}: {edium.title} ({edium.kind})")


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


@main_group.command(name="set", help="Change an element value")
@click.argument("edium_id", type=int)
@click.argument("element_name")
@click.argument("new_value")
@click.option(
    "-t",
    "--type",
    "value_type",
    type=click.Choice(
        ["NONE", "BOOL", "INT", "FLOAT", "STR", "DATETIME"],
        case_sensitive=False
    ),
    default="STR"
)
@click.option(
    "-y",
    "--allow-type-change",
    is_flag=True,
    help="Allow to specify a different value type as the previous one"
)
def set_element(
    edium_id: int,
    element_name: str,
    new_value: str,
    value_type: str,
    allow_type_change: bool
) -> None:
    value: SupportedValue
    if value_type != "STR":
        if value_type == "NONE":
            value = None
        elif value_type == "BOOL":
            value = new_value.lower() in ("1", "true")
        elif value_type == "INT":
            value = int(new_value)
        elif value_type == "FLOAT":
            value = float(new_value)
        elif value_type == "DATETIME":
            value = datetime.datetime.fromisoformat(new_value)
        else:
            raise click.UsageError("Unsupported format")
        logger.info("Value converted to %s : %r", value_type, value)
    else:
        value = new_value
    try:
        # Set the element value, after creating it if needed
        operations.set_element_value(
            edium_id,
            element_name,
            value,
            allow_type_change
        )
    except exceptions.ValueTypeChange as exc:
        msg = (
            f"{exc.args[0]}. You may want to use the --allow-type-change flag."
        )
        raise click.UsageError(msg)
    except exceptions.ObjectNotFound:
        raise click.UsageError(f"No Edium found with ID {edium_id}")
