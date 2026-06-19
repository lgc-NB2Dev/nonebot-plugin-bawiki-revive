# ruff: noqa: E402

from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_waiter")

from cookit.nonebot.localstore import ensure_localstore_path_config

ensure_localstore_path_config()

from .commands import load_commands
from .config import ConfigModel

__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="BAWiki Revive",
    description="碧蓝档案 Arona 攻略查询插件",
    usage=(
        "arona <关键词> 查询 Arona Bot 攻略数据源\n"
        "arona设置别名 <原名> <别名...> 设置本地别名\n"
        "arona删除别名 <别名...> 删除本地别名"
    ),
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki-revive",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "License": "MIT",
        "Author": "LgCuwukii",
        "pmn": {"markdown": True},
    },
)

load_commands()
