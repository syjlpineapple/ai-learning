import random

from dailypractice.Day10.game_logic import parse_guess,check_num

if __name__ == "__main__":
    target_num = random.randint(1,100)
    print("随机数",target_num)

    while True:
        input_num = input("请输入1~100的数字，输入q退出")
        if input_num == "q":
            print("游戏结束！")
            break
        else:
            try:
                int_num = parse_guess(input_num)
                result = check_num(int_num,target_num)
                print(result)
            except ValueError as e:
                print(e)


