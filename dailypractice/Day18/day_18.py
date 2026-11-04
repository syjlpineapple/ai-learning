import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"


def load_config() -> dict[str, str]:
    load_dotenv(ENV_PATH)

    api_key = os.getenv("API_KEY_TEST")
    api_base_url = os.getenv("API_BASE_URL")

    if not api_key:
        raise ValueError("缺少 API_KEY_TEST")

    if not api_base_url:
        raise ValueError("缺少 API_BASE_URL")

    return {
        "api_key": api_key,
        "api_base_url": api_base_url,
    }