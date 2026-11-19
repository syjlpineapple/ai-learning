"""M8 · 测试进阶（每日一题）。

p14  用 Mock 测 APIClient：不开服务、不联网；你写测试，评测用「故意写错的版本」检查测试有没有用
p15  装饰器：把第 8 题的重试做成 @retrying，再写一个 @logged；functools.wraps、叠放顺序
p16  给测试搭环境：你写 fixture（共用一个服务、每个测试前重置、monkeypatch、yield 清理），
     评测用它们跑 _p16_consumer_a.py、_p16_consumer_b.py
"""
