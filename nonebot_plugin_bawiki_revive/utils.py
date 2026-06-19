import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    def pmn_extra(
        *,
        func: str | None = None,
        trigger_method: str | None = None,
        trigger_condition: str | None = None,
        brief_des: str | None = None,
        detail_des: str | None = None,
    ) -> dict[str, dict[str, str | None]]: ...

else:

    def pmn_extra(**kwargs):
        return {"pmn": kwargs}


def check_md5(data: bytes, hash_value: str) -> bool:
    return not hash_value or hashlib.md5(data).hexdigest() == hash_value  # noqa: S324


def is_using_picmenu_next() -> bool:
    from nonebot import get_available_plugin_names, get_plugin

    n = "nonebot_plugin_picmenu_next"
    return n in get_available_plugin_names() or bool(get_plugin(n))
