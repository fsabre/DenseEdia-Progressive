"""Define functions that link the ORM classes and the frontend (CLI or API)."""

from typing import List, Optional as Opt, Tuple

from . import exceptions
from .customtypes import Direction, ElementSummary, SupportedValue, ValueType
from .logger import logger
from .tables import Edium, Link, orm


def _compare_element_types(
    edium: Edium,
    element_name: str,
    new_value: SupportedValue
) -> None:
    """Raises an ValueTypeChange exception if the types are different."""
    el_summary = edium.get_one_element_summary(element_name)
    if el_summary is not None:
        # Let's compare the types and raise an exception if they differ.
        logger.info("Comparing the old and new value types")
        old_type = el_summary.type
        old_type_name = ValueType.name(old_type)
        new_type = ValueType.of(new_value)
        new_type_name = ValueType.name(new_type)
        logger.debug("Old = %s, new = %s", old_type_name, new_type_name)
        if old_type != new_type:
            raise exceptions.ValueTypeChange(old_type_name, new_type_name)


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
            edium.create_element("url", url)
        if comment is not None:
            edium.create_element("comment", comment)


def list_edia() -> List[Edium]:
    """Return a list of all the Edia."""
    with orm.db_session:
        return Edium.select()[:]


def show_edium(edium_id: int) -> Tuple[Edium, List[ElementSummary]]:
    """Returns an edium and a summary of its elements."""
    try:
        with orm.db_session:
            edium: Edium = Edium[edium_id]
            return edium, edium.get_all_element_summaries()
    except orm.ObjectNotFound:
        raise exceptions.ObjectNotFound()


def set_element_value(
    edium_id: int,
    element_name: str,
    element_value: SupportedValue,
    allow_type_change: bool = False
) -> None:
    """Change an element value from a Edium."""
    try:
        with orm.db_session:
            edium: Edium = Edium[edium_id]
            if not allow_type_change:
                # Raises an exception if the user try to change the type of the
                # value
                _compare_element_types(
                    edium,
                    element_name,
                    element_value
                )
            edium.set_element_value(element_name, element_value)
    except orm.ObjectNotFound:
        raise exceptions.ObjectNotFound()


def link_edia(edium1_id: int, edium2_id: int, label: str) -> None:
    """Link two Edia together."""
    try:
        with orm.db_session:
            edium1: Edium = Edium[edium1_id]
            edium2: Edium = Edium[edium2_id]
            Link(
                edium1=edium1,
                edium2=edium2,
                label=label,
                direction=Direction.TO
            )
    except orm.ObjectNotFound:
        raise exceptions.ObjectNotFound()
