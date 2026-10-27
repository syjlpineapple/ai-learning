import json
import logging

logger = logging.getLogger(__name__)


def save_history(filename: str, data: list[int]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if type(data) != list:
            logger.error("类型错误")
            raise ValueError("类型错误")
        for item in data:
            if type(item) != int:
                logger.error("元素类型错误")
                raise ValueError("元素类型错误")
            if 100 < item or item < 1:
                logger.error("元素需要是1~100的整数")
                raise ValueError("元素需要是1~100的整数")
        return data
    except FileNotFoundError:
        logger.warning("文件不存在")
        return []
