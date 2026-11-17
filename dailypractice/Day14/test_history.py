import json
import logging
import tempfile
from pathlib import Path

from dailypractice.Day14.history import save_history, load_history


def test_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / "history.json"
        save_history(str(temp_path),[10,20,30])
        assert load_history(str(temp_path)) == [10,20,30]

        not_exist = Path(tmpdir) / "not_exist.json"
        assert load_history(str(not_exist)) == []

        temp_path.write_text("ABBC",encoding="utf-8")
        try:
            load_history(str(temp_path))
        except json.JSONDecodeError:
            pass
        else:
            raise AssertionError("应该抛json异常")

        temp_path.write_text("{\"a\":1}",encoding="utf-8")
        try:
            load_history(str(temp_path))
        except ValueError as e:
            assert str(e) == "类型错误"
        else:
            raise AssertionError("应该抛出 ValueError")

        temp_path.write_text("[10,\"ABC\",30]",encoding="utf-8")
        try:
            load_history(str(temp_path))
        except ValueError as e:
            assert str(e) == "元素类型错误"
        else:
            raise AssertionError("应该抛异常")

        temp_path.write_text("[10,10000,30]",encoding="utf-8")
        try:
            load_history(str(temp_path))
        except ValueError as e:
            assert str(e) == "元素需要是1~100的整数"
        else:
            raise AssertionError("应该抛异常")
    print("测试通过！")

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    test_history()