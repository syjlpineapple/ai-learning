import logging
from json import JSONDecodeError

import requests

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url, test_key):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {test_key}",
            "Accept": "application/json"
        })

    def post(self,path:str,data:dict):
        try:
            url = f"{self.base_url}/{path.lstrip('/')}"
            response = self.session.post(url, json=data, timeout=10)
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