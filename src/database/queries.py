"""The module is responsible for database queries"""

from logging import Logger
from typing import Dict, List, Optional, Sequence

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Image, Tweet, User

logger = Logger("query_logger")
logger.setLevel("DEBUG")


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


async def create_user(session: AsyncSession, user_dict: Dict[str, str]) -> None:
    """
    The function adds the user to the database
    :param session: session object
    :type session: AsyncSession
    :param user_dict: The user's data
    :type user_dict: Dict[str, str]
    :return: None
    """
    session.add(User(**user_dict))
    await session.commit()


async def get_user_id_by_api_key(session: AsyncSession, api_key: str) -> Optional[int]:
    """
    Function for getting user by api_key
    :param session: session object
    :param api_key: user's api_key
    :type api_key: str
    :return: user_id, if such api_key exists, else None
    :rtype: Optional[int]
    """
    user = await session.execute(select(User.id).where(User.api_key == api_key))
    return user.scalar()


async def create_tweet(session: AsyncSession, user_id: int, tweet_data: Dict) -> int:
    """
    Function for creating tweet
    :param session: session object
    :param user_id: user object
    :type user_id: User
    :param tweet_data: tweet's data
    :type tweet_data: Dict
    :return: tweet_id
    :rtype: int
    """
    logger.info("Start creating tweet")
    print("Start creating tweet")
    tweet_data["user_id"] = user_id
    images_ids: Optional[List[int]] = tweet_data.pop("tweet_media_ids")

    # if there are images, we will attach them to the tweet
    if images_ids:
        images_q = await session.execute(select(Image).where(Image.id.in_(images_ids)))
        images = images_q.all()
        tweet_data["images"] = images
    else:
        tweet_data['images'] = list()

    tweet = Tweet(**tweet_data)
    session.add(tweet)
    await session.commit()

    return tweet.id
