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

修复提交 `e6b6c2d3bcb5e5a72920425b6aa4d9edc96cf11f` 的 [Actions 43179213463](https://github.com/microarch-flow/wiki/actions/runs/43179213463) 构建和部署成功。独立验收对 18 个页面逐一 GET，均返回 200，搜索索引每页一条；15 篇正文的草稿状态及站内 KaTeX 脚本均在线可见。旧仓提交 [`3623210`](https://github.com/microarch-flow/roofline-to-runtime/commit/36232109a88624737571dd17cd874bd9ff92ba21) 在首页指向新位置，保留原稿和历史。

独立全站链接回归针对该批本地生成物检查了 17,309 次正文站内引用。旧站 798 个页面、正文锚点与既有站内媒体均保留，没有发现新增失效。该检查不覆盖外部网站、代码样式路径或 JavaScript 动态链接。

后续修复推理文章目录中的公式显示；目录锚点保持不变，无脚本时保留纯文本。桌面和 390 像素宽预览均检查了目录公式。

## B6：芯片架构实例

从 `chip-architecture-wiki@3086204c049a762eb59033f8141fba9e91f4c669` 导入五篇产品主文和一篇横向报告。纯导入提交为 `587affd793827b527cd4ed7b8e99b62d531f52d4`，六个文件的 Git blob 与来源一致。新系列首页和必要修复另行提交。

原文引用的 30 张图均登记原出处及许可状态，见[逐图台账](migration/chip-image-provenance.md)。转载许可未确认的图片没有复制到本站；正文保留说明及原发布资料链接。PDF、原始对话和网页快照留在原仓。Meta 图的第一代与第二代来源、Cerebras 的系统级与片上互连，以及报告中的旧附录路径已分别核对和标注。Graphcore 官方指南在核查时返回 502，原仓固定提交保存的指南可作为备查。

独立复核后，报告区分设备执行确定性与服务尾延迟，收窄 Graphcore BSP、Groq 跨芯片网络和 Cerebras wavelet 的结论，并将存在口径差异的 Graphcore 带宽标为待核对。Meta 第一代 DOI 本次检查返回 403，补充了原仓固定版本论文的备查链接。这些网络结果仅代表检查时的访问情况。

本地严格构建和 15 项测试通过；七篇系列页面的 112 条正文站内链接及片段检查通过。与 B0 对照，798 个旧页面、原锚点、相对引用和图片均保留，旧页面在搜索中各有一条记录。产品文章和横向报告中的商业判断及全部性能数字未逐项独立审阅。

主仓提交 `caa54d1c948956606e0b4daaa7180f6fa0ba5790` 的 [Actions 43181074308](https://github.com/microarch-flow/wiki/actions/runs/43181074308) 构建和部署成功。日志中的四个系列均来自主仓本地目录。独立验收确认七个系列入口、芯片实例首页和六篇正文均返回 HTTP 200；七个实例页面在搜索中各有一条记录，导航高亮与面包屑符合归属。旧仓提交 [`602f8e6`](https://github.com/microarch-flow/chip-architecture-wiki/commit/602f8e6bedb6d4960f7b1e580d704d80e7413b66) 在公开验收后更新首页，保留原文和历史。

对该提交独立干净检出的严格构建和 17 项测试通过。全站回归检查了 887 页和 17,423 条正文站内引用；相对于 B0，798 个旧页面、正文锚点及已引用的媒体没有缺失或变化，未发现失效的正文站内引用。这不等于逐一访问所有公开旧页面，也不涵盖外站链接和动态脚本产生的链接。

## B7：收尾与来源核对

| 批次 | 主仓关键提交 | 发布记录 |
| --- | --- | --- |
| B0 | `b6460bea23bd5109aa84d64e852f13f44486f0b3` | 基线记录 |
| B1 | `ba6ea1ee71398583e2e4f6082337d45019c7577e` | [Actions 43175284964](https://github.com/microarch-flow/wiki/actions/runs/43175284964) |
| B2 | `e1f5f08f15f49cb1dbc6b3ff6bd7e243bb0abe3a` | [Actions 43175496904](https://github.com/microarch-flow/wiki/actions/runs/43175496904) |
| B3 | `190d59b232845ee04bafb8f5d28c0d669646d624` | [Actions 43176610817](https://github.com/microarch-flow/wiki/actions/runs/43176610817) |
| B4 | `e0f99c35e6806c2cfc197fd3115d76ef2d296cf8` | [Actions 43177235541](https://github.com/microarch-flow/wiki/actions/runs/43177235541) |
| B5 | `24775eb7bff749f4070c82b55e154f9a5a3e952a`；部署修复 `e6b6c2d3bcb5e5a72920425b6aa4d9edc96cf11f` | [Actions 43179213463](https://github.com/microarch-flow/wiki/actions/runs/43179213463) |
| B6 | `ca9034a5a944609807db749ecf4bb08298cb1ebc`；复核及公式目录修复 `caa54d1c948956606e0b4daaa7180f6fa0ba5790` | [Actions 43181074308](https://github.com/microarch-flow/wiki/actions/runs/43181074308) |

| 来源仓 | 导入来源 | 首页指向新位置的提交 | 从来源到该提交的差异 |
| --- | --- | --- | --- |
| workload-wiki | `c71d7e7348f6e666c8ee4fb934472d3d85c5a460` | [`0e4e005`](https://github.com/microarch-flow/workload-wiki/commit/0e4e0056ed29ce2ffa2af24fa5199d767911c0d9) | 首页提示；移除重建通知工作流 |
| silicon-atlas | `6a384bb3d3b0d300d7e5c5bb1c3a2f66223ca7e3` | [`3ac30d7`](https://github.com/microarch-flow/silicon-atlas/commit/3ac30d72e24eea2eceed4462c4069753fe947947) | 仅首页提示 |
| roofline-to-runtime | `4c7fe5611899c4002a35c8f2fa8ea92fde391672` | [`3623210`](https://github.com/microarch-flow/roofline-to-runtime/commit/36232109a88624737571dd17cd874bd9ff92ba21) | 仅首页提示 |
| chip-architecture-wiki | `3086204c049a762eb59033f8141fba9e91f4c669` | [`602f8e6`](https://github.com/microarch-flow/chip-architecture-wiki/commit/602f8e6bedb6d4960f7b1e580d704d80e7413b66) | 仅首页提示 |

这些提交不删除旧仓和历史，也不将旧仓设为只读。主仓 Pages 原来已选择 GitHub Actions，保留默认域名和 HTTPS；主仓的 `main` 推送及手动运行均可部署。仓库级 webhook 和其他旧仓通知未发现专用绑定；账户外发送方及令牌使用范围不能由这次可见设置证明。Workload 的 `WIKI_DISPATCH_TOKEN` 仓库 secret 截至本记录尚未删除；该 secret 不再被现有通知工作流引用，清理和底层令牌撤销是不同操作。

## 待补专题的参考材料

下列专题尚无独立正文，不在主导航建立空入口。资料只能支持后续写作，不表示对应专题已完成。

| 待补专题 | 可参考的旧文或资料 |
| --- | --- |
| 模型图分区与执行后端 | [ONNX Runtime 执行后端](https://onnxruntime.ai/docs/execution-providers/)。可从后端能力查询与子图分配入手。 |
| 执行控制、依赖与同步 | [DMA 队列与完成](../DMA/wiki/04-programming-model/queues-doorbells-completions.md)。需另补跨引擎的启动与完成边界。 |
| 共享数据的缓存一致性与内存顺序 | [DMA 缓存一致性](../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)及 [AXI 属性与屏障](../BUS/wiki/04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)。二者仅覆盖局部案例。 |
| UCIe | [SerDes 芯粒与 D2D](../SERDES/wiki/08-system-applications/chiplet-and-d2d.md)及 [UCIe 规范](https://www.uciexpress.org/specifications)。正式案例需注明规范版本。 |
| CXL | [CXL 与 PCIe 的边界](../PCIE/wiki/07-advanced-topics/cxl-and-pcie-boundary.md)。需另补指定设备和协议的独立正文。 |
| UALink | [UALink 联盟规范](https://ualinkconsortium.org/specification/)。需指定版本并建立完整的通信案例。 |
| Groq TSP / LPU | [原仓固定提交的资料目录](https://github.com/microarch-flow/chip-architecture-wiki/tree/3086204c049a762eb59033f8141fba9e91f4c669/Groq_LPU)。需整理带出处的独立正文。 |
| Microsoft Maia 100 | [原仓固定提交的资料目录](https://github.com/microarch-flow/chip-architecture-wiki/tree/3086204c049a762eb59033f8141fba9e91f4c669/Microsoft_Maia_100)。需区分公开事实与未知细节。 |
