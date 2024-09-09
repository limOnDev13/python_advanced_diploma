import uvicorn

from api import routes


if __name__ == "__main__":
    app = routes.create_app()
    uvicorn.run(app)
