

def parse_guess(input_num: str) -> int:
    try:
        int_num = int(input_num)
    except ValueError:
        raise ValueError("输入格式错误，请输入整数") from None
    if not 1 <= int_num <= 100:
        raise ValueError("请输入1~100的整数") from None
    return int_num

def check_num(input_num:int,target_num:int) -> str:
    if input_num < target_num:
        return "小了"
    elif input_num > target_num:
        return "大了"
    else:
        return "正确"


print("启动了")