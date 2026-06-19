import hashlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
import pytest
from nonebot.adapters import Event
from pydantic import ValidationError
from tenacity.wait import wait_fixed

if TYPE_CHECKING:
    from nonebug import App


def type_validate_python(type_: type[Any], data: Any) -> Any:
    from nonebot.compat import type_validate_python as validate

    return validate(type_, data)


class FakeMessageEvent(Event):
    message: Any
    user_id: str = "user"
    session_id: str = "session"
    to_me: bool = True

    def get_type(self) -> str:
        return "message"

    def get_event_name(self) -> str:
        return "message"

    def get_event_description(self) -> str:
        return str(self.message)

    def get_user_id(self) -> str:
        return self.user_id

    def get_session_id(self) -> str:
        return self.session_id

    def get_message(self) -> Any:
        return self.message

    def is_tome(self) -> bool:
        return self.to_me


def make_event(message: str) -> FakeMessageEvent:
    return FakeMessageEvent(message=make_message(message))


def make_message(message: str) -> Any:
    from nonebot_plugin_alconna.uniseg.fallback import FallbackMessage

    return FallbackMessage(message)


def test_config_defaults(bawiki_revive_plugin: object) -> None:  # noqa: ARG001
    from nonebot_plugin_bawiki_revive.config import ConfigModel

    config = ConfigModel()

    assert str(config.arona_api_base_url) == "https://arona.diyigemt.com/api/v2"
    assert str(config.arona_cdn_base_url) == "https://arona.cdn.diyigemt.com/image"
    assert config.request_timeout == 10.0
    assert config.request_retry_attempts == 3
    assert config.request_retry_wait == 1.0
    assert config.arona_search_size == 8
    assert config.arona_search_method == 3
    assert config.arona_filter_r18 is True
    assert config.arona_allow_r18_param is False
    assert config.arona_alias_only_superuser is False
    assert config.arona_select_timeout == 60.0

    configured = type_validate_python(
        ConfigModel,
        {
            "bawiki_rev_arona_api_base_url": "https://example.test/api",
            "bawiki_rev_request_retry_attempts": 5,
            "bawiki_rev_arona_select_timeout": 12.5,
        },
    )

    assert str(configured.arona_api_base_url) == "https://example.test/api"
    assert configured.request_retry_attempts == 5
    assert configured.arona_select_timeout == 12.5


def test_config_accepts_documented_aliases(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.config import ConfigModel

    config = type_validate_python(
        ConfigModel,
        {
            "bawiki_rev_arona_api_base_url": "https://example.test/api",
            "bawiki_rev_arona_cdn_base_url": "https://example.test/image",
            "bawiki_rev_request_timeout": 2.5,
        },
    )

    assert str(config.arona_api_base_url) == "https://example.test/api"
    assert str(config.arona_cdn_base_url) == "https://example.test/image"
    assert config.request_timeout == 2.5


async def test_request_retries_transient_failures(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.request import req_retry

    calls = 0

    async for attempt in req_retry(wait=wait_fixed(0)):
        with attempt:
            calls += 1
            if calls == 1:
                raise httpx.ConnectError("boom")

    assert calls == 2


async def test_arona_client_builds_search_params_without_rate(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"code": 200, "message": "OK", "data": []})

    client = AronaClient(transport=httpx.MockTransport(handler))

    await client.search("国际服未来视", r18=False)

    assert len(requests) == 1
    assert str(requests[0].url).startswith("https://arona.diyigemt.com/api/v2/image?")
    params = dict(requests[0].url.params)
    assert params == {
        "name": "国际服未来视",
        "size": "8",
        "method": "3",
        "r18": "0",
    }
    assert "rate" not in params


async def test_arona_client_allows_r18_when_requested(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"code": 200, "message": "OK", "data": []})

    client = AronaClient(transport=httpx.MockTransport(handler))

    await client.search("国际服未来视", r18=True)

    assert dict(requests[0].url.params)["r18"] == "1"


def test_arona_response_parses_file_and_plain_results(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaResponse

    response = type_validate_python(
        AronaResponse,
        {
            "code": 101,
            "message": "Fuzzy Search",
            "data": [
                {
                    "name": "国际服未来视",
                    "hash": "abc",
                    "content": "/some/a.png",
                    "type": "file",
                },
                {
                    "name": "说明",
                    "hash": "",
                    "content": "纯文本",
                    "type": "plain",
                },
            ],
        },
    )

    assert response.is_fuzzy_match()
    assert not response.is_exact_match()
    assert response.data is not None
    assert response.data[0].type == "file"
    assert response.data[0].cdn_url("https://cdn.example/image") == (
        "https://cdn.example/image/some/a.png"
    )
    assert response.data[1].type == "plain"


def test_arona_response_exact_match_helper(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaResponse

    response = type_validate_python(
        AronaResponse,
        {
            "code": 200,
            "message": "OK",
            "data": [
                {
                    "name": "国际服未来视",
                    "hash": "abc",
                    "content": "/some/a.png",
                    "type": "file",
                },
            ],
        },
    )

    assert response.is_exact_match()
    assert not response.is_fuzzy_match()
    assert response.single_result() is not None


def test_arona_response_single_result_none_for_fuzzy(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaResponse

    response = type_validate_python(
        AronaResponse,
        {"code": 101, "message": "Fuzzy Search", "data": []},
    )

    assert response.is_success()
    assert response.single_result() is None


def test_arona_result_rejects_unknown_type(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaResult

    with pytest.raises(ValidationError):
        type_validate_python(
            AronaResult,
            {"name": "x", "hash": "", "content": "x", "type": "unknown"},
        )


async def test_image_cache_uses_hash_file(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    image_data = b"image-bytes"
    hash_value = hashlib.md5(image_data, usedforsecurity=False).hexdigest()

    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:  # noqa: ARG001
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=image_data)

    client = AronaClient(transport=httpx.MockTransport(handler))

    first = await client.fetch_image("/some/a.png", hash_value, cache_dir=tmp_path)
    second = await client.fetch_image("/some/a.png", hash_value, cache_dir=tmp_path)

    assert first == image_data
    assert second == image_data
    assert calls == 1
    assert (tmp_path / hash_value).read_bytes() == image_data


async def test_image_cache_defaults_to_arona_cache_dir(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona.client import AronaClient
    from nonebot_plugin_bawiki_revive.data_source.arona.consts import ARONA_CACHE_DIR

    defaults = AronaClient.fetch_image.__kwdefaults__
    assert defaults is not None
    assert defaults["cache_dir"] == ARONA_CACHE_DIR


async def test_image_cache_rejects_md5_mismatch(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    async def handler(request: httpx.Request) -> httpx.Response:  # noqa: ARG001
        return httpx.Response(200, content=b"wrong-image-bytes")

    client = AronaClient(transport=httpx.MockTransport(handler))

    with pytest.raises(ValueError, match="md5"):
        await client.fetch_image("/some/a.png", "0" * 32, cache_dir=tmp_path)

    assert not (tmp_path / ("0" * 32)).exists()


async def test_image_cache_refetches_corrupted_cache(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    image_data = b"image-bytes"
    hash_value = hashlib.md5(image_data, usedforsecurity=False).hexdigest()
    (tmp_path / hash_value).write_bytes(b"corrupted")

    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:  # noqa: ARG001
        nonlocal calls
        calls += 1
        return httpx.Response(200, content=image_data)

    client = AronaClient(transport=httpx.MockTransport(handler))

    assert (
        await client.fetch_image("/some/a.png", hash_value, cache_dir=tmp_path)
        == image_data
    )
    assert calls == 1
    assert (tmp_path / hash_value).read_bytes() == image_data


async def test_arona_client_fetches_image_from_cdn_base_url(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AronaClient

    image_data = b"image-bytes"
    hash_value = hashlib.md5(image_data, usedforsecurity=False).hexdigest()

    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=image_data)

    client = AronaClient(transport=httpx.MockTransport(handler))

    await client.fetch_image("/some/a.png", hash_value, cache_dir=tmp_path)

    assert str(requests[0].url) == "https://arona.cdn.diyigemt.com/image/some/a.png"


def test_alias_store_normalizes_and_updates(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AliasStore

    store = AliasStore(tmp_path / "aliases.json")

    assert store.resolve(" 别名 ") is None
    changes = store.set_aliases("国际服未来视", [" 别名 ", "ALIAS"])
    assert changes == {"别名": None, "ALIAS": None}
    assert store.resolve("别名") == "国际服未来视"
    assert store.resolve("alias") == "国际服未来视"

    removed = store.delete_aliases(["ALIAS", "missing"])

    assert removed == {"ALIAS": "国际服未来视", "missing": None}
    assert store.resolve("alias") is None


def test_alias_store_ignores_empty_aliases(
    bawiki_revive_plugin: object,  # noqa: ARG001
    tmp_path: Path,
) -> None:
    from nonebot_plugin_bawiki_revive.data_source.arona import AliasStore

    store = AliasStore(tmp_path / "aliases.json")

    assert store.set_aliases("国际服未来视", [" ", ""]) == {}
    assert store.delete_aliases([" ", ""]) == {}


def test_get_search_r18_rejects_disabled_r18(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command
    from nonebot_plugin_bawiki_revive.config import ConfigModel

    config = ConfigModel()
    monkeypatch.setattr(arona_command, "config", config)

    with pytest.raises(PermissionError, match="--r18"):
        arona_command.get_search_r18(use_r18=True)


def test_get_search_r18_accepts_enabled_r18(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command
    from nonebot_plugin_bawiki_revive.config import ConfigModel

    config = type_validate_python(
        ConfigModel,
        {"bawiki_rev_arona_allow_r18_param": True},
    )
    monkeypatch.setattr(arona_command, "config", config)

    assert arona_command.get_search_r18(use_r18=True) is True


def test_get_search_r18_honors_filter_default(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command
    from nonebot_plugin_bawiki_revive.config import ConfigModel

    monkeypatch.setattr(arona_command, "config", ConfigModel())
    assert arona_command.get_search_r18(use_r18=False) is False

    monkeypatch.setattr(
        arona_command,
        "config",
        type_validate_python(
            ConfigModel,
            {"bawiki_rev_arona_filter_r18": False},
        ),
    )
    assert arona_command.get_search_r18(use_r18=False) is True


def test_command_loader_loads_arona(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive import commands

    assert hasattr(commands, "load_commands")


def test_arona_alconna_uses_multivar_arguments(
    bawiki_revive_plugin: object,  # noqa: ARG001
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    parsed = arona_command.arona_alc.parse("/arona 国际服 未来视 --r18")
    assert parsed.matched
    query = parsed.query("query")
    assert query == "国际服 未来视"
    assert parsed.query("r18.value") is True

    parsed_alias = arona_command.set_alias_alc.parse(
        "/arona设置别名 国际服未来视 别名1 别名2",
    )
    assert parsed_alias.matched
    assert parsed_alias.query("aliases") == ("别名1", "别名2")


def test_arona_command_select_result(bawiki_revive_plugin: object) -> None:  # noqa: ARG001
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    results = [
        arona_command.AronaResult(
            name="一",
            hash="hash1",
            content="/1.png",
            type="file",
        ),
        arona_command.AronaResult(
            name="二",
            hash="hash2",
            content="/2.png",
            type="file",
        ),
    ]

    assert "1. 一" in arona_command.build_choice_prompt(results)
    assert "2. 二" in arona_command.build_choice_prompt(results)
    assert arona_command.select_result(results, None) == "timeout"
    assert arona_command.select_result(results, "0") == "cancel"
    assert arona_command.select_result(results, "abc") == "invalid"
    assert arona_command.select_result(results, "3") == "out_of_range"
    assert arona_command.select_result(results, "2") is results[1]


async def test_arona_command_wait_for_choice_uses_prompt(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    calls: list[tuple[str, float | None]] = []

    class FakeMessage:
        def extract_plain_text(self) -> str:
            return " 2 "

    async def fake_prompt(message: str, *, timeout: float | None = None) -> FakeMessage:
        calls.append((message, timeout))
        return FakeMessage()

    monkeypatch.setattr(arona_command.config, "arona_select_timeout", 12.5)
    monkeypatch.setattr(arona_command, "prompt", fake_prompt)

    assert await arona_command.wait_for_choice("请选择") == "2"
    assert calls == [("请选择", 12.5)]


async def test_arona_command_wait_for_query_uses_prompt(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    calls: list[tuple[str, float | None]] = []

    class FakeMessage:
        def extract_plain_text(self) -> str:
            return " 国际服未来视 "

    async def fake_prompt(message: str, *, timeout: float | None = None) -> FakeMessage:
        calls.append((message, timeout))
        return FakeMessage()

    monkeypatch.setattr(arona_command.config, "arona_select_timeout", 12.5)
    monkeypatch.setattr(arona_command, "prompt", fake_prompt)

    assert await arona_command.wait_for_query() == "国际服未来视"
    assert calls == [(arona_command.QUERY_PROMPT, 12.5)]


async def test_arona_command_prompts_when_query_missing(
    app: "App",
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    searched: list[tuple[str, bool]] = []
    sent: list[arona_command.AronaResult] = []
    prompts: list[float | None] = []
    result = arona_command.AronaResult(
        name="国际服未来视",
        hash="hash123",
        content="/some/a.png",
        type="file",
    )

    class FakeMessage:
        def extract_plain_text(self) -> str:
            return " 国际服未来视 "

    async def fake_search(query: str, *, use_r18: bool) -> arona_command.AronaResponse:
        searched.append((query, use_r18))
        return arona_command.AronaResponse(code=200, message="OK", data=[result])

    async def fake_send_result(result: arona_command.AronaResult) -> None:
        sent.append(result)

    async def fake_prompt(message: str, *, timeout: float | None = None) -> FakeMessage:
        assert message == arona_command.QUERY_PROMPT
        prompts.append(timeout)
        return FakeMessage()

    monkeypatch.setattr(arona_command, "search", fake_search)
    monkeypatch.setattr(arona_command, "send_result", fake_send_result)
    monkeypatch.setattr(arona_command.config, "arona_select_timeout", 12.5)
    monkeypatch.setattr(arona_command, "prompt", fake_prompt)

    async with app.test_matcher(arona_command.cmd_arona) as ctx:
        bot = ctx.create_bot()
        event = make_event("/arona")
        ctx.receive_event(bot, event)

    assert searched == [("国际服未来视", False)]
    assert sent == [result]
    assert prompts == [12.5]


async def test_arona_command_search_resolves_alias(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    searched: list[tuple[str, bool]] = []
    response = arona_command.AronaResponse(code=200, message="OK", data=[])

    class FakeAliasStore:
        def resolve(self, query: str) -> str | None:
            assert query == "别名"
            return "国际服未来视"

    class FakeAronaClient:
        async def search(self, name: str, *, r18: bool) -> Any:
            searched.append((name, r18))
            return response

    monkeypatch.setattr(arona_command, "get_search_r18", lambda use_r18: use_r18)
    monkeypatch.setattr(arona_command, "alias_store", FakeAliasStore())
    monkeypatch.setattr(arona_command, "AronaClient", FakeAronaClient)

    assert await arona_command.search("别名", use_r18=True) is response
    assert searched == [("国际服未来视", True)]


async def test_arona_command_search_rejects_unsuccessful_response(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    class FakeAliasStore:
        def resolve(self, query: str) -> str | None:  # noqa: ARG002
            return None

    class FakeAronaClient:
        async def search(self, name: str, *, r18: bool) -> Any:  # noqa: ARG002
            return arona_command.AronaResponse(code=500, message="Boom", data=[])

    monkeypatch.setattr(arona_command, "get_search_r18", lambda use_r18: use_r18)
    monkeypatch.setattr(arona_command, "alias_store", FakeAliasStore())
    monkeypatch.setattr(arona_command, "AronaClient", FakeAronaClient)

    with pytest.raises(RuntimeError, match="500: Boom"):
        await arona_command.search("国际服未来视", use_r18=False)


async def test_arona_command_send_plain_result(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    sent: list[tuple[str, str | bytes]] = []

    class FakeMessage:
        def __init__(self, kind: str, value: str | bytes) -> None:
            self.kind = kind
            self.value = value

        async def finish(self) -> None:
            sent.append((self.kind, self.value))

    class FakeUniMessage:
        @staticmethod
        def text(value: str) -> FakeMessage:
            return FakeMessage("text", value)

    monkeypatch.setattr(arona_command, "UniMessage", FakeUniMessage)

    await arona_command.send_result(
        arona_command.AronaResult(
            name="说明",
            hash="",
            content="纯文本",
            type="plain",
        ),
    )

    assert sent == [("text", "纯文本")]


async def test_arona_command_send_file_result(
    bawiki_revive_plugin: object,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nonebot_plugin_bawiki_revive.commands import arona as arona_command

    sent: list[tuple[str, str | bytes]] = []
    fetched: list[tuple[str, str]] = []

    class FakeMessage:
        def __init__(self, kind: str, value: str | bytes) -> None:
            self.kind = kind
            self.value = value

        async def finish(self) -> None:
            sent.append((self.kind, self.value))

    class FakeUniMessage:
        @staticmethod
        def image(*, raw: bytes) -> FakeMessage:
            return FakeMessage("image", raw)

        @staticmethod
        def text(value: str) -> FakeMessage:
            return FakeMessage("text", value)

    class FakeAronaClient:
        async def fetch_image(
            self,
            content: str,
            hash_value: str,
        ) -> bytes:
            fetched.append((content, hash_value))
            return b"image-bytes"

    monkeypatch.setattr(arona_command, "UniMessage", FakeUniMessage)
    monkeypatch.setattr(arona_command, "AronaClient", FakeAronaClient)

    await arona_command.send_result(
        arona_command.AronaResult(
            name="图",
            hash="hash123",
            content="/some/a.png",
            type="file",
        ),
    )

    assert fetched == [("/some/a.png", "hash123")]
    assert sent == [("image", b"image-bytes")]


def test_metadata_is_picmenu_next_compatible() -> None:
    from arclet.alconna import command_manager
    from nonebot import require

    require("nonebot_plugin_picmenu_next")
    require("nonebot_plugin_bawiki_revive")

    import nonebot
    from nonebot_plugin_picmenu_next.data_source.models import PMNPluginExtra

    plugin = nonebot.get_plugin("nonebot_plugin_bawiki_revive")
    assert plugin is not None
    assert plugin.metadata is not None

    extra = type_validate_python(PMNPluginExtra, plugin.metadata.extra)
    assert extra.pmn is not None
    assert extra.pmn.markdown is True
    assert extra.pmn.template == "bawiki_revive"
    assert extra.menu_data is None

    from nonebot_plugin_picmenu_next.templates import (
        detail_templates,
        func_detail_templates,
    )

    assert "bawiki_revive" in detail_templates.data
    assert "bawiki_revive" in func_detail_templates.data

    commands: list[Any] = [
        command
        for command in command_manager.get_commands()
        if command.path
        in {
            "Alconna::arona",
            "Alconna::arona设置别名",
            "Alconna::arona删除别名",
        }
    ]
    assert len(commands) == 3
    assert all("pmn" in command.meta.extra for command in commands)
