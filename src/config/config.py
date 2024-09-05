from dataclasses import dataclass
from typing import Union

from environs import Env


@dataclass
class DB:
    admin: str
    password: str


@dataclass
class Config:
    db: DB


def load_config(path: Union[str, None] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(db=DB(admin=env('POSTGRESQL_ADMIN'),
                        password=env('POSTGRESQL_PASSWORD')))