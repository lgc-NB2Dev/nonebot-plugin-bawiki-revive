from cookit.pyd import model_with_alias_generator
from nonebot import get_plugin_config
from pydantic import BaseModel, Field


@model_with_alias_generator(lambda x: f"bawiki_rev_{x}")
class ConfigModel(BaseModel):
    request_timeout: float | None = 10.0
    request_retry_attempts: int = 3
    request_retry_wait: float = 1.0

    arona_api_base_url: str = Field(
        default="https://arona.diyigemt.com/api/v2",
    )
    arona_cdn_base_url: str = Field(
        default="https://arona.cdn.diyigemt.com/image",
    )
    arona_search_size: int = 8
    arona_search_method: int = 3
    arona_filter_r18: bool = True
    arona_allow_r18_param: bool = False
    arona_alias_only_superuser: bool = False
    arona_select_timeout: float = 60.0


config: ConfigModel = get_plugin_config(ConfigModel)
