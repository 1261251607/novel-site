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


if __name__ == "__main__":
    unittest.main()
