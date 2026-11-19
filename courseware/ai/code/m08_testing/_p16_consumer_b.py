"""第 16 题的评测：用你写的 fixture 的测试（第二个文件）。不要改这个文件。"""

from __future__ import annotations

from m05_http.server import Running
from m08_testing import _p16_record as record


def test_another_file(server: Running) -> None:
    record.urls.append(server.base_url)


def test_one_server_for_all() -> None:
    """要求 1：两个文件里的测试，用的都是同一个服务。"""
    assert len(record.urls) == 3
    count = len(set(record.urls))
    assert count == 1, (
        f"要求 1：3 个测试一共开了 {count} 个服务。scope 默认是 function，每个测试一个；"
        "module 是每个文件一个；整个测试运行只开一个要用 session")
