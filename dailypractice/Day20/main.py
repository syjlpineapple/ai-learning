import logging
from json import JSONDecodeError

from requests import RequestException

from dailypractice.Day20.api_client import APIClient
from dailypractice.Day20.config import load_config

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = {
        "name":"jack"
    }
    setting = load_config()
    api_client = APIClient(setting["api_base_url"],setting["api_key"])
    try:
        api_client.post("getUser",data)
    except JSONDecodeError as e:
        logging.exception("参数解析失败")
    except RequestException as e:
        logging.exception("请求失败")
    finally:
        api_client.close()
