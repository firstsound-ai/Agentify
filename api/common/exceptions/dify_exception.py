from typing import Optional

from fastapi import HTTPException, status

from common.enums.error_code import ErrorCode


class DifyException(HTTPException):
    """
    Exception for Dify API.
    """

    def __init__(self, error_code: ErrorCode, detail: Optional[str] = None):
        """
        Initialize the DifyException.

        Args:
            error_code (ErrorCode): The error code.
            detail (str, optional): The detail of the error. Defaults to None.
        """
        self.error_code: int = error_code.code
        self.detail: str = error_code.message + (f": {detail}" if detail else "")
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self.detail,
        )
