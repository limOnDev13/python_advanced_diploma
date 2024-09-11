from logging import getLogger
from logging.config import dictConfig

import uvicorn
from fastapi import Depends, FastAPI, Response, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.log_config import dict_config
from src.database import queries as q

from src.schemas import schemas
from src.service.images import upload_image
from src.service.web import lifespan, get_session, json_response_with_error, check_api_key

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
            return user_id

        logger.debug("api_key exists")
        tweet_id: int = await q.create_tweet(session, user_id, tweet.model_dump())
        logger.debug("Tweet was created, tweet_id=%d", tweet_id)
        response.status_code = status.HTTP_201_CREATED
        return {"result": "true", "tweet_id": tweet_id}

    @app.post(
        "/api/medias",
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
        logger.info(f'Start saving image')
        user_id: int | JSONResponse = await check_api_key(api_key, session, response)
        # if api_key is in the database, the function will return user_id,
        # otherwise it will return JSON Response - we will return it immediately
        if not isinstance(user_id, int):
            return user_id

        try:
            image_id: int = await upload_image(image, session)
            return {"result": True, "image_id": image_id}
        except Exception as exc:
            return json_response_with_error(exc)
        finally:
            await image.close()

    return app


if __name__ == "__main__":
    app_ = create_app()
    uvicorn.run(app_)
