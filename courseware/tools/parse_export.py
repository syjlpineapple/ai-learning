"""ChatGPT 官方数据导出（conversations.json）解析工具。

用途：把 ChatGPT 的对话导出还原成可读的 Markdown，作为课件的原始素材。

为什么需要专门的脚本：导出文件里每个会话不是一个消息列表，而是一棵消息树
（`mapping` 字段，节点之间用 parent/children 相连）。每次编辑提问或点"重新生成"，
旧的回答会作为另一条分支留在树里。`current_node` 指向你最后实际看到的那个叶子节点，
因此只有从 `current_node` 沿 parent 一路回溯，才能还原出"你眼里的那次对话"。
如果直接遍历 mapping 的所有节点，被你抛弃的分支也会混进来。

两种模式：

    # 1. 先体检：列出所有会话、消息数、时间、内容类型分布，不写任何文件
    python courseware/tools/parse_export.py inspect courseware/_raw/导出包.zip

    # 2. 再提取：按标题关键字筛选，输出 Markdown
    python courseware/tools/parse_export.py extract courseware/_raw/导出包.zip \
        --out courseware/_raw/markdown --filter NLP --filter Python

输入可以直接是官方下载的 .zip，也可以是解压后的 conversations.json 或其所在目录。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

# ---------------------------------------------------------------------------
# 读取：兼容 zip / json 文件 / 目录
# ---------------------------------------------------------------------------

TARGET_NAME = "conversations.json"


def load_conversations(src: Path) -> list[dict[str, Any]]:
    """从 zip、json 文件或目录中读出会话列表。"""
    if not src.exists():
        raise FileNotFoundError(f"路径不存在：{src}")

    if src.is_dir():
        candidate = src / TARGET_NAME
        if not candidate.exists():
            raise FileNotFoundError(f"目录下没有找到 {TARGET_NAME}：{src}")
        raw = candidate.read_text(encoding="utf-8")
    elif src.suffix.lower() == ".zip":
        with zipfile.ZipFile(src) as zf:
            names = [n for n in zf.namelist() if n.endswith(TARGET_NAME)]
            if not names:
                raise FileNotFoundError(f"zip 包里没有找到 {TARGET_NAME}：{src}")
            # 取路径最短的那个，避免命中嵌套备份
            name = min(names, key=len)
            raw = zf.read(name).decode("utf-8")
    else:
        raw = src.read_text(encoding="utf-8")

    data = json.loads(raw)

    # 顶层通常是数组；个别导出工具会包一层 dict
    if isinstance(data, dict):
        for key in ("conversations", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]
        # 单个会话直接导出的情况
        if "mapping" in data:
            return [data]
        raise ValueError("无法识别的 JSON 结构：顶层是 dict 但找不到会话数组")
    if not isinstance(data, list):
        raise ValueError(f"无法识别的 JSON 结构：顶层是 {type(data).__name__}")
    return data


# ---------------------------------------------------------------------------
# 还原线性对话
# ---------------------------------------------------------------------------


def linearize(conv: dict[str, Any]) -> list[dict[str, Any]]:
    """从 current_node 沿 parent 回溯，还原用户实际看到的那条对话路径。

    返回的是 mapping 里的节点 dict 列表，顺序为从早到晚。
    """
    mapping = conv.get("mapping") or {}
    if not mapping:
        return []

    node_id = conv.get("current_node")

    # 没有 current_node（旧格式或单分支）时，退化为从根节点一路取第一个子节点
    if not node_id or node_id not in mapping:
        roots = [nid for nid, node in mapping.items() if not node.get("parent")]
        if not roots:
            return list(mapping.values())
        chain: list[dict[str, Any]] = []
        cursor: str | None = roots[0]
        seen: set[str] = set()
        while cursor and cursor in mapping and cursor not in seen:
            seen.add(cursor)
            node = mapping[cursor]
            chain.append(node)
            children = node.get("children") or []
            cursor = children[-1] if children else None
        return chain

    chain = []
    seen = set()
    cursor = node_id
    while cursor and cursor in mapping and cursor not in seen:
        seen.add(cursor)
        node = mapping[cursor]
        chain.append(node)
        cursor = node.get("parent")
    chain.reverse()
    return chain


def count_branches(conv: dict[str, Any]) -> int:
    """统计被抛弃的分支节点数，用于体检时提示有多少内容没被提取。"""
    mapping = conv.get("mapping") or {}
    kept = {id(node) for node in linearize(conv)}
    return sum(1 for node in mapping.values() if id(node) not in kept)


# ---------------------------------------------------------------------------
# 渲染消息内容
# ---------------------------------------------------------------------------


def render_part(part: Any) -> str:
    """content.parts 的单个元素可能是字符串，也可能是图片等结构体。"""
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        kind = part.get("content_type") or part.get("type") or "unknown"
        if kind == "image_asset_pointer":
            pointer = part.get("asset_pointer", "")
            width = part.get("width")
            height = part.get("height")
            size = f" {width}x{height}" if width and height else ""
            return f"[图片{size}：{pointer}]"
        if kind == "audio_transcription" and part.get("text"):
            return f"[语音转写]{part['text']}"
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            return text
        return f"[{kind}]"
    return str(part)


# ---------------------------------------------------------------------------
# 清理：把 ChatGPT 页面特有的写法转成通用 Markdown
# ---------------------------------------------------------------------------

# ChatGPT 的交互式图示组件，课件里渲染不出来，但类型名说明了讲的是什么，转成提示保留
VIZ_LABEL = {
    "DERIVATIVE_AS_SECANT": "导数与切线斜率（割线逼近）",
    "BAYES_THEOREM": "贝叶斯定理",
    "CLASSIFICATION_THRESHOLD": "分类阈值对预测结果的影响",
    "MATRIX_MULTIPLICATION_ROW_COLUMN_RULE": "矩阵乘法的行列规则",
}

VIZ_RE = re.compile(r"<LearningViz\s+type_id=\"([A-Z_]+)\"[^>]*?/>")

# ChatGPT 回复里混着大量页面组件标签（box/text/radio/math…，全部约 8000 个）。
# 不能统一删除：<math> 里是公式，<radio> 里是选择题的选项，删了内容就毁了。
# 所以按「有没有内容价值」分四类处理。
# 注意：<class 'str'>、<module> 这类出现在代码块和 traceback 里，是正文，
# 由 clean_markdown 跳过代码块来保护，并且不列入下面任何规则。

# 第一类：整块丢弃。SVG 是图形，button 的 onClick 里是预设提问的 JS，对课件无用
SVG_BLOCK_RE = re.compile(r"<svg\b[\s\S]*?</svg>", re.IGNORECASE)
BUTTON_BLOCK_RE = re.compile(r"<button\b[\s\S]*?</button>", re.IGNORECASE)

# 第二类：带内容，必须转成 Markdown 保留
MATH_BLOCK_RE = re.compile(r"<math\s+block\s+value=\"([^\"]*)\"\s*/?>")
MATH_INLINE_RE = re.compile(r"<math\s+value=\"([^\"]*)\"\s*/?>")
CHOICE_RE = re.compile(r"<(radio|checkbox)\b[^>]*>([\s\S]*?)</\1>")
TITLE_RE = re.compile(r"<title\b[^>]*>([\s\S]*?)</title>")
BADGE_RE = re.compile(r"<badge\b[^>]*>([\s\S]*?)</badge>")

# 第三类：纯装饰的自闭合标签，直接删
VOID_TAG_RE = re.compile(
    r"<(?:divider|icon|spacer|input|slider|radio|checkbox|button|math|line|marker|defs|path|circle|rect)\b[^>]*/?>",
    re.IGNORECASE,
)

# 第四类：只做布局的容器，去掉标签本身、保留里面的内容
SHELL_TAG_RE = re.compile(r"</?(?:box|row|col|grid|text|caption|label|list|list_item)\b[^>]*>")

# ---------------------------------------------------------------------------
# 大写驼峰的组件标签，单独一组规则
# ---------------------------------------------------------------------------

# CodeBlock 里是裸代码（没有围栏），要补上围栏
CODEBLOCK_RE = re.compile(r"<CodeBlock\b([^>]*)>([\s\S]*?)</CodeBlock>")
# WritingBlock 里面已经有 ``` 围栏，只去壳
WRITINGBLOCK_RE = re.compile(r"<WritingBlock\b[^>]*>([\s\S]*?)</WritingBlock>")
LANG_ATTR_RE = re.compile(r"language=\"([^\"]*)\"")

# Link 带着真实 URL，转成 Markdown 链接保留
LINK_RE = re.compile(r"<Link\s+url=\"([^\"]*)\"\s+title=\"([^\"]*)\"\s*/>")
# Graph 的 latex 是函数表达式，有教学价值
GRAPH_RE = re.compile(r"<Graph\s+expressions=\{\[([\s\S]*?)\]\}[^>]*/>")
LATEX_ATTR_RE = re.compile(r"\"latex\"\s*:\s*\"([^\"]*)\"")
# Chart 的 meta 里有标题和说明，数据点通常正文也讲了，保留标题即可
CHART_RE = re.compile(r"<Chart\s+content=\{\{([\s\S]*?)\}\}\s*/>")
CHART_TITLE_RE = re.compile(r"\"title\"\s*:\s*\"([^\"]*)\"")
CHART_DESC_RE = re.compile(r"\"description\"\s*:\s*\"([^\"]*)\"")

# 纯装饰：AI 生成的配图、引用角标、定时任务建议，对课件没有信息量
DECOR_COMPONENT_RE = re.compile(
    r"<(?:AsyncImage|AsyncImageGroup|Cite|SuggestAutomation|Chart|Graph|Link)\b[^>]*/?>"
)


def _replace_codeblock(match: re.Match[str]) -> str:
    attrs, code = match.group(1), match.group(2)
    lang_match = LANG_ATTR_RE.search(attrs)
    lang = lang_match.group(1) if lang_match else ""
    return f"\n```{lang}\n{code.strip()}\n```\n"


def _replace_graph(match: re.Match[str]) -> str:
    formulas = LATEX_ATTR_RE.findall(match.group(1))
    if not formulas:
        return ""
    joined = "、".join(f"${f}$" for f in formulas)
    return f"> 📈 原对话此处有函数图像：{joined}"


def _replace_chart(match: re.Match[str]) -> str:
    body = match.group(1)
    title_match = CHART_TITLE_RE.search(body)
    desc_match = CHART_DESC_RE.search(body)
    parts = [p.group(1) for p in (title_match, desc_match) if p]
    if not parts:
        return ""
    return "> 📈 原对话此处有图表：" + " —— ".join(parts)

# ChatGPT 的交互式组件还带一套 Svelte 风格的模板语法。
# 区别对待：{@body const questions = [...]} 里是题库数据（题目、选项、答案、解析），
# 这是课件的素材，必须保留；{#each}{/each}{#if}{/if} 和 setState 回调是纯控制流，删掉。
TEMPLATE_BODY_RE = re.compile(r"\{@body\s+")
TEMPLATE_FLOW_RE = re.compile(r"^[ \t]*\{[#/](?:each|if)[^\n]*$", re.MULTILINE)
TEMPLATE_CALLBACK_RE = re.compile(r"^[ \t]*-?[ \t]*set[A-Z][A-Za-z]*\([^\n]*$", re.MULTILINE)
# 组件的状态声明，和题库数据的区别是它用解构赋值：const [x, setX] = DIL.useState(...)
TEMPLATE_STATE_RE = re.compile(
    r"^[ \t]*const\s*\[[^\]]*\]\s*=\s*DIL\.useState\([^\n]*$", re.MULTILINE
)
# 带连字符的组件标签（radio-group 等），上面的规则匹配不到
HYPHEN_TAG_RE = re.compile(r"</?[a-z]+(?:-[a-z]+)+\b[^>]*>")

# 去壳后会留下一堆只含空格的行，先清空再压缩连续空行。
# 注意不动内容行的行首缩进：那会破坏 Markdown 的嵌套列表层级。
WHITESPACE_LINE_RE = re.compile(r"^[ \t]+$", re.MULTILINE)
BLANK_LINES_RE = re.compile(r"\n{3,}")
# 形如「思考了 32s」「思考了 1m 16s」，纯耗时没有信息量
THINKING_ONLY_RE = re.compile(r"^思考了\s*(?:\d+\s*[hms]\s*)+$")
CODE_FENCE_RE = re.compile(r"(```.*?```)", re.DOTALL)


def _replace_viz(match: re.Match[str]) -> str:
    type_id = match.group(1)
    label = VIZ_LABEL.get(type_id, type_id)
    return f"> 📊 原对话此处有一个交互式图示：**{label}**"


def clean_markdown(text: str) -> str:
    """把 ChatGPT 的页面专用写法转成通用 Markdown。

    只处理代码块之外的内容：代码里出现的反斜杠和括号必须原样保留，
    否则会把 Python 的正则、路径写法改坏。
    """
    if not text:
        return text

    # 必须先做这两步：CodeBlock 里是裸代码、WritingBlock 里是带围栏的代码，
    # 如果先按 ``` 分割，这两个标签会被切成两半，后面就匹配不上了。
    text = CODEBLOCK_RE.sub(_replace_codeblock, text)
    text = WRITINGBLOCK_RE.sub(lambda m: m.group(1), text)

    out = []
    # 用捕获组分割，奇数段就是代码块本身，原样放回
    for i, segment in enumerate(CODE_FENCE_RE.split(text)):
        if i % 2 == 1:
            out.append(segment)
            continue
        segment = VIZ_RE.sub(_replace_viz, segment)

        # 大写驼峰组件：先抽出有价值的内容，再删掉纯装饰的
        segment = LINK_RE.sub(lambda m: f"[{m.group(2)}]({m.group(1)})", segment)
        segment = GRAPH_RE.sub(_replace_graph, segment)
        segment = CHART_RE.sub(_replace_chart, segment)
        segment = DECOR_COMPONENT_RE.sub("", segment)

        # 整块丢弃
        segment = SVG_BLOCK_RE.sub("", segment)
        segment = BUTTON_BLOCK_RE.sub("", segment)
        # 带内容的，转成 Markdown
        segment = MATH_BLOCK_RE.sub(lambda m: f"\n$$\n{m.group(1)}\n$$\n", segment)
        segment = MATH_INLINE_RE.sub(lambda m: f"${m.group(1)}$", segment)
        segment = CHOICE_RE.sub(lambda m: f"- {m.group(2).strip()}", segment)
        segment = TITLE_RE.sub(lambda m: f"**{m.group(1).strip()}**", segment)
        segment = BADGE_RE.sub(lambda m: f"**{m.group(1).strip()}**", segment)
        # 装饰与布局
        segment = VOID_TAG_RE.sub("", segment)
        segment = SHELL_TAG_RE.sub("", segment)
        segment = HYPHEN_TAG_RE.sub("", segment)
        # 模板语法：去掉 {@body 前缀但留下里面的题库数据，删掉控制流和回调
        segment = TEMPLATE_FLOW_RE.sub("", segment)
        segment = TEMPLATE_CALLBACK_RE.sub("", segment)
        segment = TEMPLATE_BODY_RE.sub("", segment)
        segment = TEMPLATE_STATE_RE.sub("", segment)
        segment = WHITESPACE_LINE_RE.sub("", segment)
        segment = BLANK_LINES_RE.sub("\n\n", segment)
        # 行间公式 \[ ... \] -> $$ ... $$
        segment = re.sub(
            r"\\\[\s*(.+?)\s*\\\]", lambda m: f"\n$$\n{m.group(1)}\n$$\n", segment, flags=re.DOTALL
        )
        # 行内公式 \( ... \) -> $ ... $
        segment = re.sub(r"\\\(\s*(.+?)\s*\\\)", lambda m: f"${m.group(1)}$", segment, flags=re.DOTALL)
        out.append(segment)
    return "".join(out)


def render_content(message: dict[str, Any]) -> str:
    """渲染一条 message，并清理成通用 Markdown。"""
    return clean_markdown(_render_raw(message))


def _render_raw(message: dict[str, Any]) -> str:
    """把一条 message 的 content 渲染成 Markdown 文本。"""
    content = message.get("content") or {}
    if not isinstance(content, dict):
        return str(content)

    ctype = content.get("content_type", "text")

    if ctype in ("text", "multimodal_text"):
        parts = content.get("parts") or []
        return "\n\n".join(p for p in (render_part(x) for x in parts) if p.strip())

    if ctype == "code":
        code = content.get("text") or ""
        lang = content.get("language") or ""
        if not code.strip():
            return ""
        return f"```{lang}\n{code}\n```"

    if ctype == "execution_output":
        out = content.get("text") or ""
        return f"```text\n{out}\n```" if out.strip() else ""

    if ctype == "thoughts":
        chunks = []
        for item in content.get("thoughts") or []:
            if not isinstance(item, dict):
                continue
            summary = (item.get("summary") or "").strip()
            body = (item.get("content") or "").strip()
            if summary:
                chunks.append(f"**{summary}**")
            if body:
                chunks.append(body)
        return "\n\n".join(chunks)

    if ctype == "reasoning_recap":
        recap = (content.get("content") or "").strip()
        # 绝大多数只是「思考了 32s」这种耗时，对课件没用；有实质内容的保留
        return "" if THINKING_ONLY_RE.match(recap) else recap

    if ctype == "tether_quote":
        title = content.get("title") or ""
        text = content.get("text") or ""
        url = content.get("url") or ""
        head = f"> 引用：{title} {url}".strip()
        return f"{head}\n>\n> {text}" if text.strip() else head

    if ctype == "tether_browsing_display":
        return (content.get("result") or "").strip()

    # 兜底：尽力找出可读字段，而不是静默丢弃
    for key in ("text", "result", "content"):
        value = content.get(key)
        if isinstance(value, str) and value.strip():
            return value
    parts = content.get("parts")
    if isinstance(parts, list):
        rendered = "\n\n".join(p for p in (render_part(x) for x in parts) if p.strip())
        if rendered:
            return rendered
    return ""


ROLE_LABEL = {
    "user": "我",
    "assistant": "ChatGPT",
    "system": "系统",
    "tool": "工具",
}


def is_visible(node: dict[str, Any], keep_tools: bool) -> bool:
    """判断一个节点是否应该出现在课件里。"""
    message = node.get("message")
    if not isinstance(message, dict):
        return False  # 根节点没有 message

    meta = message.get("metadata") or {}
    if meta.get("is_visually_hidden_from_conversation"):
        return False

    role = ((message.get("author") or {}).get("role")) or ""
    if role == "system":
        return False
    if role == "tool" and not keep_tools:
        return False

    # recipient 不是 all 的 assistant 消息是发给工具的指令，不是给人看的回答
    if role == "assistant" and message.get("recipient") not in (None, "all") and not keep_tools:
        return False

    return bool(render_content(message).strip())


def fmt_time(ts: Any) -> str:
    if not isinstance(ts, (int, float)) or ts <= 0:
        return ""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (OSError, OverflowError, ValueError):
        return ""


# ---------------------------------------------------------------------------
# 模式一：体检
# ---------------------------------------------------------------------------


def cmd_inspect(args: argparse.Namespace) -> int:
    convs = load_conversations(Path(args.src))
    print(f"会话总数：{len(convs)}\n")

    rows = []
    for i, conv in enumerate(convs):
        chain = linearize(conv)
        visible = [n for n in chain if is_visible(n, keep_tools=False)]
        chars = sum(len(render_content(n["message"])) for n in visible)
        rows.append(
            {
                "index": i,
                "title": conv.get("title") or "(无标题)",
                "created": fmt_time(conv.get("create_time")),
                "updated": fmt_time(conv.get("update_time")),
                "nodes": len(conv.get("mapping") or {}),
                "path": len(chain),
                "visible": len(visible),
                "dropped": count_branches(conv),
                "chars": chars,
            }
        )

    rows.sort(key=lambda r: r["created"] or "")

    header = f"{'#':>4}  {'创建时间':<17} {'消息':>5} {'弃支':>5} {'字数':>8}  标题"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(
            f"{r['index']:>4}  {r['created']:<17} {r['visible']:>5} "
            f"{r['dropped']:>5} {r['chars']:>8}  {r['title']}"
        )

    total_chars = sum(r["chars"] for r in rows)
    print(f"\n可见消息合计 {sum(r['visible'] for r in rows)} 条，约 {total_chars:,} 字。")

    # 内容类型分布：用来发现脚本还没处理的新格式
    types: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    unhandled: Counter[str] = Counter()
    for conv in convs:
        for node in linearize(conv):
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            ctype = ((message.get("content") or {}) or {}).get("content_type", "?")
            types[str(ctype)] += 1
            roles[str((message.get("author") or {}).get("role"))] += 1
            if not render_content(message).strip():
                unhandled[str(ctype)] += 1

    print("\n角色分布：", dict(roles))
    print("内容类型分布：", dict(types))
    if unhandled:
        print("渲染为空的类型（多为纯工具调用，若包含 text 请告知）：", dict(unhandled))
    return 0


# ---------------------------------------------------------------------------
# 模式二：提取
# ---------------------------------------------------------------------------

ILLEGAL = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def safe_name(title: str, index: int) -> str:
    name = ILLEGAL.sub("_", title).strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    if not name:
        name = "untitled"
    return f"{index:02d}_{name[:60]}"


def iter_selected(
    convs: list[dict[str, Any]], filters: list[str], indexes: list[int]
) -> Iterator[tuple[int, dict[str, Any]]]:
    for i, conv in enumerate(convs):
        if indexes and i not in indexes:
            continue
        if filters:
            title = (conv.get("title") or "").lower()
            if not any(f.lower() in title for f in filters):
                continue
        yield i, conv


def to_markdown(conv: dict[str, Any], keep_tools: bool) -> str:
    title = conv.get("title") or "(无标题)"
    lines = [f"# {title}", ""]

    created = fmt_time(conv.get("create_time"))
    updated = fmt_time(conv.get("update_time"))
    if created or updated:
        lines.append(f"> 创建：{created or '未知'}　最后更新：{updated or '未知'}")
        lines.append("")

    for node in linearize(conv):
        if not is_visible(node, keep_tools):
            continue
        message = node["message"]
        role = (message.get("author") or {}).get("role") or "?"
        label = ROLE_LABEL.get(role, role)
        stamp = fmt_time(message.get("create_time"))
        head = f"## {label}" + (f"　`{stamp}`" if stamp else "")
        lines.extend(["---", "", head, "", render_content(message).strip(), ""])

    return "\n".join(lines).rstrip() + "\n"


def summarize(text: str, limit: int = 80) -> str:
    """把一条提问压成一行摘要，用于课时地图。"""
    # 去掉代码块，否则摘要全是代码
    body = CODE_FENCE_RE.sub(" 「代码」 ", text)
    body = re.sub(r"`[^`]*`", lambda m: m.group(0).strip("`"), body)
    body = re.sub(r"[#>*_\-]+", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    if len(body) <= limit:
        return body
    return body[:limit] + "…"


def cmd_outline(args: argparse.Namespace) -> int:
    """把所有提问按日期聚合，输出课时地图。"""
    convs = load_conversations(Path(args.src))

    # (日期, 时刻, 会话标题, 摘要, 这条回答的字数)
    rows: list[tuple[str, str, str, str, int]] = []
    for conv in convs:
        title = conv.get("title") or "(无标题)"
        chain = [n for n in linearize(conv) if is_visible(n, keep_tools=False)]
        for i, node in enumerate(chain):
            message = node["message"]
            if ((message.get("author") or {}).get("role")) != "user":
                continue
            stamp = fmt_time(message.get("create_time"))
            if not stamp:
                continue
            # 这一问之后、下一问之前的回答总字数，用来衡量这个知识点讲了多少
            answer_chars = 0
            for later in chain[i + 1 :]:
                later_msg = later["message"]
                if ((later_msg.get("author") or {}).get("role")) == "user":
                    break
                answer_chars += len(render_content(later_msg))
            date, clock = stamp.split(" ")
            rows.append((date, clock, title.strip(), summarize(render_content(message)), answer_chars))

    rows.sort(key=lambda r: (r[0], r[1]))

    lines = [
        "# 课时地图",
        "",
        f"共 {len(rows)} 条提问，按日期聚合。「答」为该问之后 ChatGPT 回答的字数，",
        "数字越大说明这个知识点讲得越深，适合作为课件的一节。",
        "",
    ]
    current_date = ""
    for date, clock, title, summary, answer_chars in rows:
        if date != current_date:
            current_date = date
            same_day = [r for r in rows if r[0] == date]
            day_titles = sorted({r[2] for r in same_day})
            lines.append("")
            lines.append(f"## {date}　（{len(same_day)} 问，来源：{'、'.join(day_titles)}）")
            lines.append("")
        lines.append(f"- `{clock}` 〔答 {answer_chars:,}〕 {summary}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    days = len({r[0] for r in rows})
    print(f"共 {len(rows)} 条提问，跨 {days} 天，已写入 {out}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    convs = load_conversations(Path(args.src))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = list(iter_selected(convs, args.filter or [], args.index or []))
    if not selected:
        print("没有匹配到任何会话。先跑 inspect 看看标题和序号。", file=sys.stderr)
        return 1

    # 按创建时间排序，让输出文件名的序号就是学习顺序
    selected.sort(key=lambda pair: pair[1].get("create_time") or 0)

    index_lines = ["# 原始对话索引", ""]
    for order, (i, conv) in enumerate(selected, start=1):
        md = to_markdown(conv, keep_tools=args.keep_tools)
        path = out_dir / f"{safe_name(conv.get('title') or '', order)}.md"
        path.write_text(md, encoding="utf-8")
        created = fmt_time(conv.get("create_time")) or "未知"
        print(f"[{order:02d}] {path.name}  ({len(md):,} 字, 原序号 {i}, {created})")
        index_lines.append(f"{order}. [{conv.get('title') or '(无标题)'}]({path.name}) — {created}")

    (out_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"\n共导出 {len(selected)} 个会话到 {out_dir}，索引见 INDEX.md")
    return 0


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="解析 ChatGPT 官方导出的 conversations.json",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_inspect = sub.add_parser("inspect", help="体检：列出所有会话概况，不写文件")
    p_inspect.add_argument("src", help="导出的 .zip / conversations.json / 解压目录")
    p_inspect.set_defaults(func=cmd_inspect)

    p_outline = sub.add_parser("outline", help="把所有提问按日期聚合成课时地图")
    p_outline.add_argument("src", help="导出的 .zip / conversations.json / 解压目录")
    p_outline.add_argument("--out", required=True, help="输出的 Markdown 文件路径")
    p_outline.set_defaults(func=cmd_outline)

    p_extract = sub.add_parser("extract", help="提取为 Markdown")
    p_extract.add_argument("src", help="导出的 .zip / conversations.json / 解压目录")
    p_extract.add_argument("--out", required=True, help="输出目录")
    p_extract.add_argument(
        "--filter",
        action="append",
        help="按标题关键字筛选，可多次传入（如 --filter NLP --filter Python）",
    )
    p_extract.add_argument(
        "--index",
        action="append",
        type=int,
        help="按 inspect 给出的序号筛选，可多次传入",
    )
    p_extract.add_argument(
        "--keep-tools",
        action="store_true",
        help="保留工具调用消息（默认丢弃，课件一般不需要）",
    )
    p_extract.set_defaults(func=cmd_extract)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
