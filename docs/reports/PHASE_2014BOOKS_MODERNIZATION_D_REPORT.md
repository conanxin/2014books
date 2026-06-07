# PHASE_2014BOOKS_MODERNIZATION_D_REPORT.md

## STATUS

IN_PROGRESS — Phase D 实施中，等待最终 commit 和推送验证。

## HOST_SCOPE

WSL2 (Ubuntu) — 本地开发环境

## REPO_DIR

/home/conanxin/projects/2014books

## BRANCH

phase/2014books-modernization-d

## BASE_COMMIT

60e3d77 Phase C docs hotfix: finalize report metadata

## IMPLEMENTATION_COMMIT

4c94ec6a47bd7e1caaeab2e40da4d01861e9296f Phase D: add Pages deploy workflow and metadata framework

## FILES_CHANGED

- `.github/workflows/pages.yml` — 新增 GitHub Pages 自动部署工作流
- `docs/GITHUB_PAGES_DEPLOYMENT.md` — 更新部署文档，增加 Actions 自动部署说明
- `data/book_metadata_overrides.json` — 新增书目元数据增强入口
- `data/missing_book_candidates.json` — 新增缺失候选池（低置信度，不进入正式书单）
- `scripts/generate_web.py` — 更新：项目状态区、待核实候选区、CSS 增强
- `scripts/package_release.sh` — 新增 release package 打包脚本
- `Makefile` — 增加 `make release` 目标
- `README.md` — 更新：自动部署说明、项目结构、元数据增强、下一阶段路线
- `docs/PROJECT_STATUS.md` — 新增项目状态文档
- `docs/reports/PHASE_2014BOOKS_MODERNIZATION_D_REPORT.md` — 本报告

## DESIGN_RATIONALE

### 为什么添加 GitHub Actions 自动部署

Phase C 已确认 `web/` 目录为纯静态站点，具备自动部署条件。手动发布到 `gh-pages` 分支容易遗忘，且 phase 分支和 master 分支的部署策略需要区分。使用 GitHub 官方 `actions/deploy-pages@v4` 可以：

- 避免维护额外的 `gh-pages` 分支
- 只有 `master` push 才触发部署，phase 分支仅做构建验证
- `workflow_dispatch` 支持手动测试

### 为什么建立元数据增强框架

97 本书目目前只有 `id/title/author/raw/source/confidence`，缺少出版社、年份、ISBN 等字段。直接修改 `scripts/generate_web.py` 的生成逻辑会导致：

- 生成逻辑和人工增强数据耦合
- 无法追踪哪些字段是解析出来的、哪些是人工补充的
- 无法支持增量更新

因此引入 `data/book_metadata_overrides.json` 作为独立的人工/半人工入口，通过 `id` 匹配合并，保留原始证据字段，只覆盖非 null 字段。

### 为什么把缺失 3 本候选单独隔离

Phase C 审计已确认附录编号 1-97 连续，缺失 98-100。章节中存在 29 个"章节独有"书名，但：

- 部分已识别为附录条目的短标题变体
- 剩余部分无法直接对应到 98-100 的编号空缺
- 强行补入会污染正式 `books.json` 的可信度

因此建立 `data/missing_book_candidates.json`，明确标注 `should_add_to_books_json: false`，并在网页上显示为"待核实候选"，避免误导。

### 为什么使用 IMPLEMENTATION_COMMIT 而非 FINAL_COMMIT

Phase A/B/C 使用 `FINAL_COMMIT` 导致报告写入后需要二次 docs hotfix。Phase D 改用 `IMPLEMENTATION_COMMIT`：

- 报告在提交前写入占位符
- 主提交完成后，用实际 commit hash 替换占位符
- 如有需要，再追加一次 docs commit
- 避免循环依赖

## PAGES_WORKFLOW_STATUS

ADDED — `.github/workflows/pages.yml` 已添加，使用官方 actions：

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/configure-pages@v5`
- `actions/upload-pages-artifact@v3`
- `actions/deploy-pages@v4`

触发条件：`push` 到 `master`，`workflow_dispatch` 手动触发。

**注意**：需要在仓库 Settings → Pages → Source 中选择 "GitHub Actions" 才能生效。

## METADATA_FRAMEWORK_STATUS

ADDED — 新增 `data/` 目录：

- `book_metadata_overrides.json`：空数组，作为人工增强入口
- `missing_book_candidates.json`：3 条低置信候选，隔离于正式书单

`scripts/generate_web.py` 已更新：

- 读取 `data/missing_book_candidates.json`
- 在网页中渲染"项目状态"和"待核实候选"区域

## MISSING_BOOK_CANDIDATE_STATUS

ISOLATED — 3 条候选来自 Phase C 审计中的"章节独有"书目：

1. 《世界是平的》（chapter 2）
2. 《通用汽车的缔造者》（chapter 2）
3. 《总开关—信息帝国的兴衰变迁》（chapter 22）

全部标注 `confidence: low`，`should_add_to_books_json: false`。

## WEB_BUILD_STATUS

PASS — `python3 scripts/generate_web.py` 成功，生成：

- `web/index.html`
- `web/assets/style.css`
- `web/data/books.json`

页面包含：项目状态区、待核实候选区、搜索功能、章节目录。

## PDF_BUILD_STATUS

DEFERRED — 本阶段未修改 PDF 构建逻辑。Phase B 已修复字体回退和封面缺失，PDF 构建状态继承自 Phase C。

## EPUB_BUILD_STATUS

DEFERRED — 本阶段未修改 EPUB 构建逻辑。状态继承自 Phase C。

## RELEASE_PACKAGE_STATUS

ADDED — 新增 `scripts/package_release.sh` 和 `make release`：

- 执行 `make web`、`make epub`、`make pdf`
- 创建 `dist/release/2014books-phase-d-release.zip`
- 包含：PDF、EPUB、web/、README.md、部署文档、阶段报告

## CI_STATUS

PASS — `.github/workflows/build.yml` 继承自 Phase C，未修改。
新增 `.github/workflows/pages.yml` 待合并到 master 后验证。

## VALIDATION_RESULTS

- `bash -n mmd2bok`：PASS
- `bash -n scripts/build_pdf.sh`：PASS
- `bash -n scripts/build_epub.sh`：PASS
- `bash -n scripts/package_release.sh`：PASS
- `python3 -m py_compile scripts/generate_web.py`：PASS
- `python3 scripts/generate_web.py`：PASS（97 books）
- `make web`：PASS
- `test -f web/index.html`：PASS
- `test -f web/.nojekyll`：PASS
- `test -f web/data/books.json`：PASS
- `test -f .github/workflows/pages.yml`：PASS
- `test -f data/book_metadata_overrides.json`：PASS
- `test -f data/missing_book_candidates.json`：PASS
- `test -f docs/PROJECT_STATUS.md`：PASS

## PUSHED

No — 等待最终提交后推送。

## RECOMMENDED_NEXT_PHASE

**Phase E**：补齐剩余 3 本书目缺口（需外部原始来源核对）；增强书籍元数据（ISBN、出版社等）；优化封面设计。
