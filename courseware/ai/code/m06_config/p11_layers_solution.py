"""第 11 题 · 参考答案。"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from dotenv import dotenv_values

from m06_config.p10_settings_solution import ConfigError, Settings, load_settings

ENVIRONMENTS = ("development", "testing", "production")
KNOWN_KEYS = ("APP_ENV", "API_KEY", "API_BASE_URL", "TIMEOUT", "RETRIES", "DEBUG")
SYSTEM = "环境变量"


def read_file(path: Path) -> dict[str, str]:
    """读一个 .env 文件。不存在就是空的；没有等号的行（值为 None）跳过。"""
    if not path.is_file():
        return {}
    return {k: v for k, v in dotenv_values(path, encoding="utf-8").items() if v is not None}


def merge_layers(config_dir: Path, environ: Mapping[str, str]) -> tuple[str, dict[str, str],
                                                                         dict[str, str]]:
    base = read_file(config_dir / ".env")

    # APP_ENV 自己也分层：系统环境变量 > .env > 默认值
    raw_env = environ.get("APP_ENV") or base.get("APP_ENV") or "development"
    env = raw_env.strip().lower()
    if env not in ENVIRONMENTS:
        raise ConfigError(f"APP_ENV 只能是 {'、'.join(ENVIRONMENTS)}，实际是 {raw_env!r}")

    env_file = config_dir / f".env.{env}"
    if not env_file.is_file():
        raise ConfigError(f"找不到 {env} 环境的配置文件：{env_file}")

    # 优先级从低到高；后面的覆盖前面的。系统环境变量放最后，所以永远赢
    layers: list[tuple[str, Mapping[str, str]]] = [
        (".env", base),
        (env_file.name, read_file(env_file)),
        (".env.local", read_file(config_dir / ".env.local")),
    ]
    values: dict[str, str] = {}
    sources: dict[str, str] = {}
    for name, layer in layers:
        for key, value in layer.items():
            values[key] = value
            sources[key] = name
    # 系统环境变量最后上，永远赢。只看「文件里出现过的」和「程序认识的」名字：
    # os.environ 里还有 PATH、USERNAME 等几百个和本程序无关的变量，不要全搬进来
    for key in sorted(set(values) | set(KNOWN_KEYS)):
        if key in environ:
            values[key] = environ[key]
            sources[key] = SYSTEM
    values["APP_ENV"] = env
    if sources.get("APP_ENV") is None:
        sources["APP_ENV"] = "默认值"
    return env, values, sources


def load_for(config_dir: Path, environ: Mapping[str, str]) -> tuple[str, Settings]:
    env, values, sources = merge_layers(config_dir, environ)
    settings = load_settings(values)
    if env == "production" and settings.debug:
        source = sources.get("DEBUG", SYSTEM)
        raise ConfigError(f"生产环境不能开 DEBUG（DEBUG 来自 {source}）")
    return env, settings
