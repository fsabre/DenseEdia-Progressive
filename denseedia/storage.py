import datetime
from typing import Any, cast, Dict, Optional as Opt

import yaml
from typing_extensions import TypedDict

from .config import DB_PATH


class EdiumType(TypedDict):
    id: int
    title: str
    kind: Opt[str]
    date: str
    extras: Dict[str, Any]


class StorageType(TypedDict):
    edia: Dict[int, EdiumType]


def read() -> StorageType:
    """Read the file."""
    processed: StorageType = {"edia": {}}
    try:
        with open(DB_PATH) as read_file:
            raw = yaml.full_load(read_file)
        for edium_id, raw_edium in raw["edia"].items():
            edium = cast(EdiumType, dict(**raw_edium, id=edium_id))
            processed["edia"][edium_id] = edium
        return processed
    except FileNotFoundError:
        return processed


def write() -> None:
    """Write the cached data to the file."""
    raw: Any = {"edia": {}}
    for edium_id, edium in cached["edia"].items():
        raw_edium = dict(**edium)
        raw_edium.pop("id")
        raw["edia"][edium_id] = raw_edium
    with open(DB_PATH, "w") as write_file:
        yaml.dump(raw, write_file)


def get_new_id() -> int:
    """Get an Edium ID not in use."""
    try:
        return max(cached["edia"].keys()) + 1
    except ValueError:
        return 1


def add_edium(title: str, kind: Opt[str], url: Opt[str]) -> None:
    """Create an Edium, cache it and write in file."""
    new_id = get_new_id()
    cached["edia"][new_id] = {
        "id": new_id,
        "title": title,
        "kind": kind,
        "date": datetime.datetime.now().isoformat(),
        "extras": {}
    }
    if url is not None:
        cached["edia"][new_id]["extras"]["url"] = url
    write()


# Read the file
cached = read()
