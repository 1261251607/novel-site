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


class TestParseTxt(unittest.TestCase):
    def test_blank_line_separates_paragraphs(self):
        text = "第一段。\n\n第二段。\n\n\n第三段。"
        self.assertEqual(build.parse_txt(text), ["第一段。", "第二段。", "第三段。"])

    def test_internal_newlines_are_joined(self):
        text = "第一段\n续行。\n\n第二段。"
        self.assertEqual(build.parse_txt(text), ["第一段续行。", "第二段。"])

    def test_empty_text_gives_no_paragraphs(self):
        self.assertEqual(build.parse_txt(""), [])


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


if __name__ == "__main__":
    unittest.main()
