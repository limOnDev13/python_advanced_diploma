"""The module is responsible for the database models (tables)"""
from typing import Any

from sqlalchemy import Column, Text, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config.config import load_config, Config


config: Config = load_config()
DB_URL: str = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@0.0.0.0:5432"
engine = create_async_engine(DB_URL)
Base = declarative_base()
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String, unique=True, index=True)
    tweets = relationship("Tweet", back_populates="user", lazy='joined', cascade='all, delete, delete-orphan')

    def to_json(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}


class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True, index=True)
    tweet_data = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="tweets")
    images = relationship("Image", lazy='joined', cascade='all, delete, delete-orphan')


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
