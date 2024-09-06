"""The module is responsible for the database models (tables)"""

from typing import Any, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped

from src.config.config import Config, load_config

config: Config = load_config()
DB_URL: str = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@0.0.0.0:5432"
engine = create_async_engine(DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    tweets: Mapped[List['Tweet']] = relationship(
        "Tweet",
        back_populates="user",
        lazy="joined",
        cascade="all, delete, delete-orphan",
    )

    def to_json(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tweet_data: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped['User'] = relationship("User", back_populates="tweets")
    images: Mapped[Optional[List['Image']]] = relationship("Image", lazy="joined", cascade="all, delete, delete-orphan")


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tweet_id: Mapped[int] = mapped_column(Integer, ForeignKey("tweets.id"))
