"""The module is responsible for the database models (tables)"""
from sqlalchemy import Column, Text, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.config import load_config, Config


config: Config = load_config()
DB_URL: str = f"postgresql+asyncpg://{config.db.admin}:{config.db.password}@localhost"
engine = create_async_engine(DB_URL)
Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String, unique=True, index=True)
    tweets = relationship("Tweet", back_populates="user", lazy='joined', cascade='all, delete, delete-orphan')


class Tweet(Base):
    __tablename__ = 'Tweet'

    id = Column(Integer, primary_key=True, index=True)
    tweet_data = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship("User", back_populates="tweets")
    images = relationship("Image", lazy='joined', cascade='all, delete, delete-orphan')


class Image(Base):
    __tablename__ = 'Image'

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("Tweet.id"))
