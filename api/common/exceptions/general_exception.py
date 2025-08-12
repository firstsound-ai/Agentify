from typing import Optional

from fastapi import HTTPException

from common.enums.error_code import ErrorCode


class GeneralException(HTTPException):
    """
    Exception for general.
    """

    def __init__(self, error_code: ErrorCode, detail: Optional[str] = None):
        """
        Initialize the GeneralException.

        Args:
            error_code (ErrorCode): The error code.
            detail (str, optional): The detail of the error. Defaults to None.
        """
        self.error_code: int = error_code.code
        self.detail: str = error_code.message + (f": {detail}" if detail else "")
        super().__init__(
            status_code=int(str(error_code.code)[1:4]),
            detail=self.detail,
        )
