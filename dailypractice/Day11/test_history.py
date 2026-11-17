import tempfile
from pathlib import Path

from dailypractice.Day11.history import save_history, load_history


def test_history():
    with tempfile.TemporaryDirectory() as temp_dir:
        filename = Path(temp_dir) / "history.json"
        print(filename)
        save_history([10, 20, 30], str(filename))
        print(load_history(str(filename)))
        assert load_history(str(filename)) == [10, 20, 30]

    assert load_history(str(Path(temp_dir)/"not_exist.json")) == []

    with tempfile.TemporaryDirectory() as temp_dir:
        filename = Path(temp_dir) / "error.json"
        filename.write_text("hello", encoding="utf-8")
        assert load_history(str(filename)) == []

    with tempfile.TemporaryDirectory() as temp_dir:
        filename = Path(temp_dir) / "history.json"
        print(filename)
        save_history([10, "abc", 30], str(filename))
        print(load_history(str(filename)))
        assert load_history(str(filename)) == []



if __name__ == "__main__":
    test_history()
    print("所有测试通过！")