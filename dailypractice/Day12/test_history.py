import tempfile
from pathlib import Path

from dailypractice.Day12.history import load_history
from dailypractice.Day12.history import save_history


# write_text 写入新内容，默认覆盖原内容

def test_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = Path(tmpdir) / "history.json"

        # 测试 1：正常保存和读取
        save_history( str(filename),[10, 20, 30])
        assert load_history(str(filename)) == [10, 20, 30]

        # 测试 2：文件不存在
        not_exist = Path(tmpdir) / "not_exist.json"
        assert load_history(str(not_exist)) == []

        # 测试 3：JSON 格式错误
        filename.write_text("hello", encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 4：JSON 顶层结构不是列表
        filename.write_text('{"guess": 10}', encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 5：列表中包含非整数
        filename.write_text('[10, "abc", 30]', encoding="utf-8")
        assert load_history(str(filename)) == []

        # 测试 6：数字超出 1～100 的范围
        filename.write_text("[10, 101]", encoding="utf-8")
        assert load_history(str(filename)) == []

test_history()