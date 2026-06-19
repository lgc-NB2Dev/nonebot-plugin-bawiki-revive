import sys
from pathlib import Path

import pytest
from pytest_asyncio import is_async_test

TEST_NB2_DIR = Path(__file__).parents[3] / "private" / "test-nb2"
PLUGIN_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))


def pytest_configure(config: pytest.Config) -> None:
    from nonebug import NONEBOT_INIT_KWARGS

    init_kwargs = dict(config.stash.get(NONEBOT_INIT_KWARGS, {}))
    init_kwargs.update(
        {
            "driver": "~fastapi+~websockets+~httpx",
            "localstore_cache_dir": TEST_NB2_DIR / "cache",
            "localstore_config_dir": TEST_NB2_DIR / "config",
            "localstore_data_dir": TEST_NB2_DIR / "data",
            "log_level": "DEBUG",
        },
    )
    config.stash[NONEBOT_INIT_KWARGS] = init_kwargs


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for item in items:
        if is_async_test(item):
            item.add_marker(session_scope_marker, append=False)


@pytest.fixture
def bawiki_revive_plugin(app: object) -> object:  # noqa: ARG001
    import nonebot

    if plugin := nonebot.get_plugin("nonebot_plugin_bawiki_revive"):
        return plugin
    try:
        return nonebot.load_plugin("nonebot_plugin_bawiki_revive")
    except RuntimeError as e:
        if "Plugin already exists" not in str(e):
            raise
    plugin = nonebot.get_plugin("nonebot_plugin_bawiki_revive")
    if plugin is None:
        msg = "Plugin already exists but cannot be found by name"
        raise RuntimeError(msg)
    return plugin
