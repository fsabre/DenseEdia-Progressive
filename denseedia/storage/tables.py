"""Define ORM classes."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional as Opt

from pony import orm

from .. import helpers, models
from ..customtypes import ElementSummary, SupportedValue, ValueType
from ..logger import logger

database = orm.Database()


def value_to_json(value_type: ValueType, value: SupportedValue):
    if value_type == ValueType.DATETIME:
        return value.isoformat()
    else:
        return value


def json_to_value(value_type: ValueType, json) -> SupportedValue:
    if value_type == ValueType.DATETIME:
        return datetime.fromisoformat(json)
    else:
        return json


class Edium(database.Entity):
    """The main piece of information stored in DenseEdia."""
    title = orm.Required(str)
    kind = orm.Optional(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    elements = orm.Set("Element")
    links_out = orm.Set("Link", reverse="start")
    links_in = orm.Set("Link", reverse="end")

    def to_model(self) -> models.EdiumModel:
        """Return an EdiumModel made with the edium data."""
        return models.EdiumModel(
            id=self.id,
            title=self.title,
            kind=self.kind,
            creation_date=self.creation_date,
        )

    def get_element_by_name(self, element_name: str) -> Opt["Element"]:
        """Get an element by its name."""
        query = self.elements.filter(lambda el: el.name == element_name)
        return query.get()

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
            value=version.get_value(),
        )

    def get_all_element_summaries(self) -> List[ElementSummary]:
        """Create the summary of all the elements."""
        # Fetch the last version of each of the elements
        query = orm.select(
            (
                (element.name, version)
                for element in self.elements
                for version in element.versions
                if version.last is True
            )
        )
        # Create a summary for each element from the query
        return [
            ElementSummary(
                name=name,
                type=version.value_type,
                value=version.get_value(),
            )
            for (name, version) in query
        ]


class Element(database.Entity):
    """A property of an Edium that can have different value types."""
    edium = orm.Required("Edium")
    name = orm.Required(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    todo = orm.Required(bool, default=False)
    versions = orm.Set("Version")

    def to_model(self) -> models.ElementModel:
        """Return an ElementModel made with the element data."""
        return models.ElementModel(
            id=self.id,
            edium_id=self.edium.id,
            name=self.name,
            creation_date=self.creation_date,
            todo=self.todo,
            versions=[self.last_version.to_model()],
        )

    def create_version(self, value: SupportedValue) -> "Version":
        """Create a new version with the new value."""
        # Mark all the others versions as "not used"
        query = self.versions.select(lambda ver: ver.last is True).for_update()
        for version in query:
            version.last = False
        # Add the new version
        new_value_type = ValueType.of(value)
        return self.versions.create(
            value_type=new_value_type,
            json=value_to_json(new_value_type, value),
        )

    @property
    def last_version(self) -> "Version":
        return self.versions.select(lambda ver: ver.last is True).get()


class Version(database.Entity):
    """A record of an element value at a given time."""
    element = orm.Required("Element")
    value_type = orm.Required(int)
    json = orm.Required(orm.Json)
    last = orm.Required(bool, default=True)
    creation_date = orm.Required(datetime, default=helpers.now)

    def to_model(self) -> models.VersionModel:
        """Return an VersionModel made with the version data."""
        return models.VersionModel(
            id=self.id,
            element_id=self.element.id,
            creation_date=self.creation_date,
            last=self.last,
            value_type=self.value_type,
            value_json=self.get_value(),
        )

    def get_value(self) -> SupportedValue:
        return json_to_value(self.value_type, self.json)


class Link(database.Entity):
    """A link between two Edia."""
    start = orm.Required(Edium)
    end = orm.Required(Edium)
    directed = orm.Required(bool)
    label = orm.Optional(str)


def use_database(file_path: Path, debug: bool = False) -> None:
    logger.info("Use the database at %s", file_path)
    database.bind(provider="sqlite", filename=str(file_path), create_db=True)
    database.generate_mapping(create_tables=True)
    orm.set_sql_debug(debug)
