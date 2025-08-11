from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException

from common.enums.error_code import ErrorCode
from web.vo import Result


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers.

    Args:
        app (FastAPI): The FastAPI application instance.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return Result.error(
            status_code=exc.status_code,
            error_code=ErrorCode.UNKNOWN_ERROR.code,
            detail=exc.detail,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return Result.error(
            status_code=500, error_code=ErrorCode.UNKNOWN_ERROR.code, detail=str(exc)
        )
