"""The module is responsible for database queries"""
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Image, Tweet


async def user_table_has_rows(session: AsyncSession) -> bool:
    """
    The function checks if there are records in the User table
    :param session: session object
    :type session: AsyncSession
    :return: True, if table User has rows, else False
    :rtype: bool
    """
    exists = await session.execute(select(User))
    return exists.first() is not None


async def create_user(session: AsyncSession, user_dict: dict[str, str]) -> None:
    """
    The function adds the user to the database
    :param session: session object
    :type session: AsyncSession
    :param user_dict: The user's data
    :type user_dict: dict[str, str]
    :return: None
    """
    async with session.begin():
        session.add(User(**user_dict))
        await session.commit()


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> Optional[User]:
    """
    Function for getting user by api_key
    :param session: session object
    :param api_key: user's api_key
    :type api_key: str
    :return: User, if such api_key exists, else None
    :rtype: Optional[User]
    """
    user = await session.execute(select(User).where(User.api_key == api_key))
    return user.first()


async def create_tweet(session: AsyncSession, user: User, tweet_data: dict) -> None:
    """
    Function for creating tweet
    :param session: session object
    :param user: user object
    :type user: User
    :param tweet_data: tweet's data
    :type tweet_data: dict
    :return: None
    """
    async with session.begin():
        tweet_data["user_id"] = user.id
        # if there are images, we will attach them to the tweet
        if "tweet_media_ids" in tweet_data:
            images_ids: List[int] = tweet_data.pop("tweet_media_ids")
            images_res = await session.execute(select(Image).where(Image.id.in_(images_ids)))
            images = images_res.all()

        tweet: Tweet = Tweet(**tweet_data)
        tweet.images = images
        user.tweets.append(tweet)
        await session.commit()
