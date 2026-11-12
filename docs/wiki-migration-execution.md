# 五库迁移执行记录

## B0：切换前基线

2026-11-12 核对时，五个仓库的本地 `main` 与 GitHub `main` 相同。四个来源仓没有未提交文件。主仓有未跟踪的讨论稿和本地对话记录；本次隔离检出不包含这些文件。

| 仓库 | 切换前完整提交 |
| --- | --- |
| wiki | `b41c501b561f3953ff1f8f7c3862ca61adb8a6f4` |
| workload-wiki | `c71d7e7348f6e666c8ee4fb934472d3d85c5a460` |
| silicon-atlas | `6a384bb3d3b0d300d7e5c5bb1c3a2f66223ca7e3` |
| roofline-to-runtime | `4c7fe5611899c4002a35c8f2fa8ea92fde391672` |
| chip-architecture-wiki | `3086204c049a762eb59033f8141fba9e91f4c669` |

主站 Pages 来源是 GitHub Actions。默认域名为 `microarch-flow.github.io`，没有自定义域名，HTTPS 为强制状态。最后一次成功部署是 [Actions 43032390031](https://github.com/microarch-flow/wiki/actions/runs/43032390031)，主仓提交为 `b41c501b561f3953ff1f8f7c3862ca61adb8a6f4`。其构建日志记录 Workload 的实际提交为 `c71d7e7348f6e666c8ee4fb934472d3d85c5a460`。

用这两个提交的干净检出重建旧站：严格构建通过，8 项现有测试通过。构建有 8 条关于 COMPUTE 目录链接的 INFO，无 WARNING 或 ERROR。基线包含 798 个页面和 20 个图片资源。机器可读的页面地址、正文锚点、相对引用、正文散列及图片散列保存在 [基线清单](migration/baseline-inventory.json.gz)。该清单来自本地同 SHA 构建，不代表对每个线上页面均已访问。

## 切换前绑定盘点

| 来源 → 目标 | 用途 | 切换条件和验证 |
| --- | --- | --- |
| `wiki/website/series.json` → `workload-wiki:main` | 构建时拉取 Workload 正文 | B2 固定同一来源导入；对照旧 URL、正文、锚点、资源和搜索后切到仓内 |
| `workload-wiki/.github/workflows/rebuild-blog.yml` → `wiki` | 推送或手动触发 `content-updated` | 仓内版本独立部署并通过公开旧地址验收后退役 |
| `wiki/.github/workflows/pages.yml` → `repository_dispatch` | 接收 `content-updated` 并重建 | 核查已知发送方停用后移除监听，保留主仓 push 和手动触发 |
| `workload-wiki` repository secret `WIKI_DISPATCH_TOKEN` → 上述发送工作流 | 跨仓 dispatch 凭据 | 核对用途后，仅在工作流停用和公开验收后清理；不记录凭据值 |

五个仓库的 Webhook 设置均未显示仓库级 webhook。五个仓库的 Actions 变量均为空；除上述 Workload 仓库 secret 外，仓库级 Actions secrets 为空，设置页未列出环境 secrets。检查五库已跟踪的工作流和上述关键词，没有发现其他通知或内容拉取。GitHub Actions 历史中存在两次 `repository_dispatch` 成功运行。其他账号或未受检仓库可能持有能够发送事件的凭据；此项不能仅凭五库代码证明不存在。

旧仓提交历史和原始材料保留。实际导入提交、部署、切换与解绑结果在后续批次追加。

## B1：支持仓内来源

系列注册支持分别指定仓内源码目录和发布路径。现有外仓配置仍然可用。仓内来源只暂存 Markdown 和常见图片；已知维护文件、原始资料目录和其他附件不进入站点。其他 Markdown 需要在导入时逐项审查。暂存前检查符号链接、路径越界和全站输出冲突。

本地测试使用独立的 Git 测试源和仓内测试源，检查无远端拉取、发布路径、搜索记录、面包屑、维护文件排除和冲突失败。沿用旧来源配置的严格构建和 9 项测试通过。与 B0 的 798 个页面逐页比较，未发现页面缺失或正文散列变化。

## B2：Workload 迁入仓内

从 `workload-wiki@c71d7e7348f6e666c8ee4fb934472d3d85c5a460` 导入 70 个 Markdown 文件。纯导入提交为 `47c56c2926deb6c2735f49b461f17552dd4608ef`，逐文件 Git blob 均与来源一致。系列发布路径仍为 `external/workload-wiki/`。

切换前重新查询来源 `main`，提交没有变化。只用主仓源码准备站点，准备日志显示本地来源，没有旧仓拉取。严格构建和 9 项测试通过。与 B0 对照，798 个旧页面和 20 个图片资源均存在；正文散列、原锚点和正文相对引用没有变化。70 个 Workload 页面在搜索索引中各有一条页面记录。公开部署验收和旧通知退役分别记录。

主仓提交 `e1f5f08f15f49cb1dbc6b3ff6bd7e243bb0abe3a` 的 [Actions 43175496904](https://github.com/microarch-flow/wiki/actions/runs/43175496904) 构建和部署均成功。日志显示 `Staged series ... from local series/workload`。公开首页、Workload 首页、Attention 深链接和原 HBM 深链接均返回 HTTP 200，正文与该提交的干净检出构建结果一致。

公开验收后，旧仓提交 [`0e4e005`](https://github.com/microarch-flow/workload-wiki/commit/0e4e0056ed29ce2ffa2af24fa5199d767911c0d9) 删除重建通知工作流，并在旧首页标明新维护位置。源正文与历史保留。该次推送后，旧仓 Actions 运行列表没有出现新的通知运行；主仓也没有新的 `repository_dispatch` 运行。专用 secret 尚需单独处理。

独立审计检查了该账户可访问的 19 个仓库、共 21 条当前分支的完整 Git tree，未发现其他指向主站的发送工作流。主站 Actions 历史列出两次 `repository_dispatch`，均早于退役提交；旧仓通知日志与这两次运行的时间相吻合，但现有日志没有事件载荷，不能单凭时间证明来源。此审计不能排除账户外的服务或其他令牌持有者。已知发送方退役后，主站移除 `content-updated` 监听；`main` 推送和手动运行继续保留。移除监听后的[推送部署 43177596774](https://github.com/microarch-flow/wiki/actions/runs/43177596774) 和[手动部署 43177833460](https://github.com/microarch-flow/wiki/actions/runs/43177833460) 均成功。`WIKI_DISPATCH_TOKEN` 仓库 secret 的清理单独验收，不因此撤销底层令牌。

## B3：原位重排主导航

保留旧文章路径，将计算、DMA 和 CIM 归入微架构，将 RAM、HBF 和数据放置文章归入存储系统，将 BUS、NoC、PCIe、SerDes 和 CPO 归入互连。FAB 在 B4 与芯片开发系列合流。四篇 HBM 文章按文件例外归入 HBM 专题。Workload 的基础组件也按结构、训练目标和生成分别设置主专题。待补专题不建立空入口。

构建检查主导航不能重复。与 B0 对照，798 个旧页面、原正文锚点、相对引用和 20 个图片资源均保留，搜索索引中每个旧页面各有一条页面记录。严格构建和导航测试结果以该批提交前的记录为准。

主仓提交 `190d59b232845ee04bafb8f5d28c0d669646d624` 的 [Actions 43176610817](https://github.com/microarch-flow/wiki/actions/runs/43176610817) 部署成功。公开站点的存储、互连首页及 HBM、SRAM、NoC、DMA、SerDes 和 Workload 深链接均返回 HTTP 200，抽查的主导航归属与面包屑符合规则。HBM 页面在桌面和 390 像素宽预览中检查了布局。

独立审阅补充了 22 个公开深链接的主系列与专题抽查。根据审阅结果，后续提交 `a376a701e764e031d9d38946325daf9c2641ea67` 补齐“片上存储与数据供给”和“架构建模与性能分析”两条跨系列阅读路线；[推送部署](https://github.com/microarch-flow/wiki/actions/runs/43177596774) 成功，线上两个入口各包含三篇文章链接。

## B4：芯片开发流程与 FAB 合流

从 `silicon-atlas@6a384bb3d3b0d300d7e5c5bb1c3a2f66223ca7e3` 导入 62 个 Markdown 文件。纯导入提交为 `febebdc07974841c80882556f443082fead7b70d`，逐文件 Git blob 均与来源一致。原协作说明中的可信度、术语和引用要求提取到新目录的维护说明；原始任务说明留在旧仓。

FAB 页面原位保留，主导航迁至芯片开发与实现系列。DFT 页面链接晶圆筛测与终测；硅后良率和项目封装页面分别链接 FAB 的机制文章。新导入页面的 2,141 条站内正文链接及片段检查均通过。

严格构建和 10 项测试通过。与 B0 对照，798 个旧页面、原正文锚点和 20 个图片资源均保留，每个旧页面在搜索索引中各有一条页面记录。DFT、FAB 晶圆筛测、项目封装、FAB 封装和良率页面的主系列、专题与面包屑通过检查。切换前再次核对 silicon-atlas 的 `main`，来源提交没有变化。

主仓提交 `e0f99c35e6806c2cfc197fd3115d76ef2d296cf8` 的 [Actions 43177235541](https://github.com/microarch-flow/wiki/actions/runs/43177235541) 构建和部署成功。公开系列首页，以及 DFT、晶圆筛测、两种封装页面和两处良率页面均返回 HTTP 200，抽查的面包屑归属正确。

独立验收逐一检查了线上 82 个 FAB 页面和 62 个芯片开发流程页面：HTTP 状态均为 200，公开搜索索引中每页各有一条页面记录。静态导航检查确认这些页面各有一个主导航位置，计划中 10 项文件级例外均符合归属；DFT、封装和良率共 5 条跨专题链接可达。旧仓提交 [`3ac30d7`](https://github.com/microarch-flow/silicon-atlas/commit/3ac30d72e24eea2eceed4462c4069753fe947947) 在首页指向新维护位置，保留原文和历史。

## B5：推理运行时草稿

从 `roofline-to-runtime@4c7fe5611899c4002a35c8f2fa8ea92fde391672` 原样导入 18 个 Markdown 文件，纯导入提交为 `55798f2dbd4aeda4939b5f67dfe91e3b1d7dfb97`。随后单独修复 34 处术语表链接、1 处约定链接、15 个首页索引链接和 70B 权重算式。15 篇正文仍标为草稿。切换前重新核对来源 `main`，提交没有变化。

公式仅对推理系列启用本仓提供的 KaTeX；777 个公式通过解析。桌面与 390 像素宽预览检查了 KV 公式；超宽公式可通过触摸或键盘横向滚动。18 页的 607 个内部链接及片段检查通过。与 B0 对照，798 个旧页面、正文锚点、相对引用、图片及每页一条搜索记录均保留。

首次 [Actions 43178709425](https://github.com/microarch-flow/wiki/actions/runs/43178709425) 在 `mkdocs build` 失败，没有部署：命令行入口未把仓库根目录加入 Python 模块搜索路径。本地此前使用 `python -m mkdocs`，没有暴露该差异。修复后由已按文件路径加载的 MkDocs hook 注册本地扩展；在不设置 `PYTHONPATH` 的条件下，直接运行 `mkdocs build --strict` 和 14 项测试均通过，推理页仍有 777 个公式包装。

迁移中发现 03 的并发公式和单次卡顿到 p99 的推断，以及 06 的共享读取结论需要进一步核实。相关页面已标注待核实范围，问题与反例记录在 [推理草稿审阅记录](inference-runtime-migration-review.md)。这些检查不构成对草稿全文的技术审阅。
