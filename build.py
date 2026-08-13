#!/usr/bin/env python3
"""克系小说展示站构建脚本。

用法：
  python3 build.py            # 从 content/ 渲染全站到 _site/
  python3 build.py --sync     # 先把草稿同步到 content/，再渲染

零依赖：仅 Python 3.9+ 标准库。
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_manifest(path):
    """读取 manifest.json 并返回 dict。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_txt(text):
    """txt 正文 → 段落列表。

    规则：空行分段；段内换行直接合并（中文断行不产生空格）。
    """
    paragraphs = []
    for block in text.split("\n\n"):
        block = block.replace("\n", "").strip()
        if block:
            paragraphs.append(block)
    return paragraphs


def inline_md(s):
    """行内格式：**粗体** → <strong>。"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def parse_markdown_sections(text):
    """settings.md → [{"level": n, "title": t, "body": [line, ...]}, ...]

    以 h1-h3 为界切分，标题之前的文本忽略。
    """
    sections = []
    current = None
    for line in text.split("\n"):
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            current = {"level": len(m.group(1)), "title": m.group(2).strip(),
                       "body": []}
            sections.append(current)
        elif current is not None:
            current["body"].append(line)
    return sections


def render_markdown_body(lines):
    """设定页正文块 → HTML。

    支持 h3、有序/无序列表、**粗体**、> 引用、段落；
    列表项跨行时以 <br> 续行。
    """
    out, para, in_ul, in_ol = [], [], False, False

    def flush_para():
        if para:
            out.append("<p>" + "".join(para) + "</p>")
            para.clear()

    def flush_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for line in lines:
        s = line.strip()
        if not s:
            flush_para()
            flush_lists()
            continue
        if s.startswith("### "):
            flush_para()
            flush_lists()
            out.append("<h3>" + inline_md(s[4:]) + "</h3>")
        elif s.startswith("- "):
            flush_para()
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append("<li>" + inline_md(s[2:]) + "</li>")
        elif re.match(r"^\d+\.\s", s):
            flush_para()
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append("<li>" + inline_md(re.sub(r"^\d+\.\s", "", s)) + "</li>")
        elif s.startswith(">"):
            flush_para()
            flush_lists()
            out.append("<blockquote>" + inline_md(s[1:].strip()) + "</blockquote>")
        elif (in_ul or in_ol) and out and out[-1].startswith("<li>"):
            out[-1] = out[-1][:-5] + "<br>" + inline_md(s) + "</li>"
        else:
            flush_lists()
            para.append(inline_md(s))
    flush_para()
    flush_lists()
    return "\n".join(out)


def sync_content(manifest, root, draft_dir=None):
    """按 manifest 把草稿拷入 content/。返回拷贝的文件数。

    只拷贝 manifest 引用的源文件；.bak 等未收录文件天然被跳过。
    """
    root = Path(root)
    if draft_dir is None:
        draft_dir = (root / manifest["draft_dir"]).resolve()
    draft_dir = Path(draft_dir)
    count = 0
    for group in ("chapters", "extras"):
        for item in manifest[group]:
            src = draft_dir / item["source"]
            if not src.is_file():
                raise FileNotFoundError(f"草稿缺失：{src}")
            dst = root / "content" / group / f"{item['id']}.txt"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            count += 1
    src = draft_dir / manifest["settings_source"]
    if not src.is_file():
        raise FileNotFoundError(f"设定文档缺失：{src}")
    shutil.copyfile(src, root / "content" / "settings.md")
    return count + 1
