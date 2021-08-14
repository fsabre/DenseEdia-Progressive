from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional as Opt, Union

from typing_extensions import TypedDict

from .exceptions import UnsupportedTypeException


class EdiumType(TypedDict):
    id: int
    title: str
    kind: Opt[str]
    date: str
    extras: Dict[str, Any]


SupportedValue = Opt[Union[bool, int, float, str, datetime]]


class ValueType(Enum):
    NONE = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    STR = 4
    DATETIME = 5

    @classmethod
    def infer_from_value(cls, value: SupportedValue) -> "ValueType":
        if value is None:
            return cls.NONE
        if isinstance(value, bool):
            return cls.BOOL
        if isinstance(value, int):
            return cls.INT
        if isinstance(value, float):
            return cls.FLOAT
        if isinstance(value, str):
            return cls.STR
        if isinstance(value, datetime):
            return cls.DATETIME
        raise UnsupportedTypeException(f"Not supported type : {type(value)}")

    @property
    def index(self):
        """Simple alias for value, as it might be confusing."""
        return self.value