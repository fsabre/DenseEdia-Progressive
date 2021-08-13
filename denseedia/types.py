from typing import Any, Dict, Optional as Opt

from typing_extensions import TypedDict


class EdiumType(TypedDict):
    id: int
    title: str
    kind: Opt[str]
    date: str
    extras: Dict[str, Any]
