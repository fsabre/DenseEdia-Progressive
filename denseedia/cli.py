from typing import Optional as Opt

import click

from . import storage


@click.group()
def main_group():
    pass


@main_group.command(name="add", help="Create a new Edium")
@click.argument("title")
@click.option("-k", "--kind", help="Optional kind for the edium")
def add_edium(title: str, kind: Opt[str]) -> None:
    storage.add_edium(title, kind)
