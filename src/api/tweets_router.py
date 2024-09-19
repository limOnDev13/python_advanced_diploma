from logging import getLogger
from typing import List, Optional, Dict, Any
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import models
from src.database import queries as q
from src.schemas import schemas
from src.service.exceptions import ForbiddenError
from src.service.images import delete_images_by_ids, validate_images_in_db
from src.service.web import check_api_key, check_tweet_exists, get_session

tweets_router: APIRouter = APIRouter(tags=["tweets"])

logger = getLogger("routes_logger.tweets_router")


@tweets_router.post(
    "/api/tweets",
    status_code=201,
    responses={
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key <api_key> not exists",
                    }
                }
            },
        },
        403: {
            "description": "Some image ids not exist or relate other tweets",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "error message",
                    }
                }
            },
        },
        201: {
            "description": "Tweet was created",
            "content": {
                "application/json": {"example": {"result": True, "tweet_id": 1}}
            },
        },
    },
)
async def create_new_tweet(
    tweet: schemas.TweetInSchema,
    response: Response,
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint creates a new tweet.
    """
    logger.info("Start creating a new tweet")

    # validate images_ids - images must be in db and not relate other tweets
    if tweet.tweet_media_ids:
        try:
            await validate_images_in_db(session, tweet.tweet_media_ids)
        except ValueError as exc:
            logger.debug("Some image ids not exists or relate other tweets")
            raise HTTPException(detail=str(exc), status_code=403)

    tweet_id: int = await q.create_tweet(session, user.id, tweet.model_dump())
    logger.debug("Tweet was created, tweet_id=%d", tweet_id)
    response.status_code = status.HTTP_201_CREATED
    return {"result": "true", "tweet_id": tweet_id}


@tweets_router.delete(
    "/api/tweets/{tweet_id}",
    status_code=200,
    responses={
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key <api_key> not exists",
                    }
                }
            },
        },
        403: {
            "description": "The tweet does not belong to this user",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "ForbiddenError",
                        "error_message": "The tweet {tweet_id} does not belong"
                        " to user {user_id}",
                    }
                }
            },
        },
        404: {
            "description": "Tweet not found",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "NotFoundError",
                        "error_message": "tweet_id {tweet_id} not found",
                    }
                }
            },
        },
        200: {
            "description": "Tweet was deleted",
            "content": {"application/json": {"example": {"result": True}}},
        },
    },
)
async def delete_tweet(
    tweet: models.Tweet = Depends(check_tweet_exists),
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint deletes the tweet by id
    """
    logger.info("Start deleting the tweet")

    # check that tweet relates user
    if tweet.user_id != user.id:
        raise ForbiddenError(
            f"The tweet {tweet.user_id} does not belong to user {user.id}"
        )

    # get images ids which relate this tweet
    images_ids: Optional[List[int]] = await q.get_images_ids_by_tweet_id(
        session, tweet.id
    )
    logger.debug("List of images ids: %s", str(images_ids))
    # delete tweet and images from db
    await q.delete_tweet_by_id(session, tweet.id)
    logger.debug("Tweet and images were deleted from db")

    # delete images from disk
    if images_ids:
        await delete_images_by_ids(images_ids)
        logger.debug("Images were deleted from disk")

    return {"result": True}


@tweets_router.post(
    "/api/tweets/{tweet_id}/likes",
    status_code=200,
    responses={
        400: {
            "description": "The tweet already has a user like",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "The tweet {tweet.id}"
                        " already has a user {user.id} like",
                    }
                }
            },
        },
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
        404: {
            "description": "Tweet not found",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "NotFoundError",
                        "error_message": "tweet_id {tweet_id} not found",
                    }
                }
            },
        },
        200: {
            "description": "The user liked the tweet",
            "content": {"application/json": {"example": {"result": True}}},
        },
    },
)
async def like_tweet(
    tweet: models.Tweet = Depends(check_tweet_exists),
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint to like a tweet
    """
    logger.info("Start liking the tweet")
    logger.debug("Tweet.id=%d, User.id=%d", tweet.id, user.id)
    try:
        await q.like_tweet(session, tweet, user)
    except ValueError as exc:
        logger.warning(str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    logger.info("Successful like")
    return {"result": True}


@tweets_router.delete(
    "/api/tweets/{tweet_id}/likes",
    status_code=200,
    responses={
        400: {
            "description": "The tweet already has not a user like",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "The tweet {tweet.id}"
                        " already has not a user {user.id} like",
                    }
                }
            },
        },
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
        404: {
            "description": "Tweet not found",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "NotFoundError",
                        "error_message": "tweet_id {tweet_id} not found",
                    }
                }
            },
        },
        200: {
            "description": "The user unliked the tweet",
            "content": {"application/json": {"example": {"result": True}}},
        },
    },
)
async def unlike_tweet(
    tweet: models.Tweet = Depends(check_tweet_exists),
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint to unlike a tweet
    """
    logger.info("Start unliking the tweet")
    logger.debug("Tweet.id=%d, User.id=%d", tweet.id, user.id)
    try:
        await q.unlike_tweet(session, tweet, user)
    except ValueError as exc:
        logger.warning(str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    logger.info("Successful unlike")
    return {"result": True}


@tweets_router.get(
    "/api/tweets",
    status_code=200,
    response_model=schemas.TweetOutSchema,
    responses={
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
    },
)
async def get_list_tweets(
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session)
):
    """
    An endpoint for receiving a feed with tweets from users
    whom he follows in descending order of popularity (by number of likes)
    """
    # create a list of tweets from authors that the user is subscribed to
    following: List[models.User] = user.authors
    following_tweets: List[models.Tweet] = list()

    authors_tweets: List[List[models.Tweet]] = await asyncio.gather(*[
        q.get_user_tweets(session, author)
        for author in following
    ])
    for author_tweets in authors_tweets:
        following_tweets.extend(author_tweets)
    # sort the list by popularity (by the number of likes)
    following_tweets.sort(key=lambda tweet: len(tweet.users_like), reverse=True)

    # assemble result
    result: Dict[str, Any] = {
        "result": True,
        "tweets": [
            await tweet.to_json() for tweet in following_tweets
        ]
    }
    return result
