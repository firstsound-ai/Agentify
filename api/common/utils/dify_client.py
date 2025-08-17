from typing import Generator, Optional

import requests
from fastapi import status

from common.constants import APP_TYPES, DEFAULT_TEMPLATES
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

    def _create_app(self, app_type: str, app_name: str, app_description: str):
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

    def create_app(self, app_type: str, app_name: str, app_description: str):
        created_app_result = self._create_app(app_type, app_name, app_description)
        _ = self.set_draft(
            draft=DEFAULT_TEMPLATES[app_type],
            app_id=created_app_result["id"],
            hash=DEFAULT_TEMPLATES[app_type]["hash"],
        )
        return created_app_result

    def get_draft(self, app_id: str):
        url = self._full_url(f"/apps/{app_id}/workflows/draft")
        response = self.client.get(url)
        if response.status_code != status.HTTP_200_OK:
            raise DifyException(ErrorCode.DIFY_CLIENT_ERROR, response.json()["message"])
        return response.json()

    def set_draft(self, app_id: str, draft: dict, hash: Optional[str] = None):
        url = self._full_url(f"/apps/{app_id}/workflows/draft")
        if not hash:
            hash = self.get_draft(app_id).get("hash")

        draft["hash"] = hash
        response = self.client.post(url, json=draft)
        if response.status_code != status.HTTP_200_OK:
            raise DifyException(ErrorCode.DIFY_CLIENT_ERROR, response.json()["message"])
        return response.json()


def get_dify_client() -> Generator[DifyClient, None, None]:
    client = DifyClient()
    client.check_connection()
    try:
        yield client
    finally:
        client.close()
