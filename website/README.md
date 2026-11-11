# 网站构建与维护

Wiki 与博客的共同写作和设计要求见 [Wiki 与博客设计规则](../docs/wiki-blog-design-rules.md)。

本网站使用 MkDocs Material。首页汇集技术系列；当前的“芯片微架构笔记”系列来自本仓库中九个专题的 `wiki/` 目录，并保留原始 Markdown 文件。`website/prepare.py` 将当前正文、专题自测、评审记录和网站资源复制到 `.site-build/docs/`，然后 MkDocs 生成静态网站。导航按专题、章节和文章展开，当前页面高亮显示。文章开头的面包屑根据同一导航层级生成；已有上级页面可以点击，没有首页的分组显示为文本。

导航由 `website/hooks.py` 根据目录与 Markdown 标题生成。章节首页中，如果“阅读顺序”或“接下来怎么读”包含指向同一目录文章的编号列表，导航优先使用该顺序；未列出的文章按文件名排序。网站构建时，如果文章开头的“上级”链接与面包屑中的上级页面相同，会在网页中省略该行；不同的链接和原始 Markdown 均保留。

RAM 专题的文章目录使用各章编号阅读列表中的链接文字作为短名称，完整文章标题保留在正文与悬停提示中。章节首页可在 Markdown 中添加 `<!-- nav-title: 短名称 -->`，为侧边导航和上级面包屑指定短名称。没有短名称时，继续使用文章标题。

侧边导航由 `website/assets/javascripts/navigation.js` 补充交互：当前章节首页的标题可以展开或收起其目录，其他标题仍跳转到对应页面；长标题在可悬停设备上显示省略号并提供完整标题提示。触屏设备保留换行，以便查看完整名称。

## 增加技术系列

在 `website/series.json` 的 `series` 数组中添加一个对象。首页和“系列”目录的卡片都由此文件生成，顶部“系列”导航直达该目录。名称和简介可以随时修改。现有系列使用 `page` 指向本网站中的 Markdown 页面；独立仓库发布后，可以使用 `url` 指向其 HTTPS 地址，例如：

```json
{
  "title": "新系列名称",
  "description": "这个系列的一句简介。",
  "url": "https://example.com/series/"
}
```

示例只是格式，不会自动创建或发布新网站。每个对象必须填写 `title`、`description`，以及 `page` 或 `url` 中的一个；`page` 指向已放入构建目录的 Markdown 页面。新增独立仓库时，需要先构建并发布该仓库的网站，再在这里填写它的公开地址。本网站的搜索索引只覆盖本仓库构建的页面，不会自动搜索其他网站。

目前聚合首页仍由本仓库发布在 `/wiki/` 路径下；独立系列可以继续使用各自的地址。若将来需要独立的总入口或跨仓库统一搜索，需要另行设计。站点的暂定名称在 `mkdocs.yml` 的 `site_name` 中修改；首页会自动使用该名称。

## 本地预览

需要 Python 3.11 或 3.12，以及可访问 Python 包仓库的网络。首次运行：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-site.txt
python website/prepare.py
mkdocs serve
```

根据命令输出打开本地地址。编辑原始 wiki、`website/home.md`、`website/series.md`、`website/microarchitecture.md`、`website/series.json`、`website/visuals.md` 或网站资源后，重新执行 `python website/prepare.py`，再启动或刷新预览。`.site-build/` 是可重新生成的构建目录，不要直接在其中维护正文。

要只生成静态文件：

```sh
python website/prepare.py
mkdocs build
```

输出目录为 `.site-build/site/`。中文搜索使用 `jieba`；Mermaid 代码块由主题处理。没有联网的读者也可以使用已加载的网页和本地资源，实际离线能力仍取决于浏览器缓存与访问方式。

构建时，`website/hooks.py` 会根据自定义 CSS 和 JavaScript 的内容生成版本参数，避免新页面继续使用浏览器缓存的旧资源。

构建完成后，可以运行 `python -m unittest discover -s website/tests`，检查各页面的当前导航项和面包屑链接。

## 发布到 GitHub Pages

仓库管理员在 GitHub 仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。将网站配置和内容提交并推送到 `main` 后，`.github/workflows/pages.yml` 会构建并部署；也可以在 Actions 页面手动运行该 workflow。检查运行结果，以 GitHub 显示的部署地址为准。

当前配置的预期地址是 `https://microarch-flow.github.io/wiki/`。若更换仓库或使用自定义域名，应调整 `mkdocs.yml` 中的 `site_url` 和 `repo_url`，并按 GitHub 的方式配置发布与域名。GitHub Pages 网站可能公开可访问，发布前请确认内容适合公开。

## 内容和图解

- 九个 `wiki/` 是正文来源；`wiki.old/`、`task.md` 和 `seed/` 不在网站构建范围内。
- 总首页维护在 `website/home.md`，系列目录维护在 `website/series.md`，微架构系列首页维护在 `website/microarchitecture.md`，系列列表维护在 `website/series.json`。精选文章列表维护在 `website/articles.md`，互动图解维护在 `website/visuals.md`，图形与脚本位于 `website/assets/`。精选文章直接引用现有正文，后续可逐篇修改原文。
- DRAM 图解只表示一次显式 PRE 读流程的逻辑阶段，不给出周期数或替代器件规格。
- 双缓冲图解假设搬运和计算各占一个周期，且资源访问不冲突。它不代表实际设备的实测性能。
- 电路与时序文章维护在根目录的 `electrical-timing-foundations.md`，原理图位于根目录 `img/`。公式区和路径卡片使用文中的 HTML 及 `site.css` 样式；构建时 `website/hooks.py` 只为该页添加阅读布局容器。公式不依赖外部脚本。
- 6T SRAM 文章通过 `website/hooks.py` 在正文标记处插入读写图解；模板位于 `website/partials/sram-demo.html`，状态与控制逻辑位于 `website/assets/javascripts/sram.js`。结构图和操作步骤都是教学示意，不是电路仿真。
- RAM 概览同样通过正文标记插入 cache miss 图解；模板为 `website/partials/ram-overview-demo.html`，状态与控制逻辑为 `website/assets/javascripts/ram-overview.js`。图解采用文章中列出的单请求假设。文章中的计算与事件路径使用 `site.css` 中的说明块样式。
- 修改图解时，同步检查状态文案、相关约束、链接，以及键盘操作和减少动态效果的设置。
