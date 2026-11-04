import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent
def load_config() -> dict[str, str|bool]:
    dotenv.load_dotenv(BASE_DIR/".env")

    env = os.getenv("APP_ENV","development")

    if env not in ["development","testing", "production"]:
        raise ValueError("不支持的运行环境")
    env_file_path = BASE_DIR / f".env.{env}"
    if not env_file_path.exists():
        raise FileNotFoundError(f"不存在的路径：{env_file_path}")
    dotenv.load_dotenv(env_file_path,override=True)

    debug = os.getenv("DEBUG","false").lower() == "true"
    api_key = os.getenv("API_KEY")
    api_base_url = os.getenv("API_BASE_URL")

    if not api_key:
        raise ValueError("API_KEY未配置")
    if not api_base_url:
        raise ValueError("API_BASE_URL未配置")

    return {
        "app_env": env,
        "debug": debug,
        "api_key": api_key,
        "api_base_url": api_base_url,
    }
