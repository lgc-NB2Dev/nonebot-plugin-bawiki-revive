from pathlib import Path
from typing import Any

import anyio
import httpx
from cookit import copy_func_annotations
from nonebot.compat import model_dump, type_validate_python

from ...config import config
from ...utils import check_md5
from ..request import BAWikiBaseClient
from .consts import ARONA_CACHE_DIR
from .models import AronaResponse, AronaSearchParams


class AronaCDNClient(BAWikiBaseClient):
    @copy_func_annotations(httpx.AsyncClient.__init__)
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            base_url=kwargs.pop("base_url", None) or str(config.arona_cdn_base_url),
            **kwargs,
        )


class AronaClient(BAWikiBaseClient):
    @copy_func_annotations(httpx.AsyncClient.__init__)
    def __init__(self, **kwargs: Any) -> None:
        self._cdn_transport = kwargs.get("transport")
        super().__init__(
            base_url=kwargs.pop("base_url", None) or str(config.arona_api_base_url),
            **kwargs,
        )

    async def search(self, name: str, *, r18: bool) -> AronaResponse:
        params = AronaSearchParams(
            name=name,
            size=config.arona_search_size,
            method=config.arona_search_method,
            r18=1 if r18 else 0,
        )
        response = await self.get(
            "image",
            params=model_dump(params),
        )
        response.raise_for_status()
        return type_validate_python(AronaResponse, response.json())

    async def fetch_image(
        self,
        content: str,
        hash_value: str,
        *,
        cache_dir: Path = ARONA_CACHE_DIR,
    ) -> bytes:
        if not content.startswith("/"):
            raise ValueError("Arona image content path must start with /")
        cache_path = anyio.Path(cache_dir / hash_value)
        await anyio.Path(cache_dir).mkdir(parents=True, exist_ok=True)
        if hash_value and await cache_path.exists():
            data = await cache_path.read_bytes()
            if check_md5(data, hash_value):
                return data
            await cache_path.unlink()

        async with AronaCDNClient(transport=self._cdn_transport) as client:
            response = await client.get(content.lstrip("/"))
        response.raise_for_status()
        data = response.content
        if not check_md5(data, hash_value):
            msg = "Arona image md5 mismatch"
            raise ValueError(msg)
        if hash_value:
            await cache_path.write_bytes(data)
        return data
