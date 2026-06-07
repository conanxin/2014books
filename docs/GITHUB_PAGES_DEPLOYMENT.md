# GitHub Pages 部署说明

## 目录结构

`web/` 目录已准备为可直接发布的静态站点：

- `index.html` — 主页面（相对路径引用）
- `assets/style.css` — 样式表
- `data/books.json` — 结构化书目数据
- `.nojekyll` — 禁用 Jekyll 处理（确保以纯静态文件方式服务）

## 发布方式

### 方式一：手动发布到 gh-pages 分支

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

### 方式二：GitHub Actions 自动部署（推荐，后续阶段实现）

后续可添加 `.github/workflows/pages.yml`，在 `push` 到 `master` 或指定分支时自动将 `web/` 内容部署到 `gh-pages`。

本阶段暂不自动部署，仅提供构建检查工作流。

## 访问地址

部署后可通过 `https://conanxin.github.io/2014books/` 访问。

## 注意事项

- 所有资源使用相对路径，不依赖外部 CDN
- 站点完全离线可用
- 无需构建工具，直接复制 `web/` 内容即可发布
