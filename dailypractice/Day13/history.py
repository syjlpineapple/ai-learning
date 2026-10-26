
import json
import logging

logger = logging.getLogger(__name__)


def save_history(filename: str, data: list[int]) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_history(filename: str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            logger.info("开始读取历史记录")
            try:
                ls = json.load(f)
            except json.JSONDecodeError:
                logger.warning("JSON 格式错误")
                return []

        if type(ls) is not list:
            logger.warning("历史记录的数据结构错误")
            return []

        for i in ls:
            if type(i) is not int:
                logger.warning("历史记录包含非整数")
                return []

            if not 1 <= i <= 100:
                logger.warning("历史记录数字超出范围")
                return []

        return ls

    except FileNotFoundError:
        logger.warning("历史记录文件不存在")
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(load_history("history.json"))
