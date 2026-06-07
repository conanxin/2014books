# PHASE_2014BOOKS_MAGAZINE_REDESIGN_E_REPORT.md

## STATUS

IN_PROGRESS — Phase E 实施中，等待最终 commit 和推送验证。

## HOST_SCOPE

WSL2 (Ubuntu) — 本地开发环境

## REPO_DIR

/home/conanxin/projects/2014books

## BRANCH

phase/2014books-magazine-redesign-e

## BASE_COMMIT

3d241b4 Merge pull request #3 from conanxin/phase/2014books-modernization-d

## IMPLEMENTATION_COMMIT

(To be filled after implementation commit)

## DESIGN_PROBLEMS_IDENTIFIED

1. **信息层级扁平**：所有内容挤在一个长页面里，没有封面区、导语区、分区节奏。用户打开页面看到的是章节目录和搜索框，缺乏"这是一本特刊"的仪式感。
2. **视觉语言偏后台工具风**：圆角卡片、阴影、蓝色按钮——适合 SaaS 产品，不适合阅读体验。页面看起来像数据管理后台，而不是一本可以读的书。
3. **章节之间无区分度**：45 章全部以相同卡片样式堆叠，没有重点章节引导，也没有快速浏览的摘要。
4. **书单和正文混排**：每章末尾的书单卡片和正文挤在一起，阅读流被打断。
5. **状态信息过于技术化**："当前已结构化整理 97 本"像系统日志，不像编辑导语。
6. **字号偏小、行高保守**：正文 16px 在桌面端阅读偏累，段落间距不足，模块之间缺乏呼吸感。
7. **无阅读焦点**：没有 hero 区吸引注意力，没有 featured 内容引导深入，用户不知道从哪里开始。
8. **搜索是唯一交互**：除了搜索，用户只能滚动。没有锚点快速跳转、没有返回顶部、没有视图切换。
9. **移动端只是缩小版**：没有针对小屏幕重新编排信息优先级。

## DESIGN_GOALS

1. 页面风格从普通静态页升级为"杂志风 / 年度阅读特刊风"。
2. 强化阅读体验，而不是只做视觉装饰。
3. 保持内容可信：正式书单仍为 97 本，候选书目继续独立隔离。
4. 不引入外部 CDN，不引入复杂前端框架。
5. 保持静态站点生成方式：scripts/generate_web.py 负责生成。
6. 保持移动端可读。

## INFORMATION_ARCHITECTURE_CHANGES

重构首页为以下结构：

1. **杂志封面区 / Hero Masthead**
   - 杂志式标题区：主标题 + 副标题 + 简洁导语
   - 状态 badge：已结构化整理 97 本 / PDF · EPUB · Web / 原始专题复刻
   - CTA：开始阅读 / 浏览书单

2. **编辑导语区（Editor's Note）**
   - 简短说明项目来源、97 本事实、缺失 3 本需核对
   - 文案有编辑感，不像技术报告

3. **Featured Chapters 区**
   - 选 6 篇代表章节做大卡片（均匀分布）
   - 每张卡片显示：章节序号（大号）、标题、摘要、阅读入口

4. **Chapters Archive 区**
   - 45 章完整目录
   - 每项显示：章节编号（大号）、标题、简短摘要
   - 点击标题跳转至正文

5. **Book Archive 区**
   - 正式 97 本书目
   - 实时搜索（oninput 触发）
   - 每本书显示：书名、作者、出版社/价格标签
   - 无结果提示

6. **Research Appendix 区**
   - 显示 missing candidates
   - 明确说明："以下为待核实候选，不可直接视为正式书单第98–100条"
   - 视觉上与正式书单明显区分（暖黄背景 + 棕色边框）

7. **完整正文区（Full Text）**
   - 按章节顺序呈现全部正文
   - 每章末尾附该章推荐书目
   - 大号章节编号作为视觉锚点

8. **Footer / 项目尾注**
   - 项目来源、GitHub repo、PDF/EPUB/Release、Pages 状态

## VISUAL_SYSTEM_CHANGES

### 配色
- 背景：暖白纸张色 `#faf8f3`
- 正文：深灰黑 `#1a1a1a`
- 辅助色：暗红 `#8b3a3a`（克制使用，避免过亮蓝色）
- 边框：浅灰 `#d8d4cc`
- 警告区：暖黄背景 `#fff8f0` + 棕色边框

### 字体栈
- 标题：`Noto Serif CJK SC` / `Source Han Serif SC` / `STSong` / serif
- UI / 辅助文字：系统无衬线栈（`-apple-system`, `PingFang SC`, `Microsoft YaHei`）
- 不依赖外部字体加载

### 阅读排版
- 正文 `font-size: 17px`，`line-height: 1.85`
- 阅读区 `max-width: 860px`
- 段落和模块之间留白更充足
- 章节阅读区 `padding: 2.5rem 2rem`

### 杂志感元素
- 细线分隔（`section-divider`）
- 小号栏目标题（`section-label`，全大写 + 宽字距）
- issue-like 标识（`Annual Reading Special · 2014`）
- 大号章节编号（`featured-card .chapter-num: 2.5rem`，`archive-num: 1.8rem`）
- 卡片阴影非常轻（`rgba(0,0,0,0.04)`），避免产品后台风
- 顶部 sticky 导航 + 回到顶部按钮

### 响应式
- 桌面端：featured 双栏、book grid 多栏
- 移动端（`max-width: 700px`）：单栏、导航链接隐藏、字号略降、padding 收紧

## READABILITY_IMPROVEMENTS

1. **章节摘要自动生成**：`extract_summary()` 从正文首段提取，截断至 120 字符，优先在句子/分句边界处截断。
2. **分层阅读路径**：hero → editor's note → featured → archive → books → full text，用户可快速定位兴趣点。
3. **Sticky 顶部导航**：滚动时始终可见，含快速锚点跳转。
4. **回到顶部按钮**：滚动超过 600px 时显示，平滑滚动。
5. **打印友好**：footer 含打印链接，CSS 已优化打印表现。
6. **搜索优化**：oninput 实时搜索，无结果时显示提示。

## WEB_BUILD_STATUS

PASS — `python3 scripts/generate_web.py` 成功，生成：
- `web/index.html`（2719 行）
- `web/assets/style.css`（570 行）
- `web/data/books.json`（97 books）

页面包含所有规划区域：hero、editor's note、featured chapters、archive、book archive、research appendix、full text、footer。

## PDF_COMPATIBILITY_STATUS

PASS — `make pdf` 未受影响，PDF 构建逻辑未修改。

## EPUB_COMPATIBILITY_STATUS

PASS — `make epub` 未受影响，EPUB 构建逻辑未修改。

## VALIDATION_RESULTS

- `bash -n mmd2bok`：PASS
- `bash -n scripts/build_pdf.sh`：PASS
- `bash -n scripts/build_epub.sh`：PASS
- `bash -n scripts/package_release.sh`：PASS
- `python3 -m py_compile scripts/generate_web.py`：PASS
- `python3 scripts/generate_web.py`：PASS（97 books, 45 chapters）
- `make web`：PASS
- `make pdf`：PASS
- `make epub`：PASS
- `test -f web/index.html`：PASS
- `test -f web/assets/style.css`：PASS
- `test -f web/data/books.json`：PASS
- `grep -c "hero" web/index.html`：PASS（3）
- `grep -c "featured-grid" web/index.html`：PASS（1）
- `grep -c "archive-list" web/index.html`：PASS（1）
- `grep -c "book-grid" web/index.html`：PASS（1）
- `grep -c "research-appendix" web/index.html`：PASS（2）
- `grep -c "back-to-top" web/index.html`：PASS（1）
- `grep -c "top-nav" web/index.html`：PASS（1）

## PUSHED

No — 等待最终提交后推送。

## RECOMMENDED_NEXT_PHASE

**Phase F**：补齐剩余 3 本书目缺口（需外部原始来源核对）；增强书籍元数据（ISBN、出版社等）；优化封面设计。
