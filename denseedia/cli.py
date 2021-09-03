"""Define the command line interface."""

import datetime
import functools
import logging
from pathlib import Path
from typing import Optional as Opt, Sequence as Seq

import click

from . import exceptions, helpers, operations, tables
from .constants import DEFAULT_FILE_NAME
from .customtypes import SupportedValue, ValueType
from .logger import logger


def translate_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.ObjectNotFound as exc:
            raise click.UsageError(exc.args[0])
        except exceptions.ValueTypeChange as exc:
            msg = (
                f"{exc.args[0]}. You may want to specify the type of the value "
                "with --type, or use the --allow-type-change flag."
            )
            raise click.UsageError(msg)

    return wrapper


def edium_as_string(edium: tables.Edium) -> str:
    return f"Edium n°{edium.id}: {edium.title} ({edium.kind})"


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


@main_group.command(name="add-edium", help="Create a new Edium")
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


@main_group.command(name="add-link", help="Create a link between two Edia")
@click.argument("edium1_id", type=int)
@click.argument("edium2_id", type=int)
@click.option("-l", "--label", help="Label of the link")
def add_link(edium1_id: int, edium2_id: int, label: str):
    operations.create_link(edium1_id, edium2_id, label)


@main_group.command(name="list", help="List all Edia")
def list_edia() -> None:
    # Fetch all Edia
    edia = operations.get_all_edia()
    # Print them
    for edium in edia:
        click.echo(edium_as_string(edium))


@main_group.command(name="search", help="Search for Edia")
@click.option("-t", "--title", "in_title", help="Part of the title of the Edia")
@click.option("-k", "--kind", help="Kind of the Edia")
def search_edia(in_title: Opt[str], kind: Opt[str]) -> None:
    if in_title is None and kind is None:
        raise click.UsageError("Please provide an option")
    edia = operations.search_edia(in_title, kind)
    for edium in edia:
        click.echo(edium_as_string(edium))


@main_group.group("edium", help="Operations on an Edium")
@click.argument("edium_id", type=int)
@click.pass_context
def edium_group(context: click.Context, edium_id: int):
    context.ensure_object(dict)
    context.obj["edium_id"] = edium_id


@edium_group.command(name="show", help="Display an Edium")
@click.pass_context
@translate_exceptions
def edium_show(context: click.Context) -> None:
    edium_id = context.obj["edium_id"]
    # Fetch the Edium and a summary of its elements
    edium, element_summaries, links = operations.get_one_edium_details(edium_id)
    # Print all the infos
    click.echo(edium_as_string(edium))
    click.echo("=" * 10)
    for element in element_summaries:
        value_type_name = ValueType.name(element.type)
        click.echo(
            f"{element.name:<10} = {element.value} ({value_type_name})"
        )
    click.echo("=" * 10)
    for link in links:
        if link.end is edium:
            direction_str = "<=="
            other_edium_str = edium_as_string(link.start)
        else:
            direction_str = "==>"
            other_edium_str = edium_as_string(link.end)
        if not link.directed:
            direction_str = "<=>"
        click.echo(
            f"Link n°{link.id} ({link.label}) : {direction_str} {other_edium_str}"
        )


@edium_group.command(name="set", help="Change an element value")
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
@click.pass_context
@translate_exceptions
def edium_set(
    context: click.Context,
    element_name: str,
    new_value: str,
    value_type: str,
    allow_type_change: bool
) -> None:
    edium_id = context.obj["edium_id"]
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
    # Set the element value, after creating it if needed
    operations.set_element_value(
        edium_id,
        element_name,
        value,
        allow_type_change
    )


@edium_group.command(name="edit", help="Edit an Edium")
@click.option("-t", "--title", help="New title for the edium")
@click.option("-k", "--kind", help="New kind for the edium")
@click.pass_context
@translate_exceptions
def edium_edit(
    context: click.Context,
    title: Opt[str],
    kind: Opt[str],
) -> None:
    edium_id: int = context.obj["edium_id"]
    operations.edit_edium(edium_id, title, kind)


@edium_group.command(name="delete", help="Delete an Edium")
@click.confirmation_option(prompt="Remove the Edium and all its history ?")
@click.pass_context
@translate_exceptions
def edium_delete(context: click.Context) -> None:
    edium_id: int = context.obj["edium_id"]
    operations.delete_edium(edium_id)


@edium_group.command(name="history", help="Show the history of an element")
@click.argument("element_name")
@click.pass_context
@translate_exceptions
def edium_history(context: click.Context, element_name: str) -> None:
    edium_id: int = context.obj["edium_id"]
    # Fetch the data
    element, versions = operations.get_element_versions(edium_id, element_name)
    # Print it
    click.echo(f"Element n°{element.id} : {element.name}")
    click.echo("=" * 10)
    for version in versions:
        date = version.creation_date
        value_type_name = ValueType.name(version.value_type)
        click.echo(f"{date} : {version.json} ({value_type_name})")


@main_group.group("link", help="Operations on a link")
@click.argument("link_id", type=int)
@click.pass_context
def link_group(context: click.Context, link_id: int):
    context.ensure_object(dict)
    context.obj["link_id"] = link_id


@link_group.command(name="show", help="Display a link")
@click.pass_context
@translate_exceptions
def link_show(context: click.Context) -> None:
    link_id = context.obj["link_id"]
    # Fetch the link
    link = operations.get_one_link_details(link_id)
    # Print all the infos
    click.echo(f"Link n°{link.id} ({link.label})")
    click.echo("=" * 10)
    click.echo(edium_as_string(link.start))
    click.echo("==>" if link.directed else "<=>")
    click.echo(edium_as_string(link.end))


@link_group.command(name="edit", help="Edit a link")
@click.option("-l", "--label", help="New label for the link")
@click.pass_context
@translate_exceptions
def link_edit(
    context: click.Context,
    label: Opt[str],
) -> None:
    link_id: int = context.obj["link_id"]
    operations.edit_link(link_id, label)


@link_group.command(name="delete", help="Delete a link")
@click.pass_context
@translate_exceptions
def link_delete(context: click.Context) -> None:
    link_id: int = context.obj["link_id"]
    operations.delete_link(link_id)
