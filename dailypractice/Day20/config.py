import os
from pathlib import Path

import dotenv


def load_config() -> dict:
    # 这里 建议使用 resolve()
    base_path = Path(__file__).resolve().parent
    dotenv.load_dotenv(base_path / ".env")
    app_env = os.getenv("APP_ENV","testing")

    if app_env not in ["production", "testing", "development"]:
        raise ValueError("错误的环境")

    # 明确覆盖规则
    dotenv.load_dotenv(base_path / f".env.{app_env}",override=True)

    api_base_url = os.getenv("API_BASE_URL")
    if not api_base_url:
        raise ValueError("API_BASE_URL未配置")

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY未配置")
    return {
        "app_env": app_env,
        "api_base_url": api_base_url,
        "api_key": api_key
    }