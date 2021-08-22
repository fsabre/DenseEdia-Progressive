"""Define functions that link the ORM classes and the frontend (CLI or API)."""

from typing import List, Optional as Opt, Tuple

from . import exceptions
from .customtypes import ElementSummary, SupportedValue, ValueType
from .logger import logger
from .tables import Edium, Element, Link, orm, Version


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


def get_all_edia() -> List[Edium]:
    """Return a list of all the Edia."""
    with orm.db_session:
        return Edium.select()[:]


def get_one_edium_details(
    edium_id: int
) -> Tuple[Edium, List[ElementSummary], List[Link]]:
    """Returns an edium, its links and a summary of its elements."""
    with orm.db_session:
        edium: Edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("Edium", edium_id)
        links = Link.select(lambda l: edium in (l.start, l.end)).prefetch(Edium)
        return edium, edium.get_all_element_summaries(), list(links)


def set_element_value(
    edium_id: int,
    element_name: str,
    element_value: SupportedValue,
    allow_type_change: bool = False
) -> None:
    """Change an element value from a Edium."""
    with orm.db_session:
        edium: Edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("Edium", edium_id)
        if not allow_type_change:
            # Raises an exception if the user try to change the type of the
            # value
            _compare_element_types(
                edium,
                element_name,
                element_value
            )
        edium.set_element_value(element_name, element_value)


def edit_edium(edium_id: int, new_title: Opt[str], new_kind: Opt[str]) -> None:
    """Change the title or the kind of an Edium."""
    with orm.db_session:
        edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("Edium", edium_id)
        if new_title is not None:
            edium.title = new_title
        if new_kind is not None:
            edium.kind = new_kind


def delete_edium(edium_id: int) -> None:
    """Delete an Edium from the database."""
    with orm.db_session:
        edium: Edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("Edium", edium_id)
        edium.delete()


def get_element_versions(
    edium_id: int, element_name: str
) -> Tuple[Element, List[Version]]:
    """Retrieve all the versions of an element."""
    with orm.db_session:
        edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("Edium", edium_id)
        element = edium.get_element_by_name(element_name)
        if element is None:
            raise exceptions.ObjectNotFound("element", element_name)
        query = element.versions.order_by(lambda ver: ver.creation_date)
        return element, list(query)


def create_link(edium1_id: int, edium2_id: int, label: str) -> None:
    """Link two Edia together."""
    with orm.db_session:
        edium1: Edium = Edium[edium1_id]
        if edium1 is None:
            raise exceptions.ObjectNotFound("Edium", edium1_id)
        edium2: Edium = Edium[edium2_id]
        if edium2 is None:
            raise exceptions.ObjectNotFound("Edium", edium2_id)
        Link(
            start=edium1,
            end=edium2,
            label=label,
            directed=True
        )


def get_one_link_details(link_id: int) -> Link:
    """Return a link and its two Edia."""
    with orm.db_session:
        query = Link.select(lambda l: l.id is link_id).prefetch(Edium)
        link = query.get()
    if link is None:
        raise exceptions.ObjectNotFound("link", link_id)
    return link


def edit_link(link_id: int, new_label: Opt[str]) -> None:
    """Change the label of a link."""
    with orm.db_session:
        link = Link.get(id=link_id)
        if link is None:
            raise exceptions.ObjectNotFound("link", link_id)
        if new_label is not None:
            link.label = new_label


def delete_link(link_id: int) -> None:
    """Delete a link from the database."""
    with orm.db_session:
        link: Link = Link.get(id=link_id)
        if link is None:
            raise exceptions.ObjectNotFound("link", link_id)
        link.delete()
