from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    name: str
    permissions: list[str]
