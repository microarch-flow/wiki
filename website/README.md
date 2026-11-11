# 网站构建与维护

本网站使用 MkDocs Material。网站内容来自仓库中九个专题的 `wiki/` 目录，并保留原始 Markdown 文件。`website/prepare.py` 将当前正文、专题自测、评审记录和网站资源复制到 `.site-build/docs/`，然后 MkDocs 生成静态网站。导航列出专题和章节；章节正文与站内搜索提供文章入口。

## 本地预览

需要 Python 3.11 或 3.12，以及可访问 Python 包仓库的网络。首次运行：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-site.txt
python website/prepare.py
mkdocs serve
```

根据命令输出打开本地地址。编辑原始 wiki、`website/home.md`、`website/visuals.md` 或网站资源后，重新执行 `python website/prepare.py`，再启动或刷新预览。`.site-build/` 是可重新生成的构建目录，不要直接在其中维护正文。

要只生成静态文件：

```sh
python website/prepare.py
mkdocs build
```

输出目录为 `.site-build/site/`。中文搜索使用 `jieba`；Mermaid 代码块由主题处理。没有联网的读者也可以使用已加载的网页和本地资源，实际离线能力仍取决于浏览器缓存与访问方式。

## 发布到 GitHub Pages

仓库管理员在 GitHub 仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。将网站配置和内容提交并推送到 `main` 后，`.github/workflows/pages.yml` 会构建并部署；也可以在 Actions 页面手动运行该 workflow。检查运行结果，以 GitHub 显示的部署地址为准。

当前配置的预期地址是 `https://microarch-flow.github.io/wiki/`。若更换仓库或使用自定义域名，应调整 `mkdocs.yml` 中的 `site_url` 和 `repo_url`，并按 GitHub 的方式配置发布与域名。GitHub Pages 网站可能公开可访问，发布前请确认内容适合公开。

## 内容和图解

- 九个 `wiki/` 是正文来源；`wiki.old/`、`task.md` 和 `seed/` 不在网站构建范围内。
- 首页维护在 `website/home.md`，精选文章列表维护在 `website/articles.md`，互动图解维护在 `website/visuals.md`，图形与脚本位于 `website/assets/`。精选文章直接引用现有正文，后续可逐篇修改原文。
- DRAM 图解只表示一次显式 PRE 读流程的逻辑阶段，不给出周期数或替代器件规格。
- 双缓冲图解假设搬运和计算各占一个周期，且资源访问不冲突。它不代表实际设备的实测性能。
- 修改图解时，同步检查状态文案、相关约束、链接，以及键盘操作和减少动态效果的设置。
