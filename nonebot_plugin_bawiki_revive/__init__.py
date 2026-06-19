# ruff: noqa: E402

from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_waiter")

from cookit.nonebot.localstore import ensure_localstore_path_config

ensure_localstore_path_config()

from .commands import load_commands
from .config import ConfigModel
from .utils import is_using_picmenu_next

_using_picmenu_next = is_using_picmenu_next()
if _using_picmenu_next:
    from . import pmn as pmn

__version__ = "0.0.1"
__plugin_meta__ = PluginMetadata(
    name="BAWiki Revive",
    description="蔚蓝档案综合插件 堂堂复活（还没完全复活 目前只有 Arona 数据源查询）",
    usage=(
        "见下方（注意：所有命令后如有参数，**必须在命令后加空格！**）"
        if _using_picmenu_next
        else "安装 picmenu-next 插件获取详细使用帮助"
    ),
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki-revive",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "License": "MIT",
        "Author": "LgCuwukii",
        "pmn": {"markdown": True, "template": "bawiki_revive"},
    },
)

load_commands()
