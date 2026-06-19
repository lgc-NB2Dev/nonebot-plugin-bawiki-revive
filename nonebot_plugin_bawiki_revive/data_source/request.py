import httpx
from cookit import copy_func_annotations
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from ..config import config


@copy_func_annotations(AsyncRetrying)
def req_retry(*args, **kwargs):
    return AsyncRetrying(
        *args,
        reraise=kwargs.pop("reraise", True),
        retry=kwargs.pop("retry", None) or retry_if_exception_type(httpx.HTTPError),
        stop=(
            kwargs.pop("stop", None)
            or stop_after_attempt(config.request_retry_attempts)
        ),
        wait=kwargs.pop("wait", None) or wait_fixed(config.request_retry_wait),
        **kwargs,
    )


class BAWikiBaseClient(httpx.AsyncClient):
    @copy_func_annotations(httpx.AsyncClient.__init__)
    def __init__(self, **kwargs) -> None:
        super().__init__(
            base_url=kwargs.pop("base_url", None),
            timeout=kwargs.pop("timeout", None) or config.request_timeout,
            follow_redirects=kwargs.pop("follow_redirects", True),
            **kwargs,
        )

    @copy_func_annotations(httpx.AsyncClient.request)
    async def request(self, *args, **kwargs):
        async for attempt in req_retry():
            with attempt:
                return await super().request(*args, **kwargs)
        raise RuntimeError("unreachable tenacity request state")
