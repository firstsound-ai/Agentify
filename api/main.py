from fastapi import FastAPI

from settings import settings
from web.controller import register_controllers
from web.handler import register_exception_handlers
from web.lifespan import register_lifespan
from web.middleware import register_middlewares

app = FastAPI()

register_middlewares(app)
register_exception_handlers(app)
register_controllers(app)
register_lifespan(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
