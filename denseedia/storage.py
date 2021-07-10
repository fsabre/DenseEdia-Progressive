from pathlib import Path
from typing import Any, cast, Dict, Optional as Opt, Union

import yaml
from typing_extensions import TypedDict

from .constants import now


class EdiumType(TypedDict):
    id: int
    title: str
    kind: Opt[str]
    date: str
    extras: Dict[str, Any]


class Storage:
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = path if isinstance(path, Path) else Path(path)

        self.edia: Dict[int, EdiumType] = {}

        # Load the content of the file
        self.read_file()

    def read_file(self) -> None:
        """Read a file."""
        try:
            with self.path.open(encoding="utf8") as file:
                raw = yaml.full_load(file)
            for edium_id, raw_edium in raw["edia"].items():
                edium = cast(EdiumType, dict(**raw_edium, id=edium_id))
                self.edia[edium_id] = edium
        except FileNotFoundError:
            print(f"No file at '{self.path}'")

    def write_file(self) -> None:
        """Write the data to the file."""
        # Create the raw dict data
        raw: Any = {"edia": {}}
        for edium_id, edium in self.edia.items():
            raw_edium = dict(**edium)
            raw_edium.pop("id")
            raw["edia"][edium_id] = raw_edium

        # Create the containing directory
        parent_dir = self.path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # Write the YAML to a file
        with self.path.open("w", encoding="utf8") as write_file:
            yaml.dump(raw, write_file, allow_unicode=True)

    def get_new_id(self) -> int:
        """Get an Edium ID that's not in use."""
        try:
            return max(self.edia.keys()) + 1
        except ValueError:
            return 1

    def add_edium(
        self,
        title: str,
        kind: Opt[str],
        url: Opt[str],
        comment: Opt[str]
    ) -> None:
        """Create an Edium and write it in file."""
        new_id = self.get_new_id()
        new_edium: EdiumType = {
            "id": new_id,
            "title": title,
            "kind": kind,
            "date": now().isoformat(),
            "extras": {}
        }
        if url is not None:
            new_edium["extras"]["url"] = url
        if comment is not None:
            new_edium["extras"]["comment"] = comment

        self.edia[new_id] = new_edium

        self.write_file()
