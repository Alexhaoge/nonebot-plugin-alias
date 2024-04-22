from typing import Literal, Optional

from nonebot import get_driver
from pydantic import Field, BaseSettings

class Config(BaseSettings):
    alias_data_path: str = "data/alias"
    redis_url: str = 'redis://localhost'
    max_local_alias: int = 30
    class Config:
        extra = "ignore"

_conf: Optional[Config] = None


def conf() -> Config:
    global _conf
    if _conf is None:
        _conf = Config(**get_driver().config.dict())
    return _conf
