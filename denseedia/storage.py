import datetime
from typing import Dict, Optional as Opt

import yaml
from typing_extensions import TypedDict

from .config import DB_PATH


class EdiumType(TypedDict):
    id: int
    title: str
    kind: Opt[str]
    date: str


class StorageType(TypedDict):
    edia: Dict[int, EdiumType]


def read() -> StorageType:
    """Read the file."""
    try:
        with open(DB_PATH) as read_file:
            return yaml.full_load(read_file)
    except FileNotFoundError:
        return {"edia": {}}


def write() -> None:
    """Write the cached data to the file."""
    with open(DB_PATH, "w") as write_file:
        yaml.dump(cached, write_file)


def get_new_id() -> int:
    """Get an Edium ID not in use."""
    try:
        return max(cached["edia"].keys()) + 1
    except ValueError:
        return 1


def add_edium(title: str, kind: Opt[str]) -> None:
    """Create an Edium, cache it and write in file."""
    new_id = get_new_id()
    cached["edia"][new_id] = {
        "id": new_id,
        "title": title,
        "kind": kind,
        "date": datetime.datetime.now().isoformat()
    }
    write()


# Read the file
cached = read()
