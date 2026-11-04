import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

def post_user(url:str,user:dict) -> Any:
    try:
        response = requests.post(url,json=user,timeout=10)
        response.raise_for_status()
        return response.json()
    except ValueError:
        logger.exception("参数解析失败")
        raise
    except requests.exceptions.Timeout:
        logger.exception("请求超时")
        raise
    except requests.exceptions.ConnectionError:
        logger.exception("连接失败")
        raise
    except requests.exceptions.RequestException as e:
        logger.exception("请求异常")
        raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    url_path = "https://httpbin.org/post"
    params = {
        "name":"Python",
        "remark":"你好"
    }
    resp = post_user(url_path,params)
    print("响应：",resp)