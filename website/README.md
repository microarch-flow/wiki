# 网站构建与维护

Wiki 与博客的共同写作和设计要求见 [Wiki 与博客设计规则](../docs/wiki-blog-design-rules.md)。

本网站使用 MkDocs Material。首页汇集技术系列。主仓原有十一域的文章按微架构、存储系统、芯片与系统互连、芯片开发与实现分配主导航；FAB 与芯片开发流程在同一系列。“算法与模型（Workload Wiki）”的维护位置是本仓库的 `series/workload/`。`website/prepare.py` 将正文复制到 `.site-build/docs/`，然后 MkDocs 生成静态网站。导航按专题、章节和文章展开，当前页面高亮显示。文章开头的面包屑根据同一导航层级生成；已有上级页面可以点击，没有首页的分组显示为文本。

导航由 `website/hooks.py` 根据目录与 Markdown 标题生成。章节首页中，如果“阅读顺序”或“接下来怎么读”包含指向同一目录文章的编号列表，导航优先使用该顺序；未列出的文章按文件名排序。网站构建时，如果文章开头的“上级”链接与面包屑中的上级页面相同，会在网页中省略该行；不同的链接和原始 Markdown 均保留。

`website/ownership.py` 指定原有文章、Workload 和芯片开发流程文章的主系列和主专题。按更具体的文件规则处理 HBM、FAB 良率等例外。文章可以从多个导读链接，但只能在主导航出现一次；构建会拒绝重复的主导航条目。新增文章时，检查其路径是否落在正确的规则内，并核对面包屑与阅读链接。

存储系统的源码和导航按相同的六个专题组织，省略 RAM、HBF 等来源名称造成的重复层级。HBM 阅读入口属于 DRAM 专题；HBM 的封装、成本与选型文章属于系统集成专题，两者通过正文链接关联。源码已迁入 `series/storage/` 下对应的专题目录；原发布网址保持不变。

“存储层级与数据路径”的导航按 `website/storage_navigation.py` 中的四组和阅读顺序生成。四组名称分别对应 `01-memory-hierarchy/` 下的 `01-system-basics/`、`02-access-paths/`、`03-performance/`、`04-npu-case/`。跨专题阅读路线、自测和参考资料位于 `series/storage/reading-and-reference/`，在网站中作为“查阅与练习”展示，不是第七个技术专题。

其他 RAM 章节的文章目录使用各章编号阅读列表中的链接文字作为短名称。完整文章标题保留在正文与悬停提示中。章节首页可在 Markdown 中添加 `<!-- nav-title: 短名称 -->`，为侧边导航和上级面包屑指定短名称。没有短名称时，继续使用文章标题。

侧边导航由 `website/assets/javascripts/navigation.js` 补充交互：当前章节首页的标题可以展开或收起其目录，其他标题仍跳转到对应页面；长标题在可悬停设备上显示省略号并提供完整标题提示。触屏设备保留换行，以便查看完整名称。

## 仓内来源与发布路径

原有专题的源码位置由 `website/source-layout.json` 指定，暂存时映射回原发布路径。存储系统的六个源码目录依次为 `01-memory-hierarchy/`、`02-sram/`、`03-dram/`、`04-dram-controller/`、`05-hbf/`、`06-system-integration/`；共享图片位于 `assets/`。系列首页由 `series/storage/README.md` 维护。历史维护资料保存在 `docs/archive/storage/`，不参与发布。

电路与时序文章及其图片目录也在 `website/source-layout.json` 中配置。调整源码目录或添加存储系统文章时，应同步检查映射和文章的导航归属；暂存目录中的旧路径保持不变。存储层级与数据路径的文章映射按文件记录，因此新增文章时需明确选择公开路径，并更新 `website/storage_navigation.py`。构建会检查来源覆盖、路径边界、导航分组和发布路径冲突，避免遗漏或重复发布文件。

跨专题的历史评审记录保存在 `docs/reviews/`，构建时暂存到 `reviews/`，保留原公开地址。评审页面不出现在网站导航和站内搜索结果中。目录中的 Markdown、第三轮盲测脚本和参考数据仍可通过原地址访问。评审结论对应当时的正文基线；打磨文章时，应结合当前正文和资料重新核对。

暂存时，构建根据实际复制的文件，将源码中指向其他已发布源码的相对链接转换到对应暂存路径；原文件不变。网站首页等模板中的 HTML URL 按最终站点路径编写，不执行此转换。改动链接或目录后，应分别检查仓库源码链接与生成网站链接。

`website/series.json` 可以为仓内系列分别指定源码目录和发布路径。例如，Workload 的源码是 `series/workload/`，发布路径仍为 `external/workload-wiki/`。芯片开发流程从 `series/chip-development/process/` 暂存，FAB 由十一域映射单独暂存。修改源码目录不必改变公开地址。仓内来源必须有唯一的 `README.md` 或 `index.md`；文章和图片留在所选目录内。构建会拒绝符号链接、路径越界及输出冲突，并排除 `AGENTS.md`、`task.md`、`wiki-plan.md`、`raw/`、`wiki.old/`、`seed/` 和非文章／图片附件。其他 Markdown 仍可能发布，加入仓内系列前必须逐项检查其公开范围。`series/` 是正文维护位置，`.site-build/` 是生成目录。

当前生产配置只使用本仓库的正文，不需要检出或联网读取旧来源仓库。仓内内容变更随主仓 `main` 推送发布。

## 可选：增加来自其他仓库的技术系列

网站使用 `website/series.json` 配置系列。若以后确需从其他仓库构建，可以在 `series` 数组中添加一个对象，例如：

```json
{
  "title": "示例系列",
  "description": "这个系列的一句简介。",
  "source": {
    "slug": "example-series",
    "repository": "example-owner/example-repository",
    "ref": "main",
    "directory": "docs/blog"
  }
}
```

这是配置格式示例，不代表已接入该仓库。`repository` 使用 GitHub 的 `owner/repository` 格式。`ref` 可以是分支、标签或完整提交 SHA；使用分支时，每次构建读取该分支当前版本，构建日志会记录实际取得的提交。`directory` 是相对于仓库根目录的目录。`slug` 是系列的稳定标识，只能使用小写英文字母、数字和连字符，不能与其他系列重复。系列标题不能重复，也不能使用现有导航名称“首页”“系列”或“微架构”。

构建时，`website/prepare.py` 获取指定版本，只将所选目录复制到临时构建目录。网站在首页和系列目录生成入口，并把文章加入统一导航、面包屑和搜索索引。其他仓库不需要单独发布 GitHub Pages。文章位于 `external/<slug>/` 下；**修改 slug 会改变该系列的 URL**。现有 Wiki 文章的路径不变。

选定的目录必须有且只有一个 `README.md` 或 `index.md` 作为系列首页。文章使用小写 `.md` 扩展名。子目录可以按同一方式设置首页；章节首页的编号阅读列表可决定同目录文章的导航顺序。请把文章引用的图片和其他文件放在选定目录内，并检查指向目录外文件的链接。外部 `source` 的跨仓库或目录外链接不会自动改写。构建时会拒绝符号链接，不会复制 `.git` 元数据；如果源文件与 Markdown 生成的页面占用同一输出路径，也会报错。

**公开范围以整个所选目录为准**：其中的文章和资源都可能发布。接入前应先确认目录内容适合公开；不要把密钥或不应公开的资料放入该目录。来源不可访问、目录缺失或首页不符合要求时，构建会失败，不会静默省略该系列。

配置外部 `source` 时，构建从 GitHub 通过 HTTPS 获取公开仓库。本地预览也可以使用已检出的目录，避免联网：

```text
本地来源目录/
├── example-series/          # 上述 slug 对应的仓库检出目录
└── another-series/          # 如果配置了第二个来源
```

```sh
python website/prepare.py --source-root /path/to/本地来源目录
mkdocs serve
```

使用 `--source-root` 时，每个外部系列都必须有对应的本地检出目录；构建使用目录中的实际文件，包括未提交的修改，不校验其是否与 `ref` 一致。正常发布流程则按 `ref` 从 GitHub 获取版本。私有仓库需要另外配置有读取权限的检出步骤和凭据，再让构建使用这些本地检出目录；当前 workflow 没有自动配置私有仓库凭据。

每个系列对象必须有 `title`、`description`，以及 `local`、`source`、`page`、`url` 中恰好一个。`page` 指向已放入构建目录的本地 Markdown 页面；`url` 指向独立网站的 HTTPS 地址。独立网站仍可添加入口，但其文章不会自动进入本网站的搜索索引。

总入口继续使用当前 `/wiki/` 路径。站点名称在 `mkdocs.yml` 的 `site_name` 中修改；首页会自动使用该名称。

## 本地预览

需要 Python 3.11 或 3.12，以及可访问 Python 包仓库的网络。首次运行：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-site.txt
python website/prepare.py
mkdocs serve
```

根据命令输出打开本地地址。编辑正文、存储系统系列首页、`website/home.md`、`website/series.md`、`website/microarchitecture.md`、`website/series.json`、`website/visuals.md` 或网站资源后，重新执行 `python website/prepare.py`，再启动或刷新预览。如果用本地检出替代配置中的外仓 `source`，重新执行时也要带上 `--source-root`；仓内 `local` 来源不需要该参数。`.site-build/` 是可重新生成的构建目录，不要直接在其中维护正文。

要只生成静态文件：

```sh
python website/prepare.py
mkdocs build
```

输出目录为 `.site-build/site/`。中文搜索使用 `jieba`；Mermaid 代码块由主题处理。没有联网的读者也可以使用已加载的网页和本地资源，实际离线能力仍取决于浏览器缓存与访问方式。

构建时，`website/hooks.py` 会根据自定义 CSS 和 JavaScript 的内容生成版本参数，避免新页面继续使用浏览器缓存的旧资源。

推理运行时草稿中的数学公式使用仓内 KaTeX 渲染，不依赖运行时访问外部 CDN。窄屏下的长公式可以横向滚动，并可通过键盘聚焦。其余系列的 Markdown 解析保持原有方式。

构建完成后，可以运行 `python -m unittest discover -s website/tests`，检查各页面的当前导航项和面包屑链接。

## 发布到 GitHub Pages

仓库管理员在 GitHub 仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。将网站配置和内容提交并推送到 `main` 后，`.github/workflows/pages.yml` 会构建并部署；也可以在 Actions 页面手动运行该 workflow。检查运行结果，以 GitHub 显示的部署地址为准。

主站的日常发布由本仓库 `main` 推送或手动运行 Pages workflow 触发。旧 Workload 仓库的通知工作流和主站的 `content-updated` 监听均已退役。旧仓的修改不会进入主站；请直接修改主仓内的正文。若以后配置新的外部来源，必须另外设计并审核其更新方式。

当前配置的预期地址是 `https://microarch-flow.github.io/wiki/`。若更换仓库或使用自定义域名，应调整 `mkdocs.yml` 中的 `site_url` 和 `repo_url`，并按 GitHub 的方式配置发布与域名。GitHub Pages 网站可能公开可访问，发布前请确认内容适合公开。

## 内容和图解

- 正文来源位于 `series/`；`wiki.old/`、`task.md`、`seed/` 和 `docs/archive/storage/` 不在网站构建范围内。
- 总首页维护在 `website/home.md`，系列目录维护在 `website/series.md`，微架构系列首页维护在 `website/microarchitecture.md`，存储系统系列首页维护在 `series/storage/README.md`，系列列表维护在 `website/series.json`。精选文章列表维护在 `website/articles.md`，互动图解维护在 `website/visuals.md`，图形与脚本位于 `website/assets/`。精选文章直接引用现有正文，后续可逐篇修改原文。
- 其余六个系列首页的封面图位于 `website/assets/images/series-covers/`，由 `website/hooks.py` 结合页面原有标题与导语生成。图片的替代文字和图注也在该文件维护；首页正文和原有链接仍由各系列的 Markdown 维护。
- DRAM 图解只表示一次显式 PRE 读流程的逻辑阶段，不给出周期数或替代器件规格。
- 双缓冲图解假设搬运和计算各占一个周期，且资源访问不冲突。它不代表实际设备的实测性能。
- 电路与时序文章维护在 `series/microarchitecture/foundations/electrical-timing-foundations.md`，原理图位于其相邻的 `img/`。暂存后仍使用原根文章和 `img/` 路径。公式区和路径卡片使用文中的 HTML 及 `site.css` 样式；构建时 `website/hooks.py` 只为该页添加阅读布局容器。公式不依赖外部脚本。
- 6T SRAM 文章通过 `website/hooks.py` 在正文标记处插入读写图解；模板位于 `website/partials/sram-demo.html`，状态与控制逻辑位于 `website/assets/javascripts/sram.js`。结构图和操作步骤都是教学示意，不是电路仿真。
- RAM 概览同样通过正文标记插入 cache miss 图解；模板为 `website/partials/ram-overview-demo.html`，状态与控制逻辑为 `website/assets/javascripts/ram-overview.js`。图解采用文章中列出的单请求假设。文章中的计算与事件路径使用 `site.css` 中的说明块样式。
- 修改图解时，同步检查状态文案、相关约束、链接，以及键盘操作和减少动态效果的设置。
