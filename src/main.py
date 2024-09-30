import uvicorn

from src.api import routes

app = routes.create_app()
