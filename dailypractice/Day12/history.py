import json

def save_history(filename:str, data:list):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False,indent=2)

def load_history(filename:str) -> list:
    try:
        with open(filename) as f:
            try:
                ls = json.load(f)
                if type(ls) != list:
                    return []
                for i in ls:
                    if type(i) != int:
                        return []
                    if not 1 <= i <= 100:
                        return []
                return ls
            except json.decoder.JSONDecodeError:
                return []
    except FileNotFoundError:
        return []
