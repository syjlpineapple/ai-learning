
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def fetch_data(
    url: str,
    params: dict | None = None
) -> Any:
    """
    发送 GET 请求并返回 JSON 数据。

    Args:
        url: API 地址
        params: URL 查询参数

    Returns:
        API 返回的 JSON 数据

    Raises:
        requests.exceptions.RequestException: 请求失败
        ValueError: JSON 解析失败
    """
    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        # 检查 HTTP 状态码
        response.raise_for_status()

        # 解析 JSON
        return response.json()

    except requests.exceptions.RequestException:
        logger.exception("HTTP 请求失败，URL: %s", url)
        raise

    except ValueError:
        logger.exception("JSON 数据解析失败，URL: %s", url)
        raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    req_url = "https://httpbin.org/get"

    params = {
        "q": "Python",
        "limit": 3
    }

    try:
        data = fetch_data(req_url, params)
        print("请求结果：", data)

    except requests.exceptions.Timeout:
        print("请求超时，请稍后重试")

    except requests.exceptions.HTTPError as e:
        print("HTTP 状态错误：", e)

    except requests.exceptions.RequestException as e:
        print("网络请求失败：", e)

    except ValueError as e:
        print("返回数据格式错误：", e)


if __name__ == "__main__":
    main()
