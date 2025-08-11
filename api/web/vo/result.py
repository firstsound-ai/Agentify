from typing import Any, ClassVar, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Result(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None

    SUCCESS_CODE: ClassVar[int] = 0
    SUCCESS_MESSAGE: ClassVar[str] = "success"

    @classmethod
    def success(cls, data: Optional[Any] = None) -> JSONResponse:
        if data and hasattr(data, "model_dump"):
            data = data.model_dump()
        return JSONResponse(
            status_code=200,
            content=Result(
                code=Result.SUCCESS_CODE, message=Result.SUCCESS_MESSAGE, data=data
            ).model_dump(mode="json"),
        )

    @classmethod
    def error(cls, status_code: int, error_code: int, detail: str) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "code": error_code,
                "message": detail,
                "data": None,
            },
        )
