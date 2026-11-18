"""命令行交互：只管问和说。

规则判断全部交给 rules；这里出现的每一个 if，都是关于「怎么跟人说话」的。
ask / say 通过参数传进来（第 1.6 章的依赖注入），测试时不需要真的键盘和屏幕。
"""

from __future__ import annotations

from collections.abc import Callable

from m03_structure.guess.errors import GuessError
from m03_structure.guess.rules import GuessGame, parse_guess


def play(game: GuessGame, ask: Callable[[str], str] = input,
         say: Callable[[str], None] = print) -> GuessGame:
    say(f"我想好了一个 {game.low}-{game.high} 之间的数，你有 {game.max_attempts} 次机会。")
    while not game.is_over:
        raw = ask(f"[{len(game.history) + 1}/{game.max_attempts}] 你猜（q 退出）： ")
        if raw.strip() == "q":
            say("不玩了。")
            break
        try:
            n = parse_guess(raw, game.low, game.high)
        except GuessError as e:
            say(f"   {e}，这次不算")
            continue
        say(f"   {n:>3} → {game.guess(n)}")
    if game.won:
        say(f"   用了 {len(game.history)} 次。")
    elif game.remaining == 0:
        say(f"   机会用完了，答案是 {game.target}。")
    return game
