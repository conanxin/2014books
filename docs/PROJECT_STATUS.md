# 2014books 项目状态

## 项目当前能力矩阵

| 能力 | 状态 | 说明 |
|------|------|------|
| Markdown source | ✅ 可用 | 45 章 + 前言 + 附录，原始内容完整保留 |
| PDF | ✅ 可用 | pandoc + xelatex，含字体回退和文字封面 |
| EPUB | ✅ 可用 | pandoc 生成，兼容主流阅读器 |
| Web | ✅ 可用 | 纯静态站点，支持搜索，可离线使用 |
| GitHub Pages workflow | ✅ 已配置 | push 到 master 自动部署 |
| CI build check | ✅ 已配置 | `.github/workflows/build.yml` |
| Release package | ✅ 已配置 | `make release` 生成 zip |
| Metadata override framework | ✅ 已配置 | `data/book_metadata_overrides.json` |

## 阶段历史

### Phase A — 现代化构建和 Web 输出

- 新增 `Makefile`、`scripts/generate_web.py`
- 修复章节自然排序问题
- 生成静态网页，支持搜索
- 基线：从 0 到可构建 PDF + Web

### Phase B — PDF 加固和书目审计

- 修复 LaTeX 中文字体回退
- 处理封面缺失（条件判断 + 文字封面）
- 审计 100 vs 73 本书问题，优化解析器
- 书单从 73 提升到 **97 本**
- 基线：PDF 稳定构建，书目数量可验证

### Phase C — EPUB 输出和书目缺口审计

- 新增 EPUB 构建脚本
- 完成 Phase C 书目缺口审计报告
- 确认附录编号 1-97 连续，缺失 98-100
- 基线：PDF + Web + EPUB 三格式输出

### Phase D — Pages 自动部署、元数据增强和 Release Package

- 新增 GitHub Pages 自动部署工作流
- 建立书目元数据增强框架（overrides + candidates）
- 更新 Web 页面：项目状态区 + 待核实候选区
- 新增 `make release` 生成 release zip
- 更新 README 和部署文档
- 基线：完整 CI/CD + 元数据框架 + 可发布包

## 当前可信事实

- 仓库内可证明 **97 本** 书目，来自附录结构化解析。
- "100本" 为历史专题名称，非当前可验证数量。
- 缺失 3 本（编号 98-100）不能无证据补入正式书单。
- 缺失候选已单独隔离在 `data/missing_book_candidates.json`。

## 下一阶段建议（Phase E）

1. **补齐 3 本缺口**：对照原始《第一财经周刊》专题或可靠存档，确认缺失的 3 本书目。
2. **元数据填充**：通过人工/半人工方式，为 97 本书目补充出版社、出版年份、ISBN 等字段。
3. **封面优化**：设计更美观的文字封面或生成简单图形封面。
4. **自动化测试**：为 `scripts/generate_web.py` 添加单元测试，防止回归。
