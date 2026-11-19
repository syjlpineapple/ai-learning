"""第 14 题 · 用 Mock 测 APIClient。

这一题是你写测试。在这个文件里写 test_ 开头的函数，测第 12 题的 APIClient，然后：

    pytest tests/test_m08.py -k p14 -v

评测会做两件事：
    1. 用正确的 APIClient 跑你的测试：必须全部通过
    2. 换成 8 个故意写错的版本，各跑一遍：每一个都必须让你的测试失败

规则：不能发真实的网络请求（评测会把网络断掉），也不能开第 5 题的本机服务。

要测的行为（每一条对应一个写错的版本）：
    1. 每个请求都带上 settings.timeout
    2. 状态码 500 时 get_scores 抛 requests.exceptions.HTTPError
    3. 请求的 URL 是 base_url + "/" + endpoint，没有 //（base_url 可以带 /api 这样的路径）
    4. 请求头里有 Authorization: Bearer <api_key>
    5. upload 发的是 JSON（json=），不是表单
    6. upload 第一次超时、第二次成功时，两次请求带的 Idempotency-Key 是同一个
    7. retries=2 时，一直失败的话一共请求 3 次
    8. with 块里出了异常，异常照样抛出来

用得上的东西：
    from unittest.mock import MagicMock
    from m08_testing.p14_target import APIClient, fake_response
    from m06_config.p10_settings_solution import Settings

    APIClient(settings, session=..., sleep=...)   第 12 题留的两个口子：传一个假的 Session、
                                                   一个不真的等待的 sleep
    fake_response(500, {"error": "x"})            造一个真的 requests.Response
"""

from __future__ import annotations

# TODO：在下面写你的测试
