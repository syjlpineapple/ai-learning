import json


# indent = 2 表示两个空格缩进
# 这里写文件有两种写法，一种是json直接写，另外一种是文件写json字符串
# ensure_ascii=False：让中文直接显示，而不是转成 Unicode 转义序列
def save_history(history:list[int],filename:str) -> None:
    # with open(...) 能确保文件在代码块结束后自动关闭
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False,indent=2)

def load_history(filename:str) -> list[int]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            try:
                ls = json.load(f)
                if type(ls) != list:
                    return []
                for i in ls:
                    if type(i) != int:
                        return []
                    if not 1 <= i <= 100:
                        return []
            except json.decoder.JSONDecodeError:
                return []
        return ls
    except FileNotFoundError:
        return []

if __name__ == '__main__':
    save_history([1,2,3],"history.json")
    print(load_history("history.json"))