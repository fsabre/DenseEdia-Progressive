"""Define types for static typing."""

import types
from datetime import datetime
from typing import NamedTuple, Optional as Opt, Union

from .exceptions import UnsupportedTypeException

SupportedValue = Opt[Union[bool, int, float, str, datetime]]

_value_type_choices = {
    0: ("NONE", type(None)),
    1: ("BOOL", bool),
    2: ("INT", int),
    3: ("FLOAT", float),
    4: ("STR", str),
    5: ("DATETIME", datetime),
}


def _get_value_type_index_of(value: SupportedValue) -> int:
    for (index, (name, original_type)) in _value_type_choices.items():
        if isinstance(value, original_type):
            return index
    raise UnsupportedTypeException(value)


def _get_value_type_name_from_index(index: int) -> str:
    return _value_type_choices[index][0]


ValueType = types.SimpleNamespace()
# Allow access like ValueType.INT
for (_index, (_name, _original_type)) in _value_type_choices.items():
    setattr(ValueType, _name, _index)
ValueType.name = _get_value_type_name_from_index
ValueType.of = _get_value_type_index_of


class ElementSummary(NamedTuple):
    name: str
    type: int
    value: SupportedValue


class Direction:
    TO = 1
    FROM = 2
    NONE = 3
