import shutil
from pathlib import Path

from nonebot import logger

from .data_source.arona import ARONA_ALIAS_PATH


def migrate_legacy_aliases() -> None:
    legacy_path = Path.cwd() / "data" / "BAWiki" / "arona_alias.json"

    if ARONA_ALIAS_PATH.exists() or not legacy_path.exists():
        return

    ARONA_ALIAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy_path, ARONA_ALIAS_PATH)
    legacy_path.unlink()
    logger.info("Successfully migrated legacy Arona aliases")


def do_legacy_migration() -> None:
    migrate_legacy_aliases()
