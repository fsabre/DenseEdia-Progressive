from typing import List

from .. import exceptions, models
from ..storage.tables import Edium, orm


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
