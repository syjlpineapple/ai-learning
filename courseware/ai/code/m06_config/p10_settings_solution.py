"""第 10 题 · 参考答案。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

TRUE_WORDS = {"true", "1", "yes", "on"}
FALSE_WORDS = {"false", "0", "no", "off"}


class ConfigError(ValueError):
    """配置不对。消息里列出所有问题，而不是只说第一个。"""


@dataclass(frozen=True)
class Settings:
    # repr=False：打印、记日志、拼进报错消息时都不会带出密钥
    api_key: str = field(repr=False)
    base_url: str
    timeout: float
    retries: int
    debug: bool


def load_settings(environ: Mapping[str, str]) -> Settings:
    problems: list[str] = []

    def get(name: str) -> str | None:
        # 「KEY=」这种空值也当成没设：os.getenv(name, 默认值) 遇到空字符串不会用默认值
        value = environ.get(name, "").strip()
        return value or None

    api_key = get("API_KEY")
    base_url = get("API_BASE_URL")
    missing = [name for name, value in (("API_KEY", api_key), ("API_BASE_URL", base_url))
               if value is None]
    if missing:
        problems.append(f"缺少 {', '.join(missing)}")
    if base_url is not None and not base_url.startswith(("http://", "https://")):
        problems.append(f"API_BASE_URL 要以 http:// 或 https:// 开头，实际是 {base_url!r}")

    timeout = 5.0
    raw = get("TIMEOUT")
    if raw is not None:
        try:
            timeout = float(raw)
        except ValueError:
            problems.append(f"TIMEOUT 必须是数字，实际是 {raw!r}")
        else:
            if not timeout > 0:          # 也挡住了 nan：nan > 0 是 False
                problems.append(f"TIMEOUT 必须大于 0，实际是 {raw!r}")

    retries = 3
    raw = get("RETRIES")
    if raw is not None:
        try:
            retries = int(raw)
        except ValueError:
            problems.append(f"RETRIES 必须是整数，实际是 {raw!r}")
        else:
            if not 0 <= retries <= 10:
                problems.append(f"RETRIES 必须在 0-10 之间，实际是 {raw!r}")

    debug = False
    raw = get("DEBUG")
    if raw is not None:
        word = raw.lower()
        if word in TRUE_WORDS:
            debug = True
        elif word not in FALSE_WORDS:
            # 认不出来就报错，而不是悄悄当成 False：DEBUG=ture 这种拼写错误要让人知道
            problems.append(f"DEBUG 只能是 true/false/1/0/yes/no/on/off，实际是 {raw!r}")

    # 后两个条件和 missing 是同一件事，写出来是让 mypy 知道下面它们一定不是 None
    if problems or api_key is None or base_url is None:
        # 注意这里一个密钥的值都没有用到，只说了「缺少 API_KEY」
        raise ConfigError(f"配置有 {len(problems)} 处问题：{'；'.join(problems)}")

    return Settings(api_key=api_key, base_url=base_url.rstrip("/"), timeout=timeout,
                    retries=retries, debug=debug)
