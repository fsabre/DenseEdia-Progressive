"""Define the models."""

import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, Json


class VersionModel(BaseModel):
    id: int
    element_id: int
    creation_date: datetime
    last: bool
    value_type: int
    value_json: str


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


class ValueType(enum.Enum):
    NONE = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    STR = 4
    DATETIME = 5


class CreateElementModel(BaseModel):
    name: str = Field(min_length=1)
    value_type: ValueType
    value_json: Json
