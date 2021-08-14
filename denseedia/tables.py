from datetime import datetime
from pathlib import Path

from pony import orm

from . import helpers
from .logger import logger
from .types import SupportedValue, ValueType

database = orm.Database()


class Edium(database.Entity):
    title = orm.Required(str)
    kind = orm.Optional(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    elements = orm.Set("Element")

    def add_element(self, name: str, value: SupportedValue) -> "Element":
        element = Element(edium=self, name=name)
        element.set_value(value)
        return element


class Element(database.Entity):
    edium = orm.Required("Edium")
    name = orm.Required(str)
    creation_date = orm.Required(datetime, default=helpers.now)
    todo = orm.Required(bool, default=False)
    versions = orm.Set("Version")

    def set_value(self, value: SupportedValue) -> "Version":
        # Mark all the others versions as "not used"
        query = self.versions.select().for_update()
        for version in query:
            version.last = False
        # Add the new version
        return self.versions.create(
            type_idx=ValueType.infer_from_value(value).index,
            json=value
        )


class Version(database.Entity):
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


def use_database(file_path: Path, debug: bool = False) -> None:
    orm.set_sql_debug(debug)
    logger.info("Use the database at %s", file_path)
    database.bind(provider="sqlite", filename=str(file_path), create_db=True)
    database.generate_mapping(create_tables=True)
