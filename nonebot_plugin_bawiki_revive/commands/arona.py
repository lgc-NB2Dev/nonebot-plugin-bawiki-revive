from arclet.alconna import Alconna, Args, CommandMeta, MultiVar, Option, store_true
from nonebot import logger
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Query, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_waiter import prompt

from ..config import config
from ..data_source.arona import (
    AronaClient,
    AronaResponse,
    AronaResult,
    alias_store,
)
from ..utils import pmn_extra

SELECT_MESSAGES = {
    "timeout": "选择超时，已取消",
    "cancel": "已取消选择",
    "invalid": "输入不是数字，已取消选择",
    "out_of_range": "序号超出范围，已取消选择",
}


def join_params(value: object) -> str:
    if isinstance(value, tuple | list):
        return " ".join(str(x) for x in value).strip()
    return str(value or "").strip()


def list_params(value: object) -> list[str]:
    if isinstance(value, tuple | list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [str(value).strip()] if str(value or "").strip() else []


async def send_result(result: AronaResult) -> None:
    if result.type == "plain":
        await UniMessage.text(result.content).finish()
    if result.type == "file":
        try:
            data = await AronaClient().fetch_image(result.content, result.hash)
        except Exception:
            logger.exception("Failed to fetch Arona image")
            await UniMessage.text("Arona 图片获取失败，请稍后再试").finish()
        await UniMessage.image(raw=data).finish()


def get_search_r18(*, use_r18: bool) -> bool:
    if use_r18 and not config.arona_allow_r18_param:
        raise PermissionError("--r18 参数未启用")
    return use_r18 or not config.arona_filter_r18


async def search(query: str, *, use_r18: bool) -> AronaResponse:
    r18 = get_search_r18(use_r18=use_r18)
    actual_query = alias_store.resolve(query) or query
    response = await AronaClient().search(actual_query, r18=r18)
    if not response.is_success():
        raise RuntimeError(f"Arona API returned {response.code}: {response.message}")
    return response


def build_choice_prompt(results: list[AronaResult]) -> str:
    choices = "\n".join(f"{i}. {item.name}" for i, item in enumerate(results, 1))
    return f"找到多个可能的结果，请发送序号选择：\n{choices}\n0. 取消"


def select_result(results: list[AronaResult], text: str | None) -> AronaResult | str:
    if text is None:
        return "timeout"
    text = text.strip()
    if text == "0":
        return "cancel"
    if not text.isdigit():
        return "invalid"
    index = int(text)
    if not (1 <= index <= len(results)):
        return "out_of_range"
    return results[index - 1]


async def wait_for_choice(message: str) -> str | None:
    response = await prompt(message, timeout=config.arona_select_timeout)
    return response.extract_plain_text().strip() if response is not None else None


arona_alc = Alconna(
    "arona",
    Args["query?", MultiVar(str)],
    Option("--r18", action=store_true, help_text="允许返回 R18 结果"),
    meta=CommandMeta(
        description="从 Arona Bot 数据源搜索攻略图或文本",
        usage="arona [--r18] <关键词>",
        example="arona 国际服未来视",
        extra=pmn_extra(
            func="Arona攻略查询",
            trigger_method="`arona` / `Arona`",
            brief_des="从 Arona Bot 数据源搜索攻略图或文本",
            detail_des="用法：`arona [--r18] <关键词>`",
        ),
    ),
)
cmd_arona = on_alconna(
    arona_alc,
    aliases={"Arona"},
    use_cmd_start=True,
    auto_send_output=True,
)


@cmd_arona.handle()
async def _(
    query: Query[object] = Query("~query", None),
    q_r18: Query[bool] = Query("~r18.value", default=False),
) -> None:
    text = join_params(query.result)
    if not text:
        await UniMessage.text("请发送想要搜索的 Arona 攻略关键词").finish()

    use_r18 = bool(q_r18.result)
    try:
        response = await search(text, use_r18=use_r18)
    except PermissionError as e:
        await UniMessage.text(str(e)).finish()
    except Exception:
        logger.exception("Failed to search Arona")
        await UniMessage.text("Arona 搜索失败，请稍后再试").finish()

    if result := response.single_result():
        await send_result(result)

    results = response.data
    if not results:
        await UniMessage.text("没有找到相关 Arona 结果").finish()
    if len(results) == 1:
        await send_result(results[0])

    selected = select_result(
        results, await wait_for_choice(build_choice_prompt(results))
    )
    if isinstance(selected, str):
        await UniMessage.text(SELECT_MESSAGES[selected]).finish()
    await send_result(selected)


set_alias_alc = Alconna(
    "arona设置别名",
    Args["name", str]["aliases", MultiVar(str)],
    meta=CommandMeta(
        description="设置 Arona 查询别名",
        usage="arona设置别名 <原名> <别名...>",
        extra=pmn_extra(
            func="Arona别名设置",
            trigger_method="`arona设置别名` / `Arona设置别名`",
            brief_des="设置本地 Arona 查询别名",
            detail_des="用法：`arona设置别名 <原名> <别名...>`",
        ),
    ),
)
cmd_set_alias = on_alconna(
    set_alias_alc,
    aliases={"Arona设置别名"},
    use_cmd_start=True,
    permission=SUPERUSER if config.arona_alias_only_superuser else None,
)


@cmd_set_alias.handle()
async def _(
    name: Query[str] = Query("~name"),
    aliases: Query[object] = Query("~aliases"),
) -> None:
    alias_list = list_params(aliases.result)
    if not alias_list:
        await UniMessage.text("请提供至少一个别名").finish()
    changes = alias_store.set_aliases(name.result.strip(), alias_list)
    lines = ["已更新 Arona 别名："]
    for alias, old_name in changes.items():
        if old_name:
            lines.append(f"- {alias}: {old_name} -> {name.result.strip()}")
        else:
            lines.append(f"- {alias}: {name.result.strip()}")
    await UniMessage.text("\n".join(lines)).finish()


del_alias_alc = Alconna(
    "arona删除别名",
    Args["aliases", MultiVar(str)],
    meta=CommandMeta(
        description="删除 Arona 查询别名",
        usage="arona删除别名 <别名...>",
        extra=pmn_extra(
            func="Arona别名删除",
            trigger_method="`arona删除别名` / `Arona删除别名`",
            brief_des="删除本地 Arona 查询别名",
            detail_des="用法：`arona删除别名 <别名...>`",
        ),
    ),
)
cmd_del_alias = on_alconna(
    del_alias_alc,
    aliases={"Arona删除别名"},
    use_cmd_start=True,
    permission=SUPERUSER if config.arona_alias_only_superuser else None,
)


@cmd_del_alias.handle()
async def _(aliases: Query[object] = Query("~aliases")) -> None:
    alias_list = list_params(aliases.result)
    if not alias_list:
        await UniMessage.text("请提供至少一个别名").finish()
    changes = alias_store.delete_aliases(alias_list)
    lines = ["已处理 Arona 别名："]
    for alias, old_name in changes.items():
        if old_name:
            lines.append(f"- 已删除 {alias} -> {old_name}")
        else:
            lines.append(f"- 未找到 {alias}")
    await UniMessage.text("\n".join(lines)).finish()
