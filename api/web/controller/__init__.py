from fastapi import Depends, FastAPI

from common.utils.dify_client import DifyClient, get_dify_client
from web.controller.requirement import router as requirement_router
from web.controller.blueprint import router as blueprint_router
from web.controller.workflow import router as workflow_router
from web.vo import Result


def register_controllers(app: FastAPI):
    """Register all API controllers.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    @app.get("/api/health", description="Health check endpoint")
    async def health_check():
        return Result.success(data={"app_status": "ok"})

    @app.get("/api/dify-health", description="Dify health check endpoint")
    async def dify_health_check(client: DifyClient = Depends(get_dify_client)):
        client.check_connection()
        return Result.success(data={"dify_status": "ok"})

    app.include_router(requirement_router)
    app.include_router(blueprint_router)
    app.include_router(workflow_router)
