"""Define the models."""

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator


class VersionModel(BaseModel):
    id: int
    element_id: int
    creation_date: datetime
    last: bool
    value_type: str
    value_json: Any


class ElementModel(BaseModel):
    id: int
    edium_id: int
    name: str
    creation_date: datetime
    todo: bool
    versions: List[VersionModel]


class EdiumModel(BaseModel):
    id: int
    title: str
    kind: Optional[str]
    creation_date: datetime


class CreateEdiumModel(BaseModel):
    title: str = Field(min_length=1)
    kind: str = Field("")


class VersionsMode:
    NONE = "none"
    SINGLE = "single"
    ALL = "all"
    asType = Literal["none", "single", "all"]


class ValueType:
    NONE = "none"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STR = "str"
    DATETIME = "datetime"
    all_types = [NONE, BOOL, INT, FLOAT, STR, DATETIME]
    asType = Literal["none", "bool", "int", "float", "str", "datetime"]

    @classmethod
    def to_id(cls, alias: str) -> int:
        return cls.all_types.index(alias)

    @classmethod
    def to_alias(cls, index: int) -> str:
        return cls.all_types[index]


class CreateVersionModel(BaseModel):
    value_type: ValueType.asType
    value_json: Any

    @root_validator(skip_on_failure=True)
    def type_and_value_must_match(cls, values):
        v_type, v_json = values.get('value_type'), values.get('value_json')
        if v_type == ValueType.NONE:
            if v_json is not None:
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            return values

        if v_type == ValueType.BOOL:
            if not isinstance(v_json, bool):
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            return values

        if v_type == ValueType.INT:
            if not isinstance(v_json, int):
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            return values

        if v_type == ValueType.FLOAT:
            if not isinstance(v_json, int) and not isinstance(v_json, float):
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            return values

        if v_type == ValueType.STR:
            if not isinstance(v_json, str):
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            return values

        if v_type == ValueType.DATETIME:
            if isinstance(v_json, str):
                try:
                    datetime.fromisoformat(v_json)
                    return values
                except ValueError:
                    raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")
            else:
                raise ValueError(f"Type '{v_type}' and value {v_json!r} are not compatible")

        raise TypeError(f"Unknown type : '{v_type}'")


class CreateElementModel(BaseModel):
    name: str = Field(min_length=1)
    version: CreateVersionModel
