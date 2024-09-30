"""The module is responsible for the database models (tables)"""

import os
from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.config.config import Config, load_config
from src.service.func import get_image_name_by_id

config: Config = load_config()
DB_URL: str = config.db.url
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

    async def to_json(self):
        tweet_json: Dict[str, Any] = dict()
        tweet_json["id"] = self.id
        tweet_json["content"] = self.tweet_data

        # add attachments
        cur_dir_path: str = os.path.dirname(__file__)
        images_dir: str = os.path.join(
            cur_dir_path, "..", "..", "client", "static", "images"
        )
        tweet_json["attachments"] = list()
        if self.images is not None:  # mypy
            for image in self.images:
                image_name: Optional[str] = await get_image_name_by_id(
                    image_id=image.id, images_path=images_dir
                )
                if image_name is None:
                    image_name = ""
                tweet_json["attachments"].append(os.path.join("client", "static", "images", image_name))

        tweet_json["author"] = self.user.brief_json()

        # add likes
        if self.users_like is not None:  # mypy
            tweet_json["likes"] = [
                {"user_id": user.id, "name": user.name} for user in self.users_like
            ]
        else:
            tweet_json["likes"] = list()

        return tweet_json


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
