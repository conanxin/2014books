2014年值得你阅读的100本书
========================

## 项目简介

本项目是 2014 年第一财经周刊专题「值得你阅读的100本书」的 Markdown 制书复刻。原始内容来自周刊网站，由 Conan Xin 整理为可编译的 Markdown 源码，并生成 PDF 小册子。

## 项目来源

- 原始专题：[第一财经周刊 · 值得你阅读的100本书](http://www.cbnweek.com/v/subject?id=22)
- 整理者：Conan Xin
- 源码仓库：https://github.com/conanxin/2014books

## 现在可以生成 PDF、Web 和 EPUB

本项目已从原始的单一脚本构建升级为支持多种输出格式：

- **PDF**：通过 `pandoc` + `xelatex` 生成排版精美的中文 PDF
- **静态网页**：通过 Python 标准库生成可离线浏览的静态网页，支持搜索和筛选
- **EPUB**：通过 `pandoc` 生成电子书，兼容主流阅读器

## GitHub Pages 自动部署

仓库已配置 GitHub Actions 工作流，支持 `push` 到 `master` 时自动部署到 GitHub Pages。

- 启用方式：仓库 Settings → Pages → Source: GitHub Actions
- 手动触发：Actions 标签页 → Deploy to GitHub Pages → Run workflow
- 预期地址：https://conanxin.github.io/2014books/

详见 [docs/GITHUB_PAGES_DEPLOYMENT.md](docs/GITHUB_PAGES_DEPLOYMENT.md)。

## 本地构建方法

### 依赖安装（Ubuntu/Debian）

```bash
sudo apt-get install pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra
sudo apt-get install fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei
```

### 构建命令

```bash
# 生成 PDF
make pdf

# 生成静态网页
make web

# 生成 EPUB
make epub

# 生成 release package（zip）
make release

# 同时生成所有输出
make all

# 清理构建产物
make clean
```

### 传统入口（兼容旧用法）

```bash
bash ./mmd2bok
```

## 项目结构

```
2014books/
├── contents/          # Markdown 源文件（章节内容）
│   ├── 0-preface*.markdown
│   ├── 1-chapter*.markdown
│   └── 2-appendix*.markdown
├── data/              # 书目元数据增强（人工/半人工入口）
│   ├── book_metadata_overrides.json
│   └── missing_book_candidates.json
├── template/          # LaTeX 模板文件
├── latex/             # LaTeX 构建工作目录
├── scripts/           # 现代构建脚本
│   ├── build_pdf.sh   # PDF 构建入口
│   ├── build_epub.sh  # EPUB 构建入口
│   ├── generate_web.py # 静态网页生成器
│   └── package_release.sh # Release package 打包
├── web/               # 生成的静态网页输出
│   ├── index.html
│   ├── .nojekyll
│   ├── assets/style.css
│   └── data/books.json
├── dist/              # 生成的 PDF/EPUB/Release 输出
│   ├── 2014books.pdf
│   ├── 2014books.epub
│   └── release/
├── .github/workflows/  # CI/CD 工作流
│   ├── build.yml
│   └── pages.yml
├── mmd2bok            # 传统 PDF 构建脚本（已修复章节排序）
├── Makefile           # 现代构建入口
└── README.md          # 本文件
```

## 已知限制

1. **书单完整性**：当前已从附录结构化整理 **97 本** 书目。项目标题中的"100本"为原始专题名称，实际可验证数量为 97 本，剩余 3 本需对照原始《第一财经周刊》专题进一步核对。缺失候选已单独记录在 `data/missing_book_candidates.json`，不会自动进入正式书单。
2. **PDF 字体依赖**：需要系统中安装 WenQuanYi 或 Noto CJK 系列中文字体，否则 xelatex 编译可能失败。模板已添加字体回退链。
3. **封面图片**：模板支持 `img/cover.pdf` 封面；若缺失则自动生成文字封面。
4. **网页搜索**：静态网页的搜索功能为前端 JavaScript 实现，无需后端服务，但仅支持当前页面已加载的内容。
5. **章节排序**：已修复原始脚本中 `1-chapter10` 排在 `1-chapter2` 之前的排序问题。

## 元数据增强

- `data/book_metadata_overrides.json`：人工/半人工增强元数据入口。用 `id` 匹配附录书目，非 null 字段覆盖或补充生成字段。
- `data/missing_book_candidates.json`：低置信度缺失候选池，不进入正式 `books.json`。

## 下一阶段路线图

- **Phase E**：补齐剩余 3 本书目缺口（需外部原始来源核对）；增强书籍元数据（ISBN、出版社等）；优化封面设计。

---

> 原始 README 历史背景保留：本项目最初创建于 2014 年，用于尝试使用 Markdown 写书。最初使用 multimarkdown 工具链，后因安装问题改为 pandoc。2024 年进行现代化升级，增加了网页版本和 Makefile 构建入口。
