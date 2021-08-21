"""Define ORM classes."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional as Opt

from pony import orm

from . import helpers
from .logger import logger
from .types import ElementSummary, SupportedValue, ValueType

database = orm.Database()


class Edium(database.Entity):
    """The main piece of information stored in DenseEdia."""
    title = orm.Required(str)
    kind = orm.Optional(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    elements = orm.Set("Element")
    links1 = orm.Set("Link", reverse="edium1")
    links2 = orm.Set("Link", reverse="edium2")

    def get_element_by_name(self, element_name: str) -> Opt["Element"]:
        """Get an element by its name."""
        return (
            self.elements
                .filter(lambda el: el.name == element_name)
                .get()
        )

    def set_element_value(
        self,
        element_name: str,
        new_value: SupportedValue,
    ) -> None:
        """Create the element if needed, then create its version."""
        # Fetch the element with the right name
        element = self.get_element_by_name(element_name)
        if element is None:
            # Create a new element if it didn't exist
            logger.debug("The element %s doesn't exist yet", element_name)
            self.create_element(element_name, new_value)
        else:
            # Create a new version if the element already exists
            logger.debug("The element %s exists (%s)", element_name, element.id)
            element.create_version(new_value)

    def create_element(self, name: str, value: SupportedValue) -> "Element":
        """Create a new element and its version with the given value."""
        element = self.elements.create(name=name)
        element.create_version(value)
        return element

    def get_one_element_summary(self, element_name: str) -> Opt[ElementSummary]:
        """Create the summary of one element, found by name."""
        element = self.get_element_by_name(element_name)
        if element is None:
            return None
        version = element.last_version
        return ElementSummary(
            name=element.name,
            type=version.value_type,
            value=version.json
        )

    def get_all_element_summaries(self) -> List[ElementSummary]:
        """Create the summary of all the elements."""
        # Fetch the last version of each of the elements
        query = orm.select(
            (
                (element.name, version.type_idx, version.json)
                for element in self.elements
                for version in element.versions
                if version.last is True
            )
        )
        # Create a summary for each element from the query
        return [
            ElementSummary(
                name=name,
                type=ValueType(type_idx),
                value=value
            )
            for (name, type_idx, value) in query
        ]


class Element(database.Entity):
    """A property of an Edium that can have different value types."""
    edium = orm.Required("Edium")
    name = orm.Required(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    todo = orm.Required(bool, default=False)
    versions = orm.Set("Version")

    def create_version(self, value: SupportedValue) -> "Version":
        """Create a new version with the new value."""
        # Mark all the others versions as "not used"
        query = self.versions.select(lambda ver: ver.last is True).for_update()
        for version in query:
            version.last = False
        # Add the new version
        return self.versions.create(
            type_idx=ValueType.infer_from_value(value).index,
            json=value
        )

    @property
    def last_version(self) -> "Version":
        return self.versions.select(lambda ver: ver.last is True).get()


class Version(database.Entity):
    """A record of an element value at a given time."""
    element = orm.Required("Element")
    type_idx = orm.Required(int)
    json = orm.Required(orm.Json)
    last = orm.Required(bool, default=True)
    creation_date = orm.Required(datetime, default=helpers.now)

    @property
    def value_type(self) -> ValueType:
        return ValueType(self.type_idx)

    @value_type.setter
    def value_type(self, new_type: ValueType) -> None:
        self.type_idx = new_type.index


class Link(database.Entity):
    """A link between two Edia."""
    edium1 = orm.Required(Edium)
    edium2 = orm.Required(Edium)
    direction = orm.Required(int)
    label = orm.Optional(str)


def use_database(file_path: Path, debug: bool = False) -> None:
    logger.info("Use the database at %s", file_path)
    database.bind(provider="sqlite", filename=str(file_path), create_db=True)
    database.generate_mapping(create_tables=True)
    orm.set_sql_debug(debug)
