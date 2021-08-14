from typing import List, Optional as Opt, Tuple

from . import exceptions
from .tables import Edium, orm
from .types import ElementSummary, ValueType


def create_edium(
    title: str,
    kind: Opt[str],
    url: Opt[str],
    comment: Opt[str]
) -> None:
    """Create an Edium."""
    kind = "" if kind is None else kind

    with orm.db_session:
        edium = Edium(title=title, kind=kind)
        if url is not None:
            edium.add_element("url", url)
        if comment is not None:
            edium.add_element("comment", comment)


def list_edia() -> List[Edium]:
    """Return a list of all the Edia."""
    with orm.db_session:
        return Edium.select()[:]


def show_edium(edium_id: int) -> Tuple[Edium, List[ElementSummary]]:
    """Returns an edium and a summary of its elements."""
    try:
        with orm.db_session:
            edium = Edium[edium_id]
            # Fetch the last version of each of the Edium elements
            query = orm.select(
                (
                    (element.name, version.type_idx, version.json)
                    for element in edium.elements
                    for version in element.versions
                    if version.last is True
                )
            )
            # Create a summary for each element from the query
            elements = [
                ElementSummary(
                    name=name,
                    type=ValueType(value_type),
                    value=value
                )
                for (name, value_type, value) in query
            ]
            return edium, elements
    except orm.ObjectNotFound:
        raise exceptions.ObjectNotFound()
