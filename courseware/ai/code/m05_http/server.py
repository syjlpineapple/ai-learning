"""本机的「排行榜服务」。M5 的题目和测试都调用它，不需要联网。

自己开一个玩：

    python -m m05_http.server              # 默认 http://127.0.0.1:8765
    python -m m05_http.server 9000         # 换个端口

然后在浏览器或另一个终端里访问：

    http://127.0.0.1:8765/scores
    http://127.0.0.1:8765/scores?player=张三&limit=2
    http://127.0.0.1:8765/echo?a=1

接口
    GET  /scores?player=&limit=     成绩列表（JSON 数组），按次数从少到多。limit 默认 10，范围 1-50
    POST /scores                    上传一条成绩，请求体是 JSON {"player": ..., "attempts": ...}，
                                    成功返回 201。带 Idempotency-Key 头时，同一个 key 只会存一次
    GET  /echo                      原样告诉你服务端收到了什么：方法、查询参数、请求头、请求体
    POST /echo                      同上
    GET  /slow?seconds=             等这么多秒再回答
    GET  /trickle?seconds=          一点一点地回答：每 0.5 秒发一个字节，持续这么多秒
    GET  /status/<code>             返回这个状态码，正文是 JSON {"error": ...}
    GET  /html                      200，但正文是 HTML
    其他路径                         404，正文是 HTML（很多真实服务器就是这样）

测试里用 running_server() 开一个随机端口的服务，用完自动关掉。
"""

from __future__ import annotations

import json
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

SEED_SCORES: list[dict[str, object]] = [
    {"player": "张三", "attempts": 5},
    {"player": "李四", "attempts": 3},
    {"player": "张三", "attempts": 2},
    {"player": "欧阳修文", "attempts": 6},
    {"player": "A&B", "attempts": 4},
    {"player": "C#", "attempts": 7},
    {"player": "100%", "attempts": 1},
]

NOT_FOUND_PAGE = b"<html><head><title>404 Not Found</title></head><body>Not Found</body></html>"


@dataclass
class ServerState:
    """服务的可调状态。测试通过它让 /scores 变慢、出错。"""

    scores: list[dict[str, object]] = field(default_factory=lambda: list(SEED_SCORES))
    scores_delay: float = 0.0          # /scores 回答前先等几秒
    scores_status: int = 200           # /scores 返回的状态码；不是 200 时正文是 {"error": ...}
    scores_override: object = None     # 不为 None 时，/scores 直接返回 200 和这个对象
    # GET /scores 的「失败计划」：每来一个请求就用掉一项，用完了才正常回答。
    #   503、429 这类数字 → 返回这个状态码；"slow" → 拖 2 秒再正常回答（让客户端超时）
    fail_plan: list[int | str] = field(default_factory=list)
    retry_after: str | None = None     # 返回 429 时带上的 Retry-After 头
    # 接下来的几次 POST /scores：成绩照常存好，但拖 2 秒才回答（让客户端以为超时失败了）
    slow_posts: int = 0
    seen_keys: dict[str, dict[str, object]] = field(default_factory=dict)  # Idempotency-Key → 那次的结果
    requests_seen: int = 0
    scores_gets: int = 0               # GET /scores 一共来了几次（测试用来数重试次数）
    # 不为 None 时，/scores 要求请求头 Authorization: Bearer <api_key>，否则返回 401
    api_key: str | None = None
    # 每个请求来自哪个客户端端口。同一个端口 = 同一条 TCP 连接
    client_ports: list[int] = field(default_factory=list)


class Handler(BaseHTTPRequestHandler):
    server: _Server
    # HTTP/1.1 才支持一条连接上连续发多个请求（keep-alive），第 12 题要看 Session 有没有复用连接。
    # 默认的 HTTP/1.0 每回答一次就断开连接
    protocol_version = "HTTP/1.1"

    # ---- 工具 ---------------------------------------------------------------

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass   # 不往终端打访问日志，免得干扰测试输出

    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    # ---- 路由 ---------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        self.route("GET")

    def do_POST(self) -> None:  # noqa: N802
        self.route("POST")

    def route(self, method: str) -> None:
        state = self.server.state
        state.requests_seen += 1
        state.client_ports.append(self.client_address[1])
        parts = urlsplit(self.path)
        if parts.path == "/scores" and state.api_key is not None \
                and self.headers.get("Authorization") != f"Bearer {state.api_key}":
            self.read_body()
            self.send_error_json(401, "缺少或错误的 Authorization 头")
            return
        query = parse_qs(parts.query, keep_blank_values=True)
        path = parts.path

        if path == "/echo":
            body = self.read_body()
            self.send_json(200, {
                "method": method,
                "raw_query": parts.query,
                "query": query,
                "headers": dict(self.headers.items()),
                "body": body.decode("utf-8", errors="replace"),
            })
        elif path == "/scores" and method == "GET":
            self.get_scores(query)
        elif path == "/scores" and method == "POST":
            self.post_score()
        elif path == "/slow":
            time.sleep(float(query.get("seconds", ["1"])[0]))
            self.send_json(200, {"ok": True})
        elif path == "/trickle":
            self.trickle(float(query.get("seconds", ["2"])[0]))
        elif path.startswith("/status/"):
            code = int(path.removeprefix("/status/"))
            self.send_json(code, {"error": f"服务端按要求返回了 {code}"})
        elif path == "/html":
            self.send_html(200, b"<html><body>this is not json</body></html>")
        else:
            self.send_html(404, NOT_FOUND_PAGE)

    def send_error_json(self, status: int, message: str) -> None:
        body = json.dumps({"error": message}, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if status == 429 and self.server.state.retry_after is not None:
            self.send_header("Retry-After", self.server.state.retry_after)
        self.end_headers()
        self.wfile.write(body)

    def get_scores(self, query: dict[str, list[str]]) -> None:
        state = self.server.state
        state.scores_gets += 1
        if state.fail_plan:
            step = state.fail_plan.pop(0)
            if step == "slow":
                time.sleep(2)
            else:
                self.send_error_json(int(step), f"服务端按计划返回了 {step}")
                return
        if state.scores_delay:
            time.sleep(state.scores_delay)
        if state.scores_status != 200:
            self.send_json(state.scores_status, {"error": f"服务端出错（{state.scores_status}）"})
            return
        if state.scores_override is not None:
            self.send_json(200, state.scores_override)
            return
        try:
            limit = int(query.get("limit", ["10"])[0])
        except ValueError:
            self.send_json(400, {"error": "limit 必须是整数"})
            return
        if not 1 <= limit <= 50:
            self.send_json(400, {"error": "limit 必须在 1-50 之间"})
            return
        rows = state.scores
        if "player" in query:
            rows = [r for r in rows if r["player"] == query["player"][0]]
        rows = sorted(rows, key=lambda r: (int(str(r["attempts"])), str(r["player"])))
        self.send_json(200, rows[:limit])

    def post_score(self) -> None:
        """POST /scores：上传一条成绩。

        请求体必须是 JSON：{"player": 非空字符串, "attempts": 1-100 的整数}
        带了 Idempotency-Key 头、而且这个 key 之前用过时，不再新增，直接返回上次的结果。
        """
        state = self.server.state
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("application/json"):
            self.send_error_json(415, f"请求体必须是 JSON，收到的 Content-Type 是 {content_type!r}")
            return
        try:
            data = json.loads(self.read_body())
        except ValueError:
            self.send_error_json(400, "请求体不是合法的 JSON")
            return
        player, attempts = (data.get("player"), data.get("attempts")) \
            if isinstance(data, dict) else (None, None)
        if not (isinstance(player, str) and player.strip()):
            self.send_error_json(400, "player 必须是非空字符串")
            return
        if not (type(attempts) is int and 1 <= attempts <= 100):
            self.send_error_json(400, "attempts 必须是 1-100 的整数")
            return

        key = self.headers.get("Idempotency-Key")
        if key is not None and key in state.seen_keys:
            self.send_json(200, state.seen_keys[key])      # 重复提交：不新增，返回上次的结果
            return
        row: dict[str, object] = {"id": len(state.scores) + 1, "player": player,
                                  "attempts": attempts}
        state.scores.append({"player": player, "attempts": attempts})
        if key is not None:
            state.seen_keys[key] = row
        if state.slow_posts > 0:
            state.slow_posts -= 1
            time.sleep(2)                                    # 已经存好了，只是回答得慢
        self.send_json(201, row)

    def trickle(self, seconds: float) -> None:
        payload = b"[" + b" " * max(int(seconds / 0.5) - 2, 0) + b"]"
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        for byte in payload:
            self.wfile.write(bytes([byte]))
            self.wfile.flush()
            time.sleep(0.5)


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: ServerState) -> None:
        super().__init__(address, Handler)
        self.state = state

    def handle_error(self, request: object, client_address: object) -> None:
        # 客户端超时后会断开连接，服务端再写回应时就会 ConnectionAbortedError。
        # 这是测试故意制造的，不打印 traceback
        pass


@dataclass
class Running:
    base_url: str
    state: ServerState


@contextmanager
def running_server(port: int = 0) -> Iterator[Running]:
    """在后台线程里开一个服务。port=0 让系统挑一个空闲端口。"""
    state = ServerState()
    httpd = _Server(("127.0.0.1", port), state)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield Running(f"http://127.0.0.1:{httpd.server_address[1]}", state)
    finally:
        httpd.shutdown()
        httpd.server_close()


def main(argv: list[str]) -> None:
    port = int(argv[0]) if argv else 8765
    with running_server(port) as srv:
        print(f"排行榜服务已启动：{srv.base_url}/scores   （Ctrl+C 停止）")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print("已停止")


if __name__ == "__main__":
    main(sys.argv[1:])
