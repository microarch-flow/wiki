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
