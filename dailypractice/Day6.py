import random


def random_num():
    return random.randint(1,100)

def check_num(input_num:int,target_num:int) -> str:
    if input_num == target_num:
        return "正确"
    elif input_num < target_num:
        return "小了"
    else:
        return "大了"

def show_statistics(guess_list:list[int]) -> None:
    print("游戏结束！")
    print("猜测记录：", guess_list)
    print("有效猜测次数：", len(guess_list))

    if not guess_list:
        print("暂无统计数据")
        return

    avg = sum(guess_list) / len(guess_list)
    print("最大猜测值：", max(guess_list))
    print("最小猜测值：", min(guess_list))
    print(f"平均猜测值：{avg:.2f}")

random_num = random_num()
guess_his = []
while True:
    i_num = input("请输入1~100的正整数")
    try:
        if i_num == 'q':
            show_statistics(guess_his)
            break
        i_num = int(i_num)

        if not 1 <= i_num <= 100:
            print("请输入1~100的数字")
            continue
        guess_his.append(i_num)
        result = check_num(i_num,random_num)

        if result == "正确":
            show_statistics(guess_his)
            break
        else:
            print("结果",result,"请继续猜")
            continue
    except ValueError:
        print("格式错误,重新输入")
        continue
