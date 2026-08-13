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
