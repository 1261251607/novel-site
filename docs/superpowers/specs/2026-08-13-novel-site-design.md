# 克系小说站 · 设计文档

日期：2026-08-13
状态：已确认（用户批准方案：Python 构建脚本）

## 1. 概述

为克系长篇连载搭建一个只读展示网站：读者浏览章节目录、在线阅读正文与番外、查看部分公开的世界观设定。站点为纯静态站，托管于 GitHub Pages。

## 2. 已确认的需求

| 决策项 | 结论 |
|---|---|
| 用途 | 小说作品站（克系长篇 + 番外） |
| 功能范围 | 只读展示（无评论、无登录、无后台） |
| 稿子同步 | 构建脚本自动生成，txt 为唯一稿源 |
| 设定集 | 只公开部分（公开清单待用户圈定） |
| 部署 | GitHub Pages |
| 视觉 | B「泛黄手稿」为默认主题；A「深渊暗黑」为主题切换备选，本阶段不做切换器，但两套配色以 CSS 变量形式同时落地 |

## 3. 技术选型

- **构建**：零依赖 Python 脚本 `build.py`（仅标准库，Python 3.9+）。理由：本机已有 python3，GitHub Actions 直接可跑，无 Node/Ruby 依赖。
- **产出**：纯静态 HTML + CSS，无 JS 框架、无构建工具链。
- **部署**：GitHub Actions，push 到 main → 运行 build.py → upload-pages-artifact → deploy-pages。

## 4. 目录结构

```
novel-site/                       # git 仓库根
├── content/                      # 稿子（canonical 副本）
│   ├── chapters/                 # 正文：每节一个 txt，文件名 01.txt … 12.txt
│   ├── extras/                   # 番外：井.txt、石像.txt
│   └── settings.md               # 设定文档（全量）
├── manifest.json                 # 唯一真源：书名、章节顺序/标题/源文件、设定页公开清单
├── build.py                      # 构建脚本：--sync 同步草稿、默认渲染全站
├── templates/                    # Python 字符串模板：base / home / chapter / settings
├── assets/style.css              # 全部样式，双主题 CSS 变量
├── docs/superpowers/specs/       # 本设计文档
├── _site/                        # 构建产物（gitignore，不提交）
└── .github/workflows/pages.yml   # Pages 部署工作流
```

## 5. 数据流与构建流程

1. 用户在 `克系小说草稿/` 继续写稿（现有工作流不变）。
2. `python3 build.py --sync`：按 manifest 中记录的源文件路径，把最新稿子拷入 `content/`，跳过 `.bak` 文件。
3. `python3 build.py`：读取 `content/`，渲染 `_site/`：
   - 首页（目录）
   - 每个章节/番外一个独立 HTML 页，带上一节/下一节导航
   - 设定页（只渲染 manifest 公开清单中的条目）
4. 本地预览：`python3 -m http.server` 指向 `_site/`。
5. 发布：`git push` → GitHub Actions 构建并部署。

## 6. manifest.json（唯一真源）

```json
{
  "site": {
    "title": "书名未定",
    "tagline": "神已死。位子是空的，有东西坐了上去。",
    "author": ""
  },
  "chapters": [
    {"id": "1-1", "title": "第一章 · 第一节", "source": "克系小说草稿/20260811-第一章第一节.txt"},
    "…（共 12 节，按草稿目录顺序）"
  ],
  "extras": [
    {"id": "jing",  "title": "番外《井》",   "source": "克系小说草稿/20260811-番外-井.txt"},
    {"id": "shixiang", "title": "番外《石像》", "source": "克系小说草稿/20260811-番外-石像.txt"}
  ],
  "settings_public": ["…用户圈定的条目标题列表，对应 settings.md 中的 ## 标题"]
}
```

书名改动只需改 `site.title`，全站生效。

## 7. 页面规格

### 7.1 首页（B 手稿风）
- 顶部导航：目录 · 番外 · 设定 · 关于（关于暂为占位锚点，无独立页）
- 书名竖排大字 + 朱砂印 + 标语（「门内纪事 · 永昌二年」式落款）
- 正篇目录：第一章 12 节，序号用汉字（壹贰叁…）
- 番外区：两篇，视觉上以朱砂色区分
- 页脚彩蛋行（如「看多了，祂要记住你的」）

### 7.2 章节页 / 番外页
- 顶部：书名（小字）· 章节名
- 正文：窄栏（max-width 680px）居中，宋体（Songti SC / STSong 回退），字号约 17–18px，行距 1.9，首段首字下沉
- 底部：上一节 / 回目录 / 下一节（首末节相应隐藏）
- 同一 B 手稿质感：纸面底色 + 墨色正文

### 7.3 设定页
- 结构先行：按 settings.md 的标题层级渲染条目
- 只渲染 `settings_public` 清单中的标题及其正文；未列入的条目不输出到 HTML
- 页面顶部注明「设定 · 部分公开」

## 8. 内容解析规则

- **txt 正文**：按空行分段，段间输出 `<p>`；其余格式（如「——」）保留原文，不做 markdown 解析。
- **settings.md**：极简 markdown 渲染器（仅 `#`–`###` 标题、`-` 列表、`**粗体**`、`>` 引用、空行分段），内置于 build.py，不引第三方库。
- **同步规则**：`--sync` 只拷 manifest 引用的文件；草稿目录中的 `.bak`、合集文件、未收录文件一律忽略。

## 9. 视觉与主题

- 默认主题 B「泛黄手稿」：纸面底色（#e7dcc0 系）、墨色正文（#33291a 系）、朱砂红（#8c2f2f）点缀、宋体。
- 主题 A「深渊暗黑」：近黑底（#0b0d10）、暗金（#c9a96a）点缀，同一套 CSS 变量切换。
- 实现方式：所有颜色/背景走 CSS 自定义属性（`--paper`、`--ink`、`--accent` 等），`[data-theme="a"]` 覆盖变量。本阶段默认 B；切换器后置，届时仅需一个极小的 JS 片段 + 按钮。

## 10. 部署

- 仓库：novel-site（新建，GitHub 上公开）。
- Workflow `pages.yml`：`push` 到 `main` → `actions/checkout` → `python3 build.py` → `upload-pages-artifact`（`_site/`）→ `deploy-pages`。
- Pages 设置：Source 选 "GitHub Actions"。
- 首次配置需在仓库 Settings → Pages 中开启（一次性手动操作，实施时给出步骤）。

## 11. 明确不做（YAGNI）

评论、登录/后台、搜索、RSS、主题切换器（下阶段）、移动端原生 App、多语言、域名绑定（先用 `*.github.io`）。

## 12. 待定事项（不阻塞实施）

1. 书名（先用「书名未定」，改 manifest 一处即可）
2. 设定页公开条目清单（页面结构先落地，公开哪些由用户后续圈定）
3. 作者署名
