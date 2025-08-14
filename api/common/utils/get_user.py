from fastapi import Request

from common.constants import DEFAULT_USER_INFO
from common.dto.user import UserInfo


def get_user_info(request: Request) -> UserInfo:
    user_info = getattr(request.state, "user", DEFAULT_USER_INFO)
    return UserInfo(
        id=user_info["id"], name=user_info["name"], permissions=user_info["permissions"]
    )
