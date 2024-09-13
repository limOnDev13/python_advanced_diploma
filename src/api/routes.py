from logging import getLogger
from logging.config import dictConfig

from fastapi import Depends, FastAPI, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.log_config import dict_config
from src.database import queries as q
from src.schemas import schemas
from src.service.images import upload_image, validate_image, validate_images_in_db
from src.service.web import (
    check_api_key,
    get_session,
    json_response_with_error,
    lifespan,
)

dictConfig(dict_config)
logger = getLogger("routes_logger")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

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
        api_key: str,
        tweet: schemas.Tweet,
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        """
        The endpoint creates a new tweet.
        """
        logger.info("Start creating a new tweet")
        user_id: int | JSONResponse = await check_api_key(api_key, session, response)
        # if api_key is in the database, the function will return user_id,
        # otherwise it will return JSON Response - we will return it immediately
        if not isinstance(user_id, int):
            logger.warning("api_key not found")
            return user_id
        logger.debug("Identification is successful")

        # validate images_ids - images must be in db and not relate other tweets
        if tweet.tweet_media_ids:
            try:
                await validate_images_in_db(session, tweet.tweet_media_ids)
            except ValueError as exc:
                logger.debug("Some image ids not exists or relate other tweets")
                return json_response_with_error(exc, 403)

        tweet_id: int = await q.create_tweet(session, user_id, tweet.model_dump())
        logger.debug("Tweet was created, tweet_id=%d", tweet_id)
        response.status_code = status.HTTP_201_CREATED
        return {"result": "true", "tweet_id": tweet_id}

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
        api_key: str,
        image: UploadFile,
        response: Response,
        session: AsyncSession = Depends(get_session),
    ):
        """
        The endpoint saves the image to disk
        """
        logger.info("Start saving image")
        user_id: int | JSONResponse = await check_api_key(api_key, session, response)
        # if api_key is in the database, the function will return user_id,
        # otherwise it will return JSON Response - we will return it immediately
        if not isinstance(user_id, int):
            logger.warning("api_key not found")
            return user_id
        logger.debug("Identification is successful")

        try:
            logger.debug("Validating image")
            validate_image(image)

            logger.debug("Trying to upload an image")
            image_id: int = await upload_image(image, session)
            logger.debug("Image was uploaded, image_id=%s", image_id)

            return {"result": True, "image_id": image_id}
        except ValueError as exc:
            logger.warning("Image too large", exc_info=exc)
            return json_response_with_error(exc, 403)
        except TypeError as exc:
            logger.warning("Wrong image format", exc_info=exc)
            return json_response_with_error(exc, 403)
        except Exception as exc:
            logger.exception("Smth wrong", exc_info=exc)
            return json_response_with_error(exc, 400)
        finally:
            await image.close()

    return app
