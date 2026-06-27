import json
from collections.abc import Iterable
from pathlib import Path


def normalize_alias(alias: str) -> str:
    return alias.strip().casefold()


class AliasStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> dict[str, str]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text("u8"))

    def write(self, data: dict[str, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "u8")

    def resolve(self, alias: str) -> str | None:
        return self.read().get(normalize_alias(alias))

    def set_aliases(self, name: str, aliases: Iterable[str]) -> dict[str, str | None]:
        data = self.read()
        changes: dict[str, str | None] = {}
        for alias in aliases:
            key = normalize_alias(alias)
            if not key:
                continue
            changes[alias.strip()] = data.get(key)
            data[key] = name
        self.write(data)
        return changes

    def delete_aliases(self, aliases: Iterable[str]) -> dict[str, str | None]:
        data = self.read()
        changes: dict[str, str | None] = {}
        for alias in aliases:
            key = normalize_alias(alias)
            if not key:
                continue
            changes[alias.strip()] = data.pop(key, None)
        self.write(data)
        return changes
