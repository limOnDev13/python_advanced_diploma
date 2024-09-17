from logging import getLogger
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import queries as q
from src.schemas import schemas
from src.service.images import delete_images_by_ids, validate_images_in_db
from src.service.web import check_api_key, check_tweet_id, get_session

tweets_router: APIRouter = APIRouter()

logger = getLogger("routes_logger.tweets_logger")


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
                        "error_type": "AuthenticationFailed",
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
                        "error_type": "ValueError",
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
    tweet: schemas.Tweet,
    response: Response,
    user_id: int = Depends(check_api_key),
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

    tweet_id: int = await q.create_tweet(session, user_id, tweet.model_dump())
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
                        "error_type": "AuthenticationFailed",
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
                        "error_type": "NotFound",
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
    tweet_id: int,
    user_id: int = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint deletes the tweet by id
    """
    logger.info("Start deleting the tweet")

    # check tweet_id
    await check_tweet_id(tweet_id, user_id, session)
    logger.debug("tweet_id was found")

    # get images ids which relate this tweet
    images_ids: Optional[List[int]] = await q.get_images_ids_by_tweet_id(
        session, tweet_id
    )
    logger.debug("List of images ids: %s", str(images_ids))
    # delete tweet and images from db
    await q.delete_tweet_by_id(session, tweet_id)
    logger.debug("Tweet and images were deleted from db")

    # delete images from disk
    if images_ids:
        await delete_images_by_ids(images_ids)
        logger.debug("Images were deleted from disk")

    return {"result": True}
