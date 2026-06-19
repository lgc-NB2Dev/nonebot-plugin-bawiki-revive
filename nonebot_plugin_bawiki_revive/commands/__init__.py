from pathlib import Path

from cookit import auto_import as auto_load


def load_commands() -> None:
    auto_load(Path(__file__).parent, __package__)
