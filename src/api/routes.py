from logging import getLogger
from logging.config import dictConfig
from typing import List, Optional

from fastapi import Depends, FastAPI, Response, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.log_config import dict_config
from src.database import queries as q
from src.schemas import schemas
from src.service.exceptions import http_exception_handler
from src.service.images import (
    delete_images_by_ids,
    upload_image,
    validate_image,
    validate_images_in_db,
)
from src.service.web import (
    check_api_key,
    check_tweet_id,
    get_session,
    lifespan,
)

dictConfig(dict_config)
logger = getLogger("routes_logger")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_exception_handler(HTTPException, http_exception_handler)

    @app.post(
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

    @app.delete(
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
                            "error_message": "The tweet {tweet_id} does not belong to user {user_id}",
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

    @app.post(
        "/api/medias",
        status_code=201,
        responses={
            400: {
                "description": "Something went wrong when uploading the image",
                "content": {
                    "application/json": {
                        "example": {
                            "result": False,
                            "error_type": "error type",
                            "error_message": "error message",
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
                            "error_type": "AuthenticationFailed",
                            "error_message": "api_key <api_key> not exists",
                        }
                    }
                },
            },
            403: {
                "description": "Image size too large or image has invalid format",
                "content": {
                    "application/json": {
                        "example": {
                            "result": False,
                            "error_type": "error type",
                            "error_message": "error message",
                        }
                    }
                },
            },
            201: {
                "description": "Image was saved",
                "content": {
                    "application/json": {"example": {"result": True, "media_id": 1}}
                },
            },
        },
    )
    async def save_image(
        image: UploadFile,
        user_id: int = Depends(check_api_key),
        session: AsyncSession = Depends(get_session),
    ):
        """
        The endpoint saves the image to disk
        """
        logger.info("Start saving image")

        try:
            logger.debug("Validating image")
            validate_image(image)

            logger.debug("Trying to upload an image")
            image_id: int = await upload_image(image, session)
            logger.debug("Image was uploaded, image_id=%s", image_id)

            return {"result": True, "image_id": image_id}
        except ValueError as exc:
            logger.warning("Image too large", exc_info=exc)
            raise HTTPException(detail=str(exc), status_code=403)
        except TypeError as exc:
            logger.warning("Wrong image format", exc_info=exc)
            raise HTTPException(detail=str(exc), status_code=403)
        except Exception as exc:
            logger.exception("Smth wrong", exc_info=exc)
            raise HTTPException(detail=str(exc), status_code=400)
        finally:
            await image.close()

    return app
