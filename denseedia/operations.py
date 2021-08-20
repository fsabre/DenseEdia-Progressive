"""Define functions that link the ORM classes and the frontend (CLI or API)."""

from typing import List, Optional as Opt, Tuple

from . import exceptions
from .logger import logger
from .tables import Edium, orm
from .types import ElementSummary, SupportedValue, ValueType


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
            el_summary = edium.get_one_element_summary(element_name)
            if not allow_type_change and el_summary is not None:
                # Let's compare the types and raise an exception if they differ.
                logger.info("Comparing the old and new value types")
                old_type = el_summary.type
                new_type = ValueType.infer_from_value(element_value)
                logger.debug("Old = %s, new = %s", old_type.name, new_type.name)
                if old_type != new_type:
                    msg = (
                        "Changing type is not allowed "
                        f"({old_type.name} -> {new_type.name})"
                    )
                    raise exceptions.ValueTypeChange(msg)
            edium.set_element_value(element_name, element_value)
    except orm.ObjectNotFound:
        raise exceptions.ObjectNotFound()
