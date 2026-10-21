
def check_num(input_num: int, target_num: int) -> str:
    if input_num == target_num:
        return "正确"
    elif input_num < target_num:
        return "小了"
    else:
        return "大了"


def test_check_num() -> None:
    assert check_num(30, 50) == "小了"
    assert check_num(50, 50) == "正确"
    assert check_num(70, 50) == "大了"
    assert check_num(1, 100) == "小了"
    assert check_num(100, 1) == "大了"