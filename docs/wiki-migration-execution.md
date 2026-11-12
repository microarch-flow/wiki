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

公开验收后，旧仓提交 [`0e4e005`](https://github.com/microarch-flow/workload-wiki/commit/0e4e0056ed29ce2ffa2af24fa5199d767911c0d9) 删除重建通知工作流，并在旧首页标明新维护位置。源正文与历史保留。该次推送后，旧仓 Actions 运行列表没有出现新的通知运行；主仓也没有新的 `repository_dispatch` 运行。专用 secret 和接收监听尚需在最终核对后处理。

## B3：原位重排主导航

保留旧文章路径，将计算、DMA 和 CIM 归入微架构，将 RAM、HBF 和数据放置文章归入存储系统，将 BUS、NoC、PCIe、SerDes 和 CPO 归入互连。FAB 在 B4 与芯片开发系列合流。四篇 HBM 文章按文件例外归入 HBM 专题。Workload 的基础组件也按结构、训练目标和生成分别设置主专题。待补专题不建立空入口。

构建检查主导航不能重复。与 B0 对照，798 个旧页面、原正文锚点、相对引用和 20 个图片资源均保留，搜索索引中每个旧页面各有一条页面记录。严格构建和导航测试结果以该批提交前的记录为准。
