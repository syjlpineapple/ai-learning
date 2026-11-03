import requests

def fetch_data(url:str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("请求失败：", e)
        return None
    except ValueError as e:
        print("响应数据无法解析：", e)
        return None


def main():
    url = "https://httpbin.org/json"

    response = fetch_data(url)
    print("结果：",response)


if __name__ == '__main__':
    main()