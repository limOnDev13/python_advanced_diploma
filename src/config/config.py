from dataclasses import dataclass
from typing import Union

from environs import Env


@dataclass
class DB:
    url: str


@dataclass
class Config:
    db: DB
    env: str


def _get_db_url(env: Env):
    """The function retrieves the ENV variable,
    and depending on it returns the required url"""
    mode: str = env("ENV")
    if mode == "debug":
        return env("DB_URL_DEBUG")
    elif mode == "test":
        return env("DB_URL_TEST")
    else:
        return env("DB_URL")


def load_config(path: Union[str, None] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        db=DB(url=_get_db_url(env)),
        env=env("ENV"),
    )
