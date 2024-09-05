"""The module is responsible for the work of the database"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.config import load_config, Config


config: Config = load_config()
DB_URL: str = f"postgresql+asyncpg://{config.db.admin}:{config.db.password}@localhost"
engine = create_async_engine(DB_URL)
Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

