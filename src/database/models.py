"""The module is responsible for the database models (tables)"""

from typing import Any, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.config.config import Config, load_config

config: Config = load_config()
DB_URL: str = (
    f"postgresql+asyncpg://"
    f"{config.db.user}:{config.db.password}@{config.db.host}:5432"
)
engine = create_async_engine(DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_key: Mapped[str] = mapped_column(String, unique=True, index=True)
    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="user",
        lazy="joined",
        cascade="all, delete, delete-orphan",
    )
    likes_tweets: Mapped[Optional[List["Tweet"]]] = relationship(
        "Tweet",
        secondary="likes",
        back_populates="users_like",
        cascade="all, delete",
        lazy="joined",
    )

    def to_json(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tweet_data: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="tweets")
    images: Mapped[Optional[List["Image"]]] = relationship(
        "Image", lazy="joined", cascade="all, delete, delete-orphan"
    )
    users_like: Mapped[Optional[List["User"]]] = relationship(
        "User",
        secondary="likes",
        back_populates="likes_tweets",
        cascade="all, delete",
        lazy="joined",
    )


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tweet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tweets.id"), nullable=True
    )


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    tweet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tweets.id"), nullable=True
    )

    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="unq_likes"),)
