from game_logic import check_num,parse_guess

if __name__ == "__main__":
    assert check_num(10,20) == "小了"
    assert check_num(20,20) == "正确"
    assert check_num(20,10) == "大了"

    assert parse_guess("1") == 1
    assert parse_guess("100") == 100

    try:
        parse_guess("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("输入 abc 时预期出现 ValueError")



