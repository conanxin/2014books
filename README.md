2014年值得你阅读的100本书
========================

## 项目简介

本项目是 2014 年第一财经周刊专题「值得你阅读的100本书」的 Markdown 制书复刻。原始内容来自周刊网站，由 Conan Xin 整理为可编译的 Markdown 源码，并生成 PDF 小册子。

## 项目来源

- 原始专题：[第一财经周刊 · 值得你阅读的100本书](http://www.cbnweek.com/v/subject?id=22)
- 整理者：Conan Xin
- 源码仓库：https://github.com/conanxin/2014books

## 现在可以生成 PDF 和 Web

本项目已从原始的单一脚本构建升级为支持多种输出格式：

- **PDF**：通过 `pandoc` + `xelatex` 生成排版精美的中文 PDF
- **静态网页**：通过 Python 标准库生成可离线浏览的静态网页，支持搜索和筛选

## 本地构建方法

### 依赖安装（Ubuntu/Debian）

```bash
sudo apt-get install pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra
sudo apt-get install ttf-wqy-microhei ttf-wqy-zenhei
```

### 构建命令

```bash
# 生成 PDF
make pdf

# 生成静态网页
make web

# 同时生成 PDF 和网页
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
├── template/          # LaTeX 模板文件
├── latex/             # LaTeX 构建工作目录
├── scripts/           # 现代构建脚本
│   ├── build_pdf.sh   # PDF 构建入口
│   └── generate_web.py # 静态网页生成器
├── web/               # 生成的静态网页输出
│   ├── index.html
│   ├── assets/style.css
│   └── data/books.json
├── dist/              # 生成的 PDF 输出
│   └── 2014books.pdf
├── mmd2bok            # 传统 PDF 构建脚本（已修复章节排序）
├── Makefile           # 现代构建入口
└── README.md          # 本文件
```

## 已知限制

1. **PDF 字体依赖**：需要系统中安装 WenQuanYi 系列中文字体，否则 xelatex 编译可能失败
2. **封面图片**：模板中引用的 `img/cover.pdf` 需要自行准备，当前仓库中可能缺失
3. **网页搜索**：静态网页的搜索功能为前端 JavaScript 实现，无需后端服务，但仅支持当前页面已加载的内容
4. **章节排序**：已修复原始脚本中 `1-chapter10` 排在 `1-chapter2` 之前的排序问题

## 下一阶段路线图

- **Phase B**：修复 LaTeX 模板中的字体和布局问题，优化中文排版
- **Phase C**：增加 EPUB 电子书输出支持
- **Phase D**：完善封面生成和书籍元数据（ISBN、出版社等）结构化

---

> 原始 README 历史背景保留：本项目最初创建于 2014 年，用于尝试使用 Markdown 写书。最初使用 multimarkdown 工具链，后因安装问题改为 pandoc。2024 年进行现代化升级，增加了网页版本和 Makefile 构建入口。
