import logging
from json import JSONDecodeError
from typing import Any

import requests

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str,api_key:str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        })

    def post(self,endpoint:str,data:dict) -> Any:
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, json=data,timeout=10)
            response.raise_for_status()
            return response.json()
        except JSONDecodeError:
            logger.exception("JSON解析错误")
            raise
        except requests.RequestException:
            logger.exception("请求失败")
            raise

    def close(self) -> None:
        self.session.close()