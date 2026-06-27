import json
from pathlib import Path

from nonebot import logger

from .data_source.arona import normalize_alias


def _load_aliases(path: Path) -> dict[str, str] | None:
    try:
        data = json.loads(path.read_text("u8"))
    except json.JSONDecodeError:
        logger.warning("Skip legacy Arona aliases migration: invalid JSON")
        return None

    if not isinstance(data, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in data.items()
    ):
        logger.warning("Skip legacy Arona aliases migration: invalid data structure")
        return None

    return data


def migrate_legacy_aliases() -> None:
    legacy_path = Path.cwd() / "data" / "BAWiki" / "arona_alias.json"

    if not legacy_path.exists():
        return

    legacy_data = _load_aliases(legacy_path)
    if legacy_data is None:
        return

    from .data_source.arona import alias_store

    data = alias_store.read()
    for alias, name in legacy_data.items():
        key = normalize_alias(alias)
        if key:
            data.setdefault(key, name)
    alias_store.write(data)
    logger.info("Successfully migrated legacy Arona aliases")


def do_legacy_migration() -> None:
    migrate_legacy_aliases()
