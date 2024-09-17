from logging import getLogger
from logging.config import dictConfig

from fastapi import FastAPI, HTTPException

from src.config.log_config import dict_config
from src.service.exceptions import http_exception_handler
from src.service.web import lifespan
from src.api.medias_router import medias_router
from src.api.tweets_router import tweets_router

dictConfig(dict_config)
logger = getLogger("routes_logger")


def create_app() -> FastAPI:
    # create app
    app = FastAPI(lifespan=lifespan)
    # register exception handler
    app.add_exception_handler(HTTPException, http_exception_handler)
    # include routers
    app.include_router(tweets_router)
    app.include_router(medias_router)

    return app
