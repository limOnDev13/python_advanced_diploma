"""The module is responsible for the database models (tables)"""
from sqlalchemy import Column, Text, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


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
