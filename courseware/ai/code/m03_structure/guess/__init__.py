"""第 3.3 章 · 按职责拆分后的猜数字。

    errors.py    异常类型（最底层，谁都可以导入它）
    rules.py     游戏规则：解析输入、判断大小、管理一局的状态。不碰 input/print
    cli.py       命令行交互：问、说、把输入交给规则。不写规则
    __main__.py  入口：python -m m03_structure.guess 时执行，只负责把上面几样组装起来

依赖方向只能从上往下：__main__ → cli → rules → errors。

这个文件刻意保持为空（除了这段说明）。包的 __init__.py 会在导入任何子模块时先执行（第 3.1 章第 1 节）：
    在这里导入 __main__  → python -m m03_structure.guess 时它执行两次，并给出 RuntimeWarning（第 3.1 章第 7 节）
    在这里导入 cli       → 只想用 rules 的人，也会连带加载交互层
"""
