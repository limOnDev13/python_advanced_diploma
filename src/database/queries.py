"""The module is responsible for database queries"""

from logging import Logger
from typing import Dict, List, Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Image, Tweet, User

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
    images: Sequence[Image] = list()
    if images_ids:
        images = await get_images_by_ids(session, images_ids)

    tweet = Tweet(**tweet_data)
    tweet.images = list(images)
    session.add(tweet)
    await session.commit()

    return tweet.id


async def add_image(session: AsyncSession) -> int:
    """
    Function for adding information about an image.
    For now, it adds an empty string. Returns the image id
    :param session: session object
    :return: image id
    :rtype: int
    """
    logger.info("Start adding image")
    image = Image()
    session.add(image)
    await session.commit()
    return image.id


async def get_images_by_ids(
    session: AsyncSession, images_ids: List[int]
) -> Sequence[Image]:
    """
    The function returns an image row by id
    :param session: session object
    :param images_ids: List of images ids
    :type images_ids: List[int]
    :return: List of objects Images
    :rtype: Result[tuple[Image]]
    """
    images_q = await session.execute(select(Image).where(Image.id.in_(images_ids)))
    return images_q.scalars().all()


async def get_all_images_ids(session: AsyncSession) -> List[int]:
    """Function returns all images ids"""
    images_q = await session.execute(select(Image.id))
    return [image_row[0] for image_row in images_q.all()]


async def get_tweet_by_id(session: AsyncSession, tweet_id: int) -> Optional[Tweet]:
    """Function returns tweet by id"""
    get_tweet_q = await session.execute(select(Tweet).where(Tweet.id == tweet_id))
    return get_tweet_q.scalar_one_or_none()


async def get_images_ids_by_tweet_id(
    session: AsyncSession, tweet_id: int
) -> Optional[List[int]]:
    """Function returns list image ids by tweet_id"""
    images_ids_q = await session.execute(
        select(Image.id).where(Image.tweet_id == tweet_id)
    )
    return [image_row[0] for image_row in images_ids_q.all()]


async def delete_tweet_by_id(session: AsyncSession, tweet_id: int) -> None:
    """Function delete the tweet from db by id.
    Returns list of images ids, which relate to this tweet or None"""
    await session.execute(delete(Tweet).where(Tweet.id == tweet_id))
    await session.commit()
