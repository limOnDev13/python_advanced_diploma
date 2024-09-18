"""The module is responsible for database queries"""

from logging import Logger
from typing import Dict, List, Optional, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Following, Image, Like, Tweet, User

logger = Logger("query_logger")
logger.setLevel("DEBUG")


async def count_users(session: AsyncSession) -> Optional[int]:
    """
    The function returns count users in db
    :param session: session object
    :type session: AsyncSession
    :return: True, if table User has rows, else False
    :rtype: bool
    """
    num_users = await session.execute(select(func.count()).select_from(User))
    logger.debug("Num users: %d", num_users)
    return num_users.scalar()


async def create_user(session: AsyncSession, user_dict: Dict[str, str]) -> User:
    """
    The function adds the user to the database
    :param session: session object
    :type session: AsyncSession
    :param user_dict: The user's data
    :type user_dict: Dict[str, str]
    :return: None
    """
    new_user = User(**user_dict)
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> Optional[User]:
    """
    Function for getting user by api_key
    :param session: session object
    :param api_key: user's api_key
    :type api_key: str
    :return: user_id, if such api_key exists, else None
    :rtype: Optional[int]
    """
    user = await session.execute(select(User).where(User.api_key == api_key))
    return user.scalars().first()


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
    return get_tweet_q.unique().scalar_one_or_none()


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
    tweet: Optional[Tweet] = await get_tweet_by_id(session, tweet_id)
    if tweet:
        await session.delete(tweet)
        await session.commit()


async def like_tweet(session: AsyncSession, tweet: Tweet, user: User) -> None:
    q = await session.execute(
        select(Like).where(and_(Like.user_id == user.id, Like.tweet_id == tweet.id))
    )
    like = q.scalars().first()
    if like:
        raise ValueError(
            f"The tweet {tweet.id} already has a user {user.id} like. Like_id={like.id}"
        )

    new_like = Like(user_id=user.id, tweet_id=tweet.id)
    session.add(new_like)
    await session.commit()


async def unlike_tweet(session: AsyncSession, tweet: Tweet, user: User) -> None:
    q = await session.execute(
        select(Like).where(and_(Like.user_id == user.id, Like.tweet_id == tweet.id))
    )
    like = q.scalars().first()
    if not like:
        raise ValueError(f"The tweet {tweet.id} already has not a user {user.id} like.")

    await session.delete(like)
    await session.commit()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Function returns user by id"""
    get_user_q = await session.execute(select(User).where(User.id == user_id))
    return get_user_q.scalars().first()


async def follow_author(session: AsyncSession, follower: User, author: User) -> None:
    """The function subscribes the follower to the author"""
    # check that the pairs (follower, author) not in the database
    get_following_q = await session.execute(
        select(Following).where(
            and_(Following.follower_id == follower.id, Following.author_id == author.id)
        )
    )
    pair: Optional[Following] = get_following_q.scalars().first()

    if pair:
        raise ValueError(
            f"The user {follower.id} is already following the author {author.id}"
        )
    new_following = Following(follower_id=follower.id, author_id=author.id)
    session.add(new_following)
    await session.commit()
