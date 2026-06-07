# GitHub Pages 部署说明

## 目录结构

`web/` 目录已准备为可直接发布的静态站点：

- `index.html` — 主页面（相对路径引用）
- `assets/style.css` — 样式表
- `data/books.json` — 结构化书目数据
- `.nojekyll` — 禁用 Jekyll 处理（确保以纯静态文件方式服务）

## 发布方式

### 方式一：GitHub Actions 自动部署（推荐）

仓库已配置 `.github/workflows/pages.yml`，支持以下触发方式：

- `push` 到 `master` 分支时自动部署
- `workflow_dispatch` 手动触发部署

#### 启用步骤

1. 打开仓库 GitHub 页面 → Settings → Pages
2. Build and deployment → Source: 选择 **GitHub Actions**
3. 保存后，下次 push 到 master 或手动触发 workflow 即可自动部署

#### 预期访问地址

https://conanxin.github.io/2014books/

#### 如果页面 404

- 检查 Pages 是否已在 Settings → Pages 中启用
- 检查 Actions 标签页中 workflow 是否成功运行
- 确认 `web/index.html` 存在且构建步骤未报错
- 确认已合并到 `master` 分支（phase 分支不自动部署）

### 方式二：手动发布到 gh-pages 分支

```bash
cd /path/to/2014books
git checkout --orphan gh-pages
git rm -rf .
cp -r web/* .
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

然后在仓库 Settings → Pages 中选择 "Deploy from a branch" → `gh-pages`。

## 当前工作流说明

- phase 分支仅验证构建，不直接发布到 Pages
- 只有 `master` 分支的 push 会触发自动部署
- 手动触发 `workflow_dispatch` 可用于测试部署流程

- 所有资源使用相对路径，不依赖外部 CDN
- 站点完全离线可用
- 无需构建工具，直接复制 `web/` 内容即可发布
