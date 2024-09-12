import uvicorn

from src.api import routes

if __name__ == "__main__":
    app = routes.create_app()
    uvicorn.run(app, host="0.0.0.0")
