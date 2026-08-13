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
