from enum import Enum


class ErrorCode(Enum):
    """
    Error Code.
    Rules:
    - 1st digit: Service level (1-Generic, 2-Specific)
    - 2nd-4th digit: HTTP status code (e.g., 404, 500)
    - 5th-7th digit: Specific error number
    """

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    # === Core Generic Errors (1xxxxx) ===
    # 1400xxx - Request Errors
    VALIDATION_ERROR = (1400001, "Request data validation failed")

    # 1401xxx - Authentication Errors
    UNAUTHORIZED = (1401001, "Authentication failed")
    INVALID_TOKEN = (1401002, "Invalid or expired token")

    # 1403xxx - Permission Errors
    FORBIDDEN = (1403001, "Permission denied for this resource")

    # 1404xxx - Resource Not Found
    NOT_FOUND = (1404001, "The requested resource does not exist")

    # 1500xxx - Internal Server Errors
    INTERNAL_SERVER_ERROR = (1500001, "Internal server error")
    DATABASE_ERROR = (1500002, "Database operation error")
    EXTERNAL_SERVICE_ERROR = (1500003, "External service error")
    CONFIGURATION_ERROR = (1500004, "Server configuration error")

    # 1999xxx - Unknown Errors
    UNKNOWN_ERROR = (1999001, "An unknown error occurred")

    # === Specific Business Errors (2xxxxx) ===
    # 2001xx - Dify-related
    DIFY_CLIENT_ERROR = (2001001, "Dify client error")
    DIFY_LOGIN_FAILED = (2001002, "Dify login failed")
