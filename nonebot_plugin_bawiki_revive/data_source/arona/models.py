from typing import Literal
from urllib.parse import urljoin

from pydantic import BaseModel


class AronaSearchParams(BaseModel):
    name: str
    size: int
    method: int
    r18: int


class AronaResult(BaseModel):
    name: str
    hash: str
    content: str
    type: Literal["file", "plain"]

    def cdn_url(self, base_url: str) -> str:
        return urljoin(f"{base_url.rstrip('/')}/", self.content.lstrip("/"))


class AronaResponse(BaseModel):
    code: int
    message: str
    data: list[AronaResult] | None = None

    def is_exact_match(self) -> bool:
        return self.code == 200 and len(self.data or []) == 1

    def is_fuzzy_match(self) -> bool:
        return self.code == 101

    def is_success(self) -> bool:
        return self.code in {101, 200}

    def single_result(self) -> AronaResult | None:
        if self.is_exact_match() and self.data:
            return self.data[0]
        return None
