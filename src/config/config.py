from dataclasses import dataclass
from typing import Union

from environs import Env


@dataclass
class DB:
    db_admin: str
    db_password: str


@dataclass
class Config:
    db: DB


def load_config(path: Union[str, None] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(db=DB(db_admin=env('POSTGRESQL_ADMIN'),
                        db_password=env('POSTGRESQL_PASSWORD')))
