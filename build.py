#!/usr/bin/env python3
"""克系小说展示站构建脚本。

用法：
  python3 build.py            # 从 content/ 渲染全站到 _site/
  python3 build.py --sync     # 先把草稿同步到 content/，再渲染

零依赖：仅 Python 3.9+ 标准库。
"""
import argparse
import html
import json
import re
import shutil
import string
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


# ---------------------------------------------------------------- 自动维护 manifest

_CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_to_int(s):
    """中文数字 → 整数，支持 一 到 九千九百九十九（章节编号用）。"""
    total, num = 0, 0
    for ch in s:
        if ch in _CN_DIGITS:
            num = _CN_DIGITS[ch]
        elif ch in ("十", "百", "千"):
            unit = {"十": 10, "百": 100, "千": 1000}[ch]
            total += (num if num else 1) * unit
            num = 0
        else:
            raise ValueError(f"无法解析的中文数字：{s}")
    return total + num


_CHAPTER_RE = re.compile(
    r"^\d{8}-(第[零一二三四五六七八九十百千]+章)"
    r"(第[零一二三四五六七八九十百千]+节)\.txt$")


def parse_chapter_filename(name):
    """'20260812-第二章第一节.txt' → (2, 1, '第二章 · 第一节')；不匹配返回 None。"""
    m = _CHAPTER_RE.match(name)
    if not m:
        return None
    try:
        cn = cn_to_int(m.group(1)[1:-1])
        sn = cn_to_int(m.group(2)[1:-1])
    except ValueError:
        return None
    return cn, sn, f"{m.group(1)} · {m.group(2)}"


_EXTRA_RE = re.compile(r"^(\d{8})-番外-(.+)\.txt$")


def parse_extra_filename(name):
    """'20260811-番外-石像.txt' → ('20260811', '石像', '番外《石像》')；不匹配返回 None。"""
    m = _EXTRA_RE.match(name)
    if not m:
        return None
    return m.group(1), m.group(2), f"番外《{m.group(2)}》"


def update_manifest(manifest, draft_dir):
    """按草稿目录维护 manifest 的章节/番外条目。

    - 新增：未收录且命名规范的 txt 自动加条目（章节按章/节号排序，番外按日期排序）
    - 清理：源文件已不存在的条目移除
    - 忽略：命名不规范的 txt 不收，报给调用方提醒
    返回 (added, pruned, ignored) 三个列表。幂等。
    """
    draft_dir = Path(draft_dir)
    listed = {item["source"] for g in ("chapters", "extras")
              for item in manifest[g]}
    added, pruned, ignored = [], [], []

    for group in ("chapters", "extras"):
        kept = []
        for item in manifest[group]:
            if (draft_dir / item["source"]).is_file():
                kept.append(item)
            else:
                pruned.append(item["title"])
        manifest[group] = kept

    for p in sorted(draft_dir.glob("*.txt")):
        name = p.name
        if name in listed or name.endswith(".bak") or "合集" in name:
            continue
        if name == manifest.get("settings_source", ""):
            continue
        ch = parse_chapter_filename(name)
        if ch:
            cn, sn, title = ch
            manifest["chapters"].append(
                {"id": f"{cn}-{sn}", "title": title, "source": name})
            added.append(title)
            continue
        ex = parse_extra_filename(name)
        if ex:
            _, key, title = ex
            manifest["extras"].append(
                {"id": key, "title": title, "source": name})
            added.append(title)
            continue
        ignored.append(name)

    manifest["chapters"].sort(
        key=lambda it: (parse_chapter_filename(it["source"]) or (10 ** 6, 10 ** 6, ""))[:2])
    manifest["extras"].sort(
        key=lambda it: (parse_extra_filename(it["source"]) or ("", "", ""))[:2])
    return added, pruned, ignored


_NUMERALS = "零壹贰叁肆伍陆柒捌玖拾"


def _numeral(n):
    """1-99 的汉字数字（目录序号用）。"""
    if n <= 10:
        return _NUMERALS[n]
    if n < 20:
        return "拾" + _NUMERALS[n - 10]
    return _NUMERALS[n // 10] + "拾" + (_NUMERALS[n % 10] if n % 10 else "")


def _escape(s):
    return html.escape(s, quote=False)


def render_template(templates_dir, name, **ctx):
    """渲染 string.Template 模板文件。"""
    tpl = string.Template(
        (Path(templates_dir) / name).read_text(encoding="utf-8"))
    return tpl.substitute(**ctx)


def build(manifest, root, out_dir=None, templates_dir=None):
    """渲染全站到 out_dir（默认 <root>/_site）。返回 out_dir。"""
    root = Path(root)
    out_dir = Path(out_dir) if out_dir else root / "_site"
    templates_dir = Path(templates_dir) if templates_dir else root / "templates"
    site = manifest["site"]

    out_dir.mkdir(parents=True, exist_ok=True)
    dst_assets = out_dir / "assets"
    dst_assets.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "assets" / "style.css", dst_assets / "style.css")

    first_extra_id = manifest["extras"][0]["id"] if manifest["extras"] else ""
    ctx = {
        "sitetitle": _escape(site["title"]),
        "tagline": _escape(site["tagline"]),
        "author": _escape(site.get("author", "")),
        "footline": _escape(site.get("footline", "")),
        "seal": site["title"][0],
        "firstextra": f"extras/{first_extra_id}.html" if first_extra_id else "",
    }

    def render_page(name, content, root_prefix, pagetitle):
        page = render_template(
            templates_dir, "base.html",
            root=root_prefix, pagetitle=pagetitle, content=content, **ctx)
        target = out_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page, encoding="utf-8")

    # 章节与番外
    for group in ("chapters", "extras"):
        items = manifest[group]
        for i, item in enumerate(items):
            src = root / "content" / group / f"{item['id']}.txt"
            paragraphs = parse_txt(src.read_text(encoding="utf-8"))
            body = "\n".join(
                f'<p class="first">{_escape(p)}</p>' if k == 0 else f"<p>{_escape(p)}</p>"
                for k, p in enumerate(paragraphs)
            )
            if i > 0:
                prev_html = (f'<a href="{items[i - 1]["id"]}.html">'
                             f'← {_escape(items[i - 1]["title"])}</a>')
            else:
                prev_html = '<span class="pager-off">已是开头</span>'
            if i < len(items) - 1:
                next_html = (f'<a href="{items[i + 1]["id"]}.html">'
                             f'{_escape(items[i + 1]["title"])} →</a>')
            else:
                next_html = '<span class="pager-off">已是结尾</span>'
            content = render_template(
                templates_dir, "chapter.html",
                grouplabel="正篇" if group == "chapters" else "番外",
                title=_escape(item["title"]),
                body=body, prev=prev_html, next=next_html,
                root="../",
            )
            render_page(f"{group}/{item['id']}.html", content, "../",
                        f"{item['title']} · {site['title']}")

    # 设定页（只渲染 settings_public 清单中的条目）
    settings_md = (root / "content" / "settings.md").read_text(encoding="utf-8")
    sections = parse_markdown_sections(settings_md)
    public = set(manifest.get("settings_public", []))
    parts = []
    for s in sections:
        if s["title"] not in public:
            continue
        level = min(s["level"], 2)
        parts.append(
            f'<h{level} class="setting-title">{_escape(s["title"])}</h{level}>'
            + "\n" + render_markdown_body(s["body"])
        )
    settings_content = render_template(
        templates_dir, "settings.html",
        sections="\n".join(parts) if parts else "<p>设定尚未公开，敬请期待。</p>",
        root="",
    )
    render_page("settings.html", settings_content, "",
                f"设定 · {site['title']}")

    # 首页
    chapters_html = "\n".join(
        f'<li class="toc-item"><a href="chapters/{item["id"]}.html">'
        f'<span class="toc-no">{_numeral(k + 1)}</span>'
        f'<span class="toc-name">{_escape(item["title"])}</span></a></li>'
        for k, item in enumerate(manifest["chapters"])
    )
    extras_html = "\n".join(
        f'<li class="toc-item extra"><a href="extras/{item["id"]}.html">'
        f'<span class="toc-name">{_escape(item["title"])}</span></a></li>'
        for item in manifest["extras"]
    )
    home_content = render_template(
        templates_dir, "home.html",
        chapters=chapters_html, extras=extras_html, root="", **ctx,
    )
    render_page("index.html", home_content, "", site["title"])
    return out_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description="克系小说展示站构建脚本")
    parser.add_argument("--sync", action="store_true",
                        help="先把草稿同步到 content/ 再构建")
    parser.add_argument("--autoupdate", action="store_true",
                        help="按草稿目录自动维护 manifest（新增/清理章节番外条目）")
    parser.add_argument("--out-dir", default=None,
                        help="输出目录（默认 _site/）")
    args = parser.parse_args(argv)

    manifest_path = ROOT / "manifest.json"
    manifest = load_manifest(manifest_path)
    if args.autoupdate:
        added, pruned, ignored = update_manifest(
            manifest, (ROOT / manifest["draft_dir"]).resolve())
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        for t in added:
            print(f"✓ 新增条目：{t}")
        for t in pruned:
            print(f"✗ 移除条目（源稿缺失）：{t}")
        for n in ignored:
            print(f"⚠️  未收录（命名不识别）：{n}")
    if args.sync:
        n = sync_content(manifest, ROOT)
        print(f"已同步 {n} 个文件")
    out_dir = build(manifest, ROOT, out_dir=args.out_dir)
    print(f"构建完成 → {out_dir}")


if __name__ == "__main__":
    main()
