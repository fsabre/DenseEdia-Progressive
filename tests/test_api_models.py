import pytest
from pydantic import ValidationError

from denseedia.models import CreateEdiumModel, ModifyEdiumModel


def test_CreateEdiumModel():
    # Valid data
    model = CreateEdiumModel(title="Title", kind="Kind")
    assert model.title == "Title"
    assert model.kind == "Kind"

    # Valid data with empty kind
    model = CreateEdiumModel(title="Title", kind="")
    assert model.title == "Title"
    assert model.kind == ""

    # Valid data with missing kind
    model = CreateEdiumModel(title="Title")
    assert model.title == "Title"
    assert model.kind == ""

    # Invalid data with empty title
    with pytest.raises(ValidationError):
        CreateEdiumModel(title="", kind="Kind")
    # Invalid data with missing title
    with pytest.raises(ValidationError):
        CreateEdiumModel(kind="Kind")
    # Invalid data with None title
    with pytest.raises(ValidationError):
        CreateEdiumModel(title=None, kind="Kind")
    # Invalid data with None kind
    with pytest.raises(ValidationError):
        CreateEdiumModel(title="Title", kind=None)


def test_ModifyEdiumModel():
    # Valid data with both values filled
    model = ModifyEdiumModel(title="Title", kind="Kind")
    assert model.dict(exclude_unset=True) == {"title": "Title", "kind": "Kind"}

    # Valid data with missing both
    model = ModifyEdiumModel()
    assert model.dict(exclude_unset=True) == {}

    # Invalid data with empty title
    with pytest.raises(ValidationError):
        ModifyEdiumModel(title="")

    # Invalid data with None title
    with pytest.raises(ValidationError):
        ModifyEdiumModel(title=None)

    # Valid data with empty kind
    model = ModifyEdiumModel(kind="")
    assert model.dict(exclude_unset=True) == {"kind": ""}

    # Invalid data with None kind
    with pytest.raises(ValidationError):
        ModifyEdiumModel(kind=None)
