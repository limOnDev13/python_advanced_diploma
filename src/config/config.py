from dataclasses import dataclass
from typing import Union

from environs import Env


@dataclass
class DB:
    user: str
    password: str
    host: str


@dataclass
class Config:
    db: DB


def load_config(path: Union[str, None] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        db=DB(
            user=env("POSTGRES_USER"),
            password=env("POSTGRES_PASSWORD"),
            host=env("POSTGRES_HOST"),
        )
    )
