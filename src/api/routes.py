import os
from logging import getLogger
from logging.config import dictConfig

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.medias_router import medias_router
from src.api.tweets_router import tweets_router
from src.api.users_router import users_router
from src.config.log_config import dict_config
from src.service.exceptions import http_exception_handler
from src.service.web import lifespan

dictConfig(dict_config)
logger = getLogger("routes_logger")

tags_metadata = [
    {
        "name": "main",
    },
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "tweets",
        "description": "Operations with tweets.",
    },
    {
        "name": "medias",
        "description": "Operations with images.",
    },
]


def create_app() -> FastAPI:
    # create app
    app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)
    # register exception handler
    app.exception_handler(HTTPException)(http_exception_handler)
    # include routers
    app.include_router(tweets_router)
    app.include_router(medias_router)
    app.include_router(users_router)

    # mount static
    templates = Jinja2Templates(directory=os.path.join(".", "src", "static"))
    app.mount(
        "/", StaticFiles(directory=os.path.join(".", "src", "static")), name="static"
    )

    @app.get("/", response_class=HTMLResponse)
    def main():
        return templates.TemplateResponse("index.html")

    return app
