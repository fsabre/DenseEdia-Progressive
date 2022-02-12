from typing import Dict, List, Optional

from .. import exceptions, models
from ..storage.tables import Edium, Element, orm


def get_all_edia() -> List[models.EdiumModel]:
    """Return a list of all edia as simple models."""
    with orm.db_session:
        edia = Edium.select()[:]
        return [edium.to_model() for edium in edia]


def get_one_edium(edium_id: int) -> models.EdiumModel:
    """Return an edium as a model."""
    with orm.db_session:
        edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("edium", edium_id)
        return edium.to_model()


def create_one_edium(body: models.CreateEdiumModel) -> models.EdiumModel:
    """Create and return one edium."""
    with orm.db_session:
        edium = Edium(**body.dict())
        orm.commit()
        return edium.to_model()


def delete_one_edium(edium_id: int) -> models.EdiumModel:
    """Delete an edium and return its model."""
    with orm.db_session:
        edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("edium", edium_id)
        content = edium.to_model()
        edium.delete()
    return content


def get_elements_of_one_edium(edium_id: int, mode: models.VersionsMode.asType) -> List[models.ElementModel]:
    """Return the elements of an Edium.

    None, one or all of its versions are attached, according to the ``mode``.
    It works even if an element has no version.
    """
    with orm.db_session:
        # The first request is used to retrieve the elements
        elements = orm.select(e for e in Element if e.edium.id == edium_id)
        if not elements:
            return []
        content: Dict[int, models.ElementModel]
        content = {element.id: element.to_model() for element in elements}

        # Attach the last version of each element if needed by the mode
        if mode == models.VersionsMode.SINGLE:
            # A second request is used to retrieve the last version of those elements
            versions = orm.left_join(
                v
                    for e in Element
                    for v in e.versions
                    if e.edium.id == edium_id if v.last is True
            )
            for version in versions:
                content[version.element.id].versions = [version.to_model()]

    return list(content.values())


def get_one_element(element_id: int, mode: models.VersionsMode.asType) -> models.ElementModel:
    """Return one element.

    None, one or all of its versions are attached, according to the ``mode``.
    """
    with orm.db_session:
        element = Element.get(id=element_id)
        if element is None:
            raise exceptions.ObjectNotFound("element", element_id)
        content = element.to_model()

        if mode == models.VersionsMode.SINGLE:
            # Add the last version if it exists
            last_version = element.get_last_version()
            if last_version is not None:
                content.versions = [last_version.to_model()]
        elif mode == models.VersionsMode.ALL:
            # Add all its versions
            content.versions = [version.to_model() for version in element.versions]

    return content


def create_one_element(edium_id: int, body: models.CreateElementModel) -> models.ElementModel:
    with orm.db_session:
        edium: Optional[Edium] = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("edium", edium_id)
        if edium.get_element_by_name(body.name) is not None:
            raise exceptions.DuplicateElementName(body.name)

        element = Element(edium=edium, name=body.name)
        version = element.create_version2(body.value_type, body.value_json)
        orm.commit()
        content = element.to_model()
        content.versions = [version.to_model()]
    return content
