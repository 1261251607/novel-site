# 克系小说展示站 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用零依赖 Python 构建脚本把 txt 草稿渲染成克系风格的静态小说站，部署到 GitHub Pages。

**Architecture:** `manifest.json` 是唯一真源（书名、章节顺序、源文件、设定公开清单）；`build.py` 按 manifest 从 `content/` 渲染纯静态 HTML 到 `_site/`，`--sync` 负责从草稿目录同步稿子；GitHub Actions 在 push 后构建并部署。

**Tech Stack:** Python 3.9+ 标准库（argparse/json/shutil/string/html/pathlib/re）、string.Template 模板、纯 CSS 双主题变量、GitHub Actions + Pages。

**Spec:** `docs/superpowers/specs/2026-08-13-novel-site-design.md`

**说明：** novel-site/ 将成为独立 git 仓库（claudework 本身不是仓库）。content/ 中的章节文件名用 id 命名（`chapters/1-1.txt`），替代设计文档中「01.txt」的说法——两者等价，id 命名与 URL 一一对应更简单。

---

### Task 1: 仓库初始化

**Files:**
- Create: `novel-site/.gitignore`

- [ ] **Step 1: 初始化 git 仓库并建目录**

```bash
cd /Users/scholar/claudework/novel-site
git init -b main
mkdir -p content/chapters content/extras templates assets tests .github/workflows docs/superpowers/plans
```

- [ ] **Step 2: 写 .gitignore**

```
_site/
__pycache__/
.DS_Store
```

- [ ] **Step 3: 提交**

```bash
git add .gitignore
git commit -m "chore: init novel-site repo"
```

---

### Task 2: manifest.json + load_manifest

**Files:**
- Create: `novel-site/manifest.json`
- Create: `novel-site/build.py`
- Test: `novel-site/tests/test_build.py`

- [ ] **Step 1: 写失败的测试**

`tests/test_build.py` 完整内容：

```python
"""build.py 单元测试。运行：python3 -m unittest discover tests"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import build  # noqa: E402


def make_manifest():
    """测试用最小 manifest，与真实 manifest.json 同构。"""
    return {
        "draft_dir": "../drafts",
        "site": {
            "title": "测试书名",
            "tagline": "测试标语",
            "author": "",
            "footline": "测试页脚",
        },
        "chapters": [
            {"id": "1-1", "title": "第一章 · 第一节", "source": "01.txt"},
            {"id": "1-2", "title": "第一章 · 第二节", "source": "02.txt"},
        ],
        "extras": [
            {"id": "jing", "title": "番外《井》", "source": "jing.txt"},
        ],
        "settings_source": "settings.md",
        "settings_public": ["一句话概括"],
    }


class TestLoadManifest(unittest.TestCase):
    def test_load_manifest_reads_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text('{"a": 1, "b": [2, 3]}', encoding="utf-8")
            self.assertEqual(build.load_manifest(path), {"a": 1, "b": [2, 3]})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `cd /Users/scholar/claudework/novel-site && python3 -m unittest discover tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build'`

- [ ] **Step 3: 写 build.py 骨架 + load_manifest**

`build.py` 初始内容：

```python
#!/usr/bin/env python3
"""克系小说展示站构建脚本。

用法：
  python3 build.py            # 从 content/ 渲染全站到 _site/
  python3 build.py --sync     # 先把草稿同步到 content/，再渲染

零依赖：仅 Python 3.9+ 标准库。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_manifest(path):
    """读取 manifest.json 并返回 dict。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — `test_load_manifest_reads_json ... ok`

- [ ] **Step 5: 写真实 manifest.json**

```json
{
  "draft_dir": "../克系小说草稿",
  "site": {
    "title": "书名未定",
    "tagline": "神已死。位子是空的，有东西坐了上去。",
    "author": "",
    "footline": "看多了，祂要记住你的"
  },
  "chapters": [
    {"id": "1-1", "title": "第一章 · 第一节", "source": "20260811-第一章第一节.txt"},
    {"id": "1-2", "title": "第一章 · 第二节", "source": "20260811-第一章第二节.txt"},
    {"id": "1-3", "title": "第一章 · 第三节", "source": "20260811-第一章第三节.txt"},
    {"id": "1-4", "title": "第一章 · 第四节", "source": "20260811-第一章第四节.txt"},
    {"id": "1-5", "title": "第一章 · 第五节", "source": "20260811-第一章第五节.txt"},
    {"id": "1-6", "title": "第一章 · 第六节", "source": "20260811-第一章第六节.txt"},
    {"id": "1-7", "title": "第一章 · 第七节", "source": "20260811-第一章第七节.txt"},
    {"id": "1-8", "title": "第一章 · 第八节", "source": "20260811-第一章第八节.txt"},
    {"id": "1-9", "title": "第一章 · 第九节", "source": "20260811-第一章第九节.txt"},
    {"id": "1-10", "title": "第一章 · 第十节", "source": "20260811-第一章第十节.txt"},
    {"id": "1-11", "title": "第一章 · 第十一节", "source": "20260811-第一章第十一节.txt"},
    {"id": "1-12", "title": "第一章 · 第十二节", "source": "20260811-第一章第十二节.txt"}
  ],
  "extras": [
    {"id": "jing", "title": "番外《井》", "source": "20260811-番外-井.txt"},
    {"id": "shixiang", "title": "番外《石像》", "source": "20260811-番外-石像.txt"}
  ],
  "settings_source": "设定文档.md",
  "settings_public": ["一句话概括"]
}
```

> 注意：`settings_public` 初始只公开「一句话概括」（与标语同级别信息）。用户后续圈定更多条目时，把 settings.md 中对应的 `##` 标题原文加进这个数组即可。

- [ ] **Step 6: 提交**

```bash
git add build.py manifest.json tests/test_build.py
git commit -m "feat: manifest and load_manifest"
```

---

### Task 3: parse_txt

**Files:**
- Modify: `novel-site/build.py`（追加函数）
- Modify: `novel-site/tests/test_build.py`（追加测试类）

- [ ] **Step 1: 写失败的测试**（追加到 test_build.py 末尾）

```python
class TestParseTxt(unittest.TestCase):
    def test_blank_line_separates_paragraphs(self):
        text = "第一段。\n\n第二段。\n\n\n第三段。"
        self.assertEqual(build.parse_txt(text), ["第一段。", "第二段。", "第三段。"])

    def test_internal_newlines_are_joined(self):
        text = "第一段\n续行。\n\n第二段。"
        self.assertEqual(build.parse_txt(text), ["第一段续行。", "第二段。"])

    def test_empty_text_gives_no_paragraphs(self):
        self.assertEqual(build.parse_txt(""), [])
```

- [ ] **Step 2: 运行，确认失败**

Run: `python3 -m unittest discover tests -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'parse_txt'`

- [ ] **Step 3: 在 build.py 末尾追加**

```python
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
```

- [ ] **Step 4: 运行，确认通过**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — 3 个 parse_txt 测试全过

- [ ] **Step 5: 提交**

```bash
git add build.py tests/test_build.py
git commit -m "feat: parse_txt paragraph parser"
```

---

### Task 4: markdown 渲染（设定页用）

**Files:**
- Modify: `novel-site/build.py`（追加）
- Modify: `novel-site/tests/test_build.py`（追加）

- [ ] **Step 1: 写失败的测试**（追加）

```python
class TestMarkdown(unittest.TestCase):
    def test_sections_split_by_headings(self):
        md = "# 标题\n\n## 一、某节\n\n正文一。\n\n## 二、另一节\n\n正文三。"
        sections = build.parse_markdown_sections(md)
        self.assertEqual([s["title"] for s in sections],
                         ["标题", "一、某节", "二、另一节"])

    def test_body_renders_heading_list_bold_quote(self):
        html = build.render_markdown_body([
            "### 小节",
            "普通段落。",
            "",
            "- 条目一",
            "- **加粗条目**",
            "",
            "1. 有序一",
            "2. 有序二",
            "",
            "> 引用行",
        ])
        self.assertIn("<h3>小节</h3>", html)
        self.assertIn("<p>普通段落。</p>", html)
        self.assertIn("<li>条目一</li>", html)
        self.assertIn("<li><strong>加粗条目</strong></li>", html)
        self.assertIn("<ol>", html)
        self.assertIn("<li>有序一</li>", html)
        self.assertIn("<blockquote>引用行</blockquote>", html)

    def test_list_item_continuation_line(self):
        html = build.render_markdown_body(["- 条目一", "  续行内容。"])
        self.assertIn("<li>条目一<br>续行内容。</li>", html)
```

- [ ] **Step 2: 运行，确认失败**

Run: `python3 -m unittest discover tests -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'parse_markdown_sections'`

- [ ] **Step 3: 在 build.py 末尾追加**

```python
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
```

- [ ] **Step 4: 改 build.py 顶部 import**（加 `re`）

把：

```python
import json
from pathlib import Path
```

改成：

```python
import json
import re
from pathlib import Path
```

- [ ] **Step 5: 运行，确认通过**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — 3 个 markdown 测试全过

- [ ] **Step 6: 提交**

```bash
git add build.py tests/test_build.py
git commit -m "feat: minimal markdown renderer for settings page"
```

---

### Task 5: sync_content

**Files:**
- Modify: `novel-site/build.py`（追加）
- Modify: `novel-site/tests/test_build.py`（追加）

- [ ] **Step 1: 写失败的测试**（追加）

```python
class TestSync(unittest.TestCase):
    def test_sync_copies_listed_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            drafts = root / "drafts"
            drafts.mkdir()
            (drafts / "01.txt").write_text("甲", encoding="utf-8")
            (drafts / "02.txt").write_text("乙", encoding="utf-8")
            (drafts / "jing.txt").write_text("丙", encoding="utf-8")
            (drafts / "settings.md").write_text("丁", encoding="utf-8")
            # 未列入 manifest 的文件（含 .bak）不应被拷贝
            (drafts / "03.txt.bak").write_text("忽略我", encoding="utf-8")
            manifest = make_manifest()
            count = build.sync_content(manifest, root, draft_dir=drafts)
            self.assertEqual(count, 4)
            self.assertEqual(
                (root / "content/chapters/1-1.txt").read_text(encoding="utf-8"), "甲")
            self.assertEqual(
                (root / "content/extras/jing.txt").read_text(encoding="utf-8"), "丙")
            self.assertEqual(
                (root / "content/settings.md").read_text(encoding="utf-8"), "丁")
            self.assertFalse((root / "content/chapters/03.txt.bak").exists())

    def test_sync_raises_when_source_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "drafts").mkdir()
            manifest = make_manifest()
            with self.assertRaises(FileNotFoundError):
                build.sync_content(manifest, root, draft_dir=root / "drafts")
```

- [ ] **Step 2: 运行，确认失败**

Run: `python3 -m unittest discover tests -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'sync_content'`

- [ ] **Step 3: 在 build.py 末尾追加**

```python
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
```

- [ ] **Step 4: 改 build.py 顶部 import**（加 `shutil`）

```python
import json
import re
import shutil
from pathlib import Path
```

- [ ] **Step 5: 运行，确认通过**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — 2 个 sync 测试全过

- [ ] **Step 6: 提交**

```bash
git add build.py tests/test_build.py
git commit -m "feat: sync_content draft importer"
```

---

### Task 6: 页面模板

**Files:**
- Create: `novel-site/templates/base.html`
- Create: `novel-site/templates/home.html`
- Create: `novel-site/templates/chapter.html`
- Create: `novel-site/templates/settings.html`

本任务只写模板文件，无单测——Task 7 的 build 测试会覆盖它们。占位符语法为 `string.Template`（`$name` / `${root}`）。

- [ ] **Step 1: templates/base.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$pagetitle</title>
<link rel="stylesheet" href="${root}assets/style.css">
</head>
<body>
<header class="site-nav">
  <a class="site-name" href="${root}index.html">$sitetitle</a>
  <nav class="nav-links">
    <a href="${root}index.html">目录</a>
    <a href="${root}$firstextra">番外</a>
    <a href="${root}settings.html">设定</a>
    <a href="#footer">关于</a>
  </nav>
</header>
<main>
$content
</main>
<footer id="footer" class="site-foot">
  <p class="foot-line">$footline</p>
  <p class="foot-meta">本页面由 build.py 自动生成</p>
</footer>
</body>
</html>
```

- [ ] **Step 2: templates/home.html**

```html
<section class="hero">
  <div class="seal">$seal</div>
  <h1 class="hero-title">$sitetitle</h1>
  <p class="hero-tag">$tagline</p>
  <p class="hero-sub">—— 门内纪事 · 永昌二年</p>
</section>
<section class="toc">
  <h2 class="toc-head">正篇</h2>
  <ul class="toc-list">$chapters</ul>
  <h2 class="toc-head toc-head-extra">番外</h2>
  <ul class="toc-list toc-list-extra">$extras</ul>
</section>
```

- [ ] **Step 3: templates/chapter.html**

```html
<article class="reading">
  <p class="reading-label">$grouplabel</p>
  <h1 class="reading-title">$title</h1>
  <div class="reading-body">
$body
  </div>
  <nav class="pager">
    $prev
    <a class="pager-toc" href="${root}index.html">回目录</a>
    $next
  </nav>
</article>
```

- [ ] **Step 4: templates/settings.html**

```html
<article class="settings">
  <h1 class="settings-title">设定 · 部分公开</h1>
  <p class="settings-note">以下条目已公开。其余设定仍封存于门内。</p>
  <div class="settings-body">
$sections
  </div>
</article>
```

- [ ] **Step 5: 提交**

```bash
git add templates/
git commit -m "feat: HTML templates (base/home/chapter/settings)"
```

---

### Task 7: build() 渲染管线

**Files:**
- Modify: `novel-site/build.py`（追加）
- Modify: `novel-site/tests/test_build.py`（追加）

- [ ] **Step 1: 写失败的测试**（追加；用仓库真实模板，测试同时覆盖模板正确性）

```python
class TestBuild(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        content = self.root / "content"
        (content / "chapters").mkdir(parents=True)
        (content / "extras").mkdir(parents=True)
        (content / "chapters/1-1.txt").write_text(
            "第一节第一段。\n\n第一节第二段。", encoding="utf-8")
        (content / "chapters/1-2.txt").write_text("第二节正文。", encoding="utf-8")
        (content / "extras/jing.txt").write_text("井的正文。", encoding="utf-8")
        (content / "settings.md").write_text(
            "# 设定文档\n\n## 一句话概括\n\n这是公开的一句话。\n\n"
            "## 时间线\n\n这是秘密时间线。",
            encoding="utf-8",
        )
        (self.root / "assets").mkdir()
        (self.root / "assets/style.css").write_text("/* css */", encoding="utf-8")
        self.manifest = make_manifest()

    def tearDown(self):
        self._tmp.cleanup()

    def test_build_generates_all_pages(self):
        out = build.build(self.manifest, self.root, templates_dir=REPO / "templates")
        self.assertTrue((out / "index.html").is_file())
        self.assertTrue((out / "chapters/1-1.html").is_file())
        self.assertTrue((out / "chapters/1-2.html").is_file())
        self.assertTrue((out / "extras/jing.html").is_file())
        self.assertTrue((out / "settings.html").is_file())
        self.assertTrue((out / "assets/style.css").is_file())

    def test_chapter_renders_paragraphs_and_prev_next(self):
        out = build.build(self.manifest, self.root, templates_dir=REPO / "templates")
        first = (out / "chapters/1-1.html").read_text(encoding="utf-8")
        self.assertIn("第一节第一段。", first)
        self.assertIn('class="first"', first)
        self.assertIn("已是开头", first)
        self.assertIn('href="1-2.html"', first)
        second = (out / "chapters/1-2.html").read_text(encoding="utf-8")
        self.assertIn("第二节正文。", second)
        self.assertIn('href="1-1.html"', second)
        self.assertIn("已是结尾", second)

    def test_home_lists_chapters_and_extras(self):
        out = build.build(self.manifest, self.root, templates_dir=REPO / "templates")
        home = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("第一章 · 第一节", home)
        self.assertIn("番外《井》", home)
        self.assertIn('href="chapters/1-1.html"', home)
        self.assertIn('href="extras/jing.html"', home)
        self.assertIn("壹", home)

    def test_settings_public_filter(self):
        out = build.build(self.manifest, self.root, templates_dir=REPO / "templates")
        page = (out / "settings.html").read_text(encoding="utf-8")
        self.assertIn("这是公开的一句话。", page)
        self.assertNotIn("秘密时间线", page)

    def test_chapter_nav_links_back_to_index(self):
        out = build.build(self.manifest, self.root, templates_dir=REPO / "templates")
        page = (out / "chapters/1-1.html").read_text(encoding="utf-8")
        self.assertIn("../index.html", page)
```

- [ ] **Step 2: 运行，确认失败**

Run: `python3 -m unittest discover tests -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'build'`

- [ ] **Step 3: 在 build.py 末尾追加渲染管线**

```python
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
        chapters=chapters_html, extras=extras_html, root="",
    )
    render_page("index.html", home_content, "", site["title"])
    return out_dir
```

- [ ] **Step 4: 改 build.py 顶部 import**（加 `html`、`string`）

```python
import html
import json
import re
import shutil
import string
from pathlib import Path
```

- [ ] **Step 5: 运行，确认通过**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — 全部 14 个测试

- [ ] **Step 6: 提交**

```bash
git add build.py tests/test_build.py
git commit -m "feat: full site render pipeline"
```

---

### Task 8: CLI 入口

**Files:**
- Modify: `novel-site/build.py`（追加）

- [ ] **Step 1: 在 build.py 末尾追加 CLI**

```python
def main(argv=None):
    parser = argparse.ArgumentParser(description="克系小说展示站构建脚本")
    parser.add_argument("--sync", action="store_true",
                        help="先把草稿同步到 content/ 再构建")
    parser.add_argument("--out-dir", default=None,
                        help="输出目录（默认 _site/）")
    args = parser.parse_args(argv)

    manifest = load_manifest(ROOT / "manifest.json")
    if args.sync:
        n = sync_content(manifest, ROOT)
        print(f"已同步 {n} 个文件")
    out_dir = build(manifest, ROOT, out_dir=args.out_dir)
    print(f"构建完成 → {out_dir}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 改 build.py 顶部 import**（加 `argparse`）

```python
import argparse
import html
import json
import re
import shutil
import string
from pathlib import Path
```

- [ ] **Step 3: 冒烟测试 --help**

Run: `python3 build.py --help`
Expected: 输出 usage 与三个参数说明，退出码 0

- [ ] **Step 4: 跑全量单测**

Run: `python3 -m unittest discover tests -v`
Expected: PASS — 全部 14 个测试

- [ ] **Step 5: 提交**

```bash
git add build.py
git commit -m "feat: CLI entry (--sync, --out-dir)"
```

---

### Task 9: 样式表（双主题）

**Files:**
- Create: `novel-site/assets/style.css`

- [ ] **Step 1: 写 assets/style.css 完整内容**

```css
/* 克系小说展示站样式 · 双主题
   B「泛黄手稿」为默认（:root），A「深渊暗黑」为备用（[data-theme="a"]）。
   切换器后置；两套配色已用 CSS 变量就位。 */

:root {
  /* B · 泛黄手稿 */
  --paper: #e7dcc0;
  --ink: #33291a;
  --ink-soft: #6d5a36;
  --accent: #8c2f2f;
  --line: #a08c62;
  --seal-bg: #8c2f2f;
  --seal-ink: #e7dcc0;
}

[data-theme="a"] {
  /* A · 深渊暗黑 */
  --paper: #0b0d10;
  --ink: #cfc8b8;
  --ink-soft: #8d8574;
  --accent: #c9a96a;
  --line: #2a2e35;
  --seal-bg: #c9a96a;
  --seal-ink: #0b0d10;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--paper);
  color: var(--ink);
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", Georgia, serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-image:
    radial-gradient(ellipse at 18% 8%, rgba(120, 90, 40, .10), transparent 60%),
    radial-gradient(ellipse at 85% 92%, rgba(120, 90, 40, .12), transparent 55%);
  background-attachment: fixed;
}

[data-theme="a"] body {
  background-image:
    radial-gradient(ellipse at 50% 0%, rgba(201, 169, 106, .06), transparent 55%),
    radial-gradient(ellipse at 50% 100%, rgba(60, 40, 20, .25), transparent 60%);
}

/* 导航 */
.site-nav {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 18px 28px 12px;
  border-bottom: 1px solid var(--line);
  margin: 0 20px;
}
.site-name {
  font-size: 15px;
  letter-spacing: 6px;
  color: var(--ink);
  text-decoration: none;
}
.nav-links a {
  margin-left: 18px;
  font-size: 13px;
  color: var(--ink-soft);
  text-decoration: none;
  letter-spacing: 2px;
}
.nav-links a:hover { color: var(--accent); }

main {
  flex: 1;
  width: 100%;
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 28px 64px;
}

/* 首页 hero */
.hero { text-align: center; position: relative; padding: 30px 0 10px; }
.seal {
  position: absolute;
  top: 26px;
  right: 8px;
  width: 44px;
  height: 44px;
  background: var(--seal-bg);
  color: var(--seal-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  transform: rotate(-6deg);
  opacity: .85;
}
.hero-title {
  writing-mode: vertical-rl;
  font-size: 30px;
  font-weight: 600;
  letter-spacing: 12px;
  margin: 0 auto 10px;
}
.hero-tag { font-size: 14px; line-height: 1.9; }
.hero-sub {
  font-size: 12px;
  color: var(--ink-soft);
  margin-top: 8px;
  letter-spacing: 2px;
}

/* 目录 */
.toc { margin-top: 36px; }
.toc-head {
  font-size: 13px;
  letter-spacing: 6px;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--line);
  padding-bottom: 6px;
  margin-bottom: 10px;
}
.toc-head-extra { margin-top: 28px; }
.toc-list { list-style: none; }
.toc-item a {
  display: flex;
  align-items: baseline;
  padding: 10px 4px;
  border-bottom: 1px dotted var(--line);
  text-decoration: none;
  color: var(--ink);
  font-size: 16px;
}
.toc-item a:hover { color: var(--accent); }
.toc-no {
  color: var(--ink-soft);
  font-size: 12px;
  letter-spacing: 2px;
  margin-right: 14px;
}
.toc-list-extra .toc-name { color: var(--accent); }

/* 阅读页 */
.reading { padding-top: 8px; }
.reading-label {
  font-size: 12px;
  letter-spacing: 4px;
  color: var(--ink-soft);
  margin-bottom: 10px;
}
.reading-title {
  font-size: 24px;
  letter-spacing: 4px;
  margin-bottom: 28px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.reading-body {
  max-width: 680px;
  margin: 0 auto;
  font-size: 17px;
  line-height: 1.9;
}
.reading-body p { margin-bottom: 1.4em; text-indent: 2em; }
.reading-body p.first { text-indent: 0; }
.reading-body p.first::first-letter {
  font-size: 3.2em;
  float: left;
  line-height: 1;
  padding: 6px 10px 0 0;
  color: var(--accent);
  font-weight: 600;
}

/* 翻页 */
.pager {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 44px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  font-size: 14px;
}
.pager a { color: var(--ink); text-decoration: none; }
.pager a:hover { color: var(--accent); }
.pager-off { color: var(--ink-soft); opacity: .5; }
.pager-toc { letter-spacing: 3px; }

/* 设定页 */
.settings-title {
  font-size: 24px;
  letter-spacing: 4px;
  margin-bottom: 10px;
}
.settings-note {
  color: var(--ink-soft);
  font-size: 13px;
  margin-bottom: 30px;
}
.settings-body h2 {
  font-size: 18px;
  margin: 26px 0 12px;
  letter-spacing: 2px;
}
.settings-body h3 { font-size: 16px; margin: 20px 0 8px; }
.settings-body p {
  margin-bottom: 1em;
  font-size: 15.5px;
  line-height: 1.85;
}
.settings-body ul, .settings-body ol {
  margin: 0 0 1em 1.6em;
  font-size: 15.5px;
  line-height: 1.85;
}
.settings-body blockquote {
  margin: 0 0 1em;
  padding: 8px 16px;
  border-left: 3px solid var(--accent);
  color: var(--ink-soft);
  font-size: 14.5px;
}
.settings-body strong { color: var(--accent); }

/* 页脚 */
.site-foot {
  text-align: center;
  padding: 26px 0 30px;
  border-top: 1px solid var(--line);
  margin: 0 20px;
}
.foot-line {
  font-size: 12px;
  letter-spacing: 6px;
  color: var(--ink-soft);
}
.foot-meta {
  font-size: 10px;
  color: var(--ink-soft);
  opacity: .6;
  margin-top: 8px;
  letter-spacing: 1px;
}

@media (max-width: 560px) {
  .site-nav { flex-direction: column; gap: 8px; }
  .reading-body { font-size: 16px; }
}
```

- [ ] **Step 2: 提交**

```bash
git add assets/style.css
git commit -m "feat: dual-theme stylesheet (B default, A reserved)"
```

---

### Task 10: 真实内容全量同步 + 浏览器走查

**Files:**
- Create: `novel-site/content/**`（由 --sync 生成，提交进仓库）

- [ ] **Step 1: 全量同步并构建**

Run: `python3 build.py --sync`
Expected:
```
已同步 15 个文件
构建完成 → /Users/scholar/claudework/novel-site/_site
```

- [ ] **Step 2: 起本地预览服务**

Run: `cd /Users/scholar/claudework/novel-site && python3 -m http.server 8321 --directory _site`
（后台运行；浏览器打开 http://localhost:8321）

- [ ] **Step 3: 走查清单（浏览器面板逐页检查）**

1. 首页：竖排书名、朱砂印、标语、正篇目录 12 节（壹…拾贰）、番外 2 篇、页脚彩蛋
2. 第一章第一节：首字下沉、段首缩进、无「上一节」链接（已是开头）、有「下一节」
3. 第一章第十二节：有「上一节」、无「下一节」（已是结尾）
4. 番外《井》：番外标签、上一篇/下一篇为番外互链
5. 设定页：只显示「一句话概括」，无「时间线」
6. 任意页点导航四链接均可用；移动端宽度（375px）下导航竖排不断裂

- [ ] **Step 4: 提交**

```bash
git add content/
git commit -m "content: sync chapter 1 (12 sections) + extras + settings"
```

---

### Task 11: GitHub 仓库 + Actions 部署

**Files:**
- Create: `novel-site/.github/workflows/pages.yml`

- [ ] **Step 1: 写部署工作流**

`.github/workflows/pages.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run tests
        run: python3 -m unittest discover tests -v
      - name: Build site
        run: python3 build.py
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: 提交并推到 GitHub**

```bash
git add .github/workflows/pages.yml
git commit -m "ci: GitHub Pages deploy workflow"
gh auth status   # 若未登录：gh auth login
gh repo create novel-site --public --source . --push
```

（若无 gh CLI 或未登录：在 github.com 手动建空仓库 `novel-site`（public），然后 `git remote add origin git@github.com:<用户名>/novel-site.git && git push -u origin main`。）

- [ ] **Step 3: 开启 Pages（一次性手动操作）**

浏览器打开 `https://github.com/<用户名>/novel-site/settings/pages` → Build and deployment → Source 选 **GitHub Actions** → Save。

- [ ] **Step 4: 验证部署**

- 打开仓库 Actions 页，确认 `Deploy to GitHub Pages` 工作流全绿
- 访问 `https://<用户名>.github.io/novel-site/`，重复 Task 10 Step 3 的走查清单

- [ ] **Step 5: 收尾提交（如有 Pages 设置引发的重跑）**

无改动则跳过。至此全部任务完成。

---

## 验证总则

每个任务提交前：`python3 -m unittest discover tests -v` 全绿；Task 10 起另有浏览器走查。最终验收标准：

1. `python3 build.py --sync` 一条命令完成「改稿 → 网站更新」全流程
2. 首页/章节/番外/设定四类页面在桌面与 375px 宽度下渲染正常
3. 设定页只含 `settings_public` 清单条目
4. push 到 main 后 GitHub Pages 自动更新
