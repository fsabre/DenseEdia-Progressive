import pytest
from pydantic import ValidationError

from denseedia.models import CreateEdiumModel


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
