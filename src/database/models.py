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
    name: Mapped[str] = mapped_column(String)
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
    authors: Mapped[Optional[List["User"]]] = relationship(
        "User",
        secondary="following",
        primaryjoin="User.id==Following.follower_id",
        secondaryjoin="User.id==Following.author_id",
        back_populates="followers",
        cascade="all, delete",
        lazy="joined",
    )
    followers: Mapped[Optional[List["User"]]] = relationship(
        "User",
        secondary="following",
        primaryjoin="User.id==Following.author_id",
        secondaryjoin="User.id==Following.follower_id",
        back_populates="authors",
        cascade="all, delete",
        lazy="joined",
    )

    def brief_json(self) -> dict[str, Any]:
        """Returns brief info about user"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def full_json(self) -> dict[str, Any]:
        result_json: dict = self.brief_json()
        if self.followers is not None:
            result_json["followers"] = [user.brief_json() for user in self.followers]
        if self.authors is not None:
            result_json["following"] = [user.brief_json() for user in self.authors]
        return result_json


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
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    tweet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tweets.id"), nullable=False
    )

    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="unq_likes"),)


class Following(Base):
    __tablename__ = "following"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    follower_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("author_id", "follower_id", name="unq_following"),
    )
