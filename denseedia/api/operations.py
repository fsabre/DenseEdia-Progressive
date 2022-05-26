from collections import Counter
from typing import Dict, List, Optional, Tuple

from .. import exceptions, models
from ..storage.tables import Edium, Element, Link, orm, Version


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


def modify_one_edium(edium_id: int, data: models.ModifyEdiumModel) -> models.EdiumModel:
    """Modify an edium and return its model."""
    with orm.db_session:
        edium = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("edium", edium_id)
        for (key, val) in data.dict(exclude_unset=True).items():
            setattr(edium, key, val)
        orm.commit()
        content = edium.to_model()
    return content


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

        # Don't have to provide the versions, it's easy
        if mode == models.VersionsMode.NONE:
            return [element.to_model() for element in elements]

        content: Dict[int, models.ElementModel]
        content = {element.id: element.to_model() for element in elements}

        # Let's make a second request to retrieve the needed versions
        if mode == models.VersionsMode.SINGLE:
            versions = orm.left_join(
                v
                    for e in Element
                    for v in e.versions
                    if e.edium.id == edium_id if v.last is True
            )
        else:
            versions = orm.left_join(
                v
                    for e in Element
                    for v in e.versions
                    if e.edium.id == edium_id
            )

        # Insert those versions in the returned pydantic models
        for version in versions:
            content[version.element.id].versions.append(version.to_model())

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


def create_one_element(edium_id: int, data: models.CreateElementModel) -> models.ElementModel:
    """Create one element and its last version."""
    with orm.db_session:
        edium: Optional[Edium] = Edium.get(id=edium_id)
        if edium is None:
            raise exceptions.ObjectNotFound("edium", edium_id)
        if edium.get_element_by_name(data.name) is not None:
            raise exceptions.DuplicateElementName(data.name)

        element = Element(edium=edium, name=data.name)
        version = element.create_version2(data.version.value_type, data.version.value_json)
        orm.commit()
        content = element.to_model()
        content.versions = [version.to_model()]
    return content


def modify_one_element(element_id: int, data: models.ModifyElementModel) -> models.ElementModel:
    """Modify an element and return its model."""
    with orm.db_session:
        element = Element.get(id=element_id)
        if element is None:
            raise exceptions.ObjectNotFound("element", element_id)
        for (key, val) in data.dict(exclude_unset=True).items():
            setattr(element, key, val)
        orm.commit()
        content = element.to_model()
    return content


def delete_one_element(element_id: int) -> models.ElementModel:
    """Delete an element and return its model."""
    with orm.db_session:
        element = Element.get(id=element_id)
        if element is None:
            raise exceptions.ObjectNotFound("element", element_id)
        content = element.to_model()
        element.delete()
    return content


def create_one_version(element_id: int, data: models.CreateVersionModel) -> models.VersionModel:
    """Create a new version for an element."""
    with orm.db_session:
        element: Optional[Element] = Element.get(id=element_id)
        if element is None:
            raise exceptions.ObjectNotFound("element", element_id)

        version = element.create_version2(data.value_type, data.value_json)
        orm.commit()
        content = version.to_model()
    return content


def modify_one_version(version_id: int, data: models.CreateVersionModel) -> models.VersionModel:
    """Modify a version and return its model."""
    with orm.db_session:
        version: Optional[Version] = Version.get(id=version_id)
        if version is None:
            raise exceptions.ObjectNotFound("version", version_id)

        v_type: models.ValueType.asType = data.value_type
        v_json = data.value_json
        # Same trick that in Element.create_version2
        if v_type == models.ValueType.NONE:
            v_json = ""
        version.value_type = models.ValueType.to_id(v_type)
        version.json = v_json

        orm.commit()
        content = version.to_model()
    return content


def delete_one_version(version_id: int) -> models.VersionModel:
    """Delete a version and return its model."""
    with orm.db_session:
        version = Version.get(id=version_id)
        if version is None:
            raise exceptions.ObjectNotFound("version", version_id)
        content = version.to_model()
        version.delete()
    return content


def get_all_links() -> List[models.LinkModel]:
    """Return a list of all links as models."""
    with orm.db_session:
        links = Link.select()[:]
        return [link.to_model() for link in links]


def get_one_link(link_id: int) -> models.LinkModel:
    """Return a link as a model."""
    with orm.db_session:
        link = Link.get(id=link_id)
        if link is None:
            raise exceptions.ObjectNotFound("link", link_id)
        return link.to_model()


def get_links_of_one_edium(edium_id: int) -> List[models.LinkModel]:
    """Return the links in which an edium appears."""
    with orm.db_session:
        links: List[Link] = orm.select(
            link
                for link in Link
                if link.start.id == edium_id or link.end.id == edium_id
        )
        content = [link.to_model() for link in links]
    return content


def create_one_link(data: models.CreateLinkModel) -> models.LinkModel:
    """Create and return one link."""
    with orm.db_session:
        # Check that the edia exist
        edium1: Optional[Edium] = Edium.get(id=data.start)
        if edium1 is None:
            raise exceptions.ObjectNotFound("edium", data.start)
        edium2: Optional[Edium] = Edium.get(id=data.end)
        if edium2 is None:
            raise exceptions.ObjectNotFound("edium", data.end)
        # Create the link
        link = Link(
            start=edium1,
            end=edium2,
            directed=data.directed,
            label=data.label,
        )
        orm.commit()
        return link.to_model()


def modify_one_link(link_id: int, data: models.ModifyLinkModel) -> models.LinkModel:
    """Modify a link and return its model."""
    with orm.db_session:
        link = Link.get(id=link_id)
        if link is None:
            raise exceptions.ObjectNotFound("link", link_id)
        for (key, val) in data.dict(exclude_unset=True).items():
            setattr(link, key, val)
        orm.commit()
        content = link.to_model()
    return content


def delete_one_link(link_id: int) -> models.LinkModel:
    """Delete a link and return its model."""
    with orm.db_session:
        link = Link.get(id=link_id)
        if link is None:
            raise exceptions.ObjectNotFound("link", link_id)
        content = link.to_model()
        link.delete()
    return content


def most_used_elements(kind: str, max_count: int) -> List[Tuple[str, int]]:
    """Return the most used element names for an edium kind.
    The return format is a tuple (element_name, count).
    """
    # I tried to make it purely SQL, but I can't do it with Pony.
    with orm.db_session:
        query = orm.select(e.elements.name for e in Edium if e.kind == kind).without_distinct()
        counter: Counter = Counter(query)
    return counter.most_common(max_count)
