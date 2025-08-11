from typing import Generator

import requests
from fastapi import status

from common.constants import APP_TYPES
from common.enums.error_code import ErrorCode
from common.exceptions import DifyException
from settings import settings


class DifyClient:
    def __init__(self):
        self.url = settings.DIFY_URL
        self.email = settings.DIFY_EMAIL
        self.password = settings.DIFY_PASSWORD
        self.client = requests.Session()
        self.api_token = self._login()
        self.headers = {
            "Authorization": "Bearer " + self.api_token,
        }
        self.client.headers.update(self.headers)

    def close(self):
        self.client.close()

    def _full_url(self, path: str) -> str:
        return self.url.rstrip("/") + "/console/api" + path

    def _login(self) -> str:
        try:
            response = self.client.post(
                self._full_url("/login"),
                json={
                    "email": self.email,
                    "password": self.password,
                },
            )
            if response.status_code != status.HTTP_200_OK:
                raise DifyException(
                    ErrorCode.DIFY_LOGIN_FAILED,
                    response.json()["message"],
                )
            return response.json()["data"]["access_token"]
        except Exception as e:
            raise DifyException(ErrorCode.DIFY_CLIENT_ERROR, str(e))

    def check_connection(self) -> bool:
        try:
            response = self.client.get(self._full_url("/workspaces"))
            if response.status_code != status.HTTP_200_OK:
                raise DifyException(
                    ErrorCode.DIFY_CLIENT_ERROR, response.json()["message"]
                )
            return True
        except Exception as e:
            raise DifyException(ErrorCode.DIFY_CLIENT_ERROR, str(e))

    def create_app(self, app_type: str, app_name: str, app_description: str):
        if app_type not in APP_TYPES:
            raise DifyException(
                ErrorCode.DIFY_CLIENT_ERROR,
                f"Invalid app type: {app_type}. Valid types are: {', '.join(APP_TYPES)}",
            )
        try:
            response = self.client.post(
                self._full_url("/apps"),
                json={
                    "name": app_name,
                    "icon_type": "emoji",
                    "icon": "🤖",
                    "icon_background": "#FFEAD5",
                    "mode": app_type,
                    "description": app_description,
                },
            )

            if response.status_code != 201:
                raise DifyException(
                    ErrorCode.DIFY_CLIENT_ERROR,
                    "Failed to create app: " + response.json().get("message", ""),
                )
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
            raise DifyException(ErrorCode.DIFY_CLIENT_ERROR, str(e))


def get_dify_client() -> Generator[DifyClient, None, None]:
    client = DifyClient()
    client.check_connection()
    try:
        yield client
    finally:
        client.close()
