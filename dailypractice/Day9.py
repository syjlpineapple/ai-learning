

def parse_guess(user_input: str) -> int:
    try:
        int_num = int(user_input)
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None

    if not 1 <= int_num <= 100:
        raise ValueError("数字必须在 1～100")

    return int_num


#input_num = input("请输入:")
#if input_num == "q":
#    print("退出游戏")
#else:
#    guess = parse_guess(input_num)



def test_invalid_input() -> None:
    assert parse_guess("2") == 2
    assert parse_guess("50") == 50
    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")

    try:
        parse_guess("0")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")

    try:
        parse_guess("1000")
    except ValueError:
        pass
    else:
        raise AssertionError("预期出现 ValueError")
test_invalid_input()