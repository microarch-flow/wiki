# 推理运行时重组与内容验收记录

日期：2026-11-17。范围：已确认的方案 B，九个专题、29 篇正文。本文记录内容变更、兼容方案与提交前验收；部署与公开站点结果在发布完成后报告。

## 结构与文章边界

源码位于 `series/inference-runtime/`。九个专题目录与博客侧栏一致。15 篇原文保留主文职责并重写，新增或拆出 14 篇；另有九个专题导读、系列首页、术语表和写作约定，共 41 个 Markdown 页面。

| 专题 | 文章 | 内容边界 |
|---|---|---|
| 请求路径与服务指标 | [完整请求路径](../series/inference-runtime/01-request-and-metrics/request-path.md)（新增） | 输入准备、准入、迭代、输出与清理的端到端关系 |
| 请求路径与服务指标 | [Prefill 与 Decode](../series/inference-runtime/01-request-and-metrics/01-prefill-decode.md) | 阶段的计算、KV 状态与资源需求；不凭阶段名称判断瓶颈 |
| 请求路径与服务指标 | [延迟、吞吐与 SLO](../series/inference-runtime/01-request-and-metrics/02-metrics-slo.md) | 测量边界、统计集合、分位数、联合达标与 goodput |
| 请求路径与服务指标 | [朴素引擎的瓶颈](../series/inference-runtime/01-request-and-metrics/03-naive-bottlenecks.md) | 预留容量、静态批处理和执行开销为何造成浪费 |
| 模型加载与执行计划 | [模型加载与执行后端](../series/inference-runtime/02-model-execution/model-loading.md)（新增） | 模型身份、权重与配置、后端能力、加载峰值与就绪条件 |
| 模型加载与执行计划 | [动态形状与数据布局](../series/inference-runtime/02-model-execution/dynamic-shapes.md)（拆出） | token 数、布局、padding、分桶与执行计划；调度另述 |
| 模型加载与执行计划 | [CPU 与设备协作](../series/inference-runtime/02-model-execution/host-device-execution.md)（新增） | 计划提交、stream/event、CUDA Graph、重叠与完成边界 |
| 算子内核与低精度执行 | [一般算子与融合](../series/inference-runtime/03-kernels-and-precision/operator-execution.md)（新增） | GEMM、归一化、融合、工作区及形状依赖的执行成本 |
| 算子内核与低精度执行 | [Attention 内核](../series/inference-runtime/03-kernels-and-precision/05-attention-kernels.md) | 在线 softmax、IO 复杂度、split-KV 与分页寻址 |
| 算子内核与低精度执行 | [低精度执行](../series/inference-runtime/03-kernels-and-precision/10-quantization.md) | 权重、激活、KV 的量化表示、内核开销与质量验证 |
| 运行时状态与 KV 管理 | [状态与内存预算](../series/inference-runtime/04-state-and-memory/runtime-state.md)（新增） | 权重、KV、工作区、元数据、输出缓冲及峰值重叠 |
| 运行时状态与 KV 管理 | [分页 KV](../series/inference-runtime/04-state-and-memory/06-paged-kv-cache.md) | 块分配、逻辑映射、引用、CoW 和回收 |
| 运行时状态与 KV 管理 | [前缀复用](../series/inference-runtime/04-state-and-memory/07-radix-prefix-reuse.md) | 缓存身份、前缀查找、引用保护、命中口径与节省工作 |
| 运行时状态与 KV 管理 | [KV 分层存储](../series/inference-runtime/04-state-and-memory/tiered-kv.md)（拆出） | 状态迁移、恢复、淘汰与传输关键路径；不与 PD 混写 |
| 批处理与请求调度 | [连续批处理与分块 Prefill](../series/inference-runtime/05-batching-and-scheduling/04-dynamic-shape-batching.md) | 每轮重组、token 配额及 Prefill/Decode 混排 |
| 批处理与请求调度 | [准入、抢占与公平性](../series/inference-runtime/05-batching-and-scheduling/08-scheduling.md) | 选择规则、状态增长、抢占代价、等待与服务目标 |
| 采样与解码控制 | [采样、停止与输出](../series/inference-runtime/06-sampling-and-decoding/sampling-and-stopping.md)（新增） | logits 处理、token 选择、EOS/停止串、流式输出与状态 |
| 采样与解码控制 | [推测解码](../series/inference-runtime/06-sampling-and-decoding/09-speculative-decoding.md) | 候选、验证、拒绝采样、提交回滚与成本条件 |
| 采样与解码控制 | [约束解码](../series/inference-runtime/06-sampling-and-decoding/13-constrained-decoding.md) | 语法状态、token 掩码、栈、EOS 和截断边界 |
| 分布式执行与阶段分离 | [TP、PP 与 DP](../series/inference-runtime/07-distributed-execution/11-cluster-parallelism.md) | 模型切分、副本、rank 布局、状态分片与通信依赖 |
| 分布式执行与阶段分离 | [MoE 专家并行](../series/inference-runtime/07-distributed-execution/moe-expert-parallelism.md)（拆出） | 路由、派发、合并、热点、专家容量及并行组组合 |
| 分布式执行与阶段分离 | [上下文并行](../series/inference-runtime/07-distributed-execution/context-parallelism.md)（新增） | 查询或 KV 位置切分、归一化合并与长上下文条件 |
| 分布式执行与阶段分离 | [PD 分离与 KV 交接](../series/inference-runtime/07-distributed-execution/12-pd-disaggregation.md) | 阶段所有权、首 token、传输、安装与端到端关键路径 |
| 服务生命周期与副本管理 | [路由与扩缩容](../series/inference-runtime/08-serving-lifecycle/routing-and-scaling.md)（新增） | 副本选择、缓存局部性、排队、冷启动、排空与升级 |
| 服务生命周期与副本管理 | [取消、故障与资源回收](../series/inference-runtime/08-serving-lifecycle/request-resource-lifecycle.md)（新增） | 请求终止、在途操作、幂等清理、背压和恢复状态 |
| 测量、建模与框架案例 | [压测与性能定位](../series/inference-runtime/09-measurement-and-cases/benchmarking-and-profiling.md)（新增） | 开环/闭环负载、冷热状态、错误统计、剖析及可复现条件 |
| 测量、建模与框架案例 | [Trace 与事件模型](../series/inference-runtime/09-measurement-and-cases/trace-and-event-model.md)（新增） | 请求输入、调度事件、成本表、模型不变量与独立校准 |
| 测量、建模与框架案例 | [框架源码剖析](../series/inference-runtime/09-measurement-and-cases/14-framework-comparison.md) | 固定版本的请求路径与模块职责；不提供未经测试的排名 |
| 测量、建模与框架案例 | [容量与性能估算](../series/inference-runtime/09-measurement-and-cases/15-quantitative-estimation.md) | Llama 3 70B / H100 条件算例；分开规格、假设、估算与实测 |

## 主要技术修正与去重

- 区分请求数、本轮 token 数和上下文长度。补齐标准全注意力的工作量，并说明 GQA、MLA、窗口与混合模型的公式边界。
- 修正容量利用率推导；区分当前 KV 载荷上限、后续增长空间、每 rank 预算与完整进程内存峰值。
- 区分共享存储、节省重算和 HBM 实测流量。缓存命中身份包含模型与执行语义；请求命中率和 token 加权命中率分别定义。
- 将动态形状与请求批处理分开。连续批处理不依赖分页 KV；padding 和分桶也可能改善执行计划复用。
- 说明 FlashAttention 的容量单位、查询形状与有限精度边界。补充在线归一化和跨分片合并关系。
- 区分单次停顿、请求内 token 间隔与总体 p99。分别达到两个 99% 指标，不保证联合达标率仍为 99%。
- 推测解码区分贪心一致、目标分布保持与任务质量接近，给出拒绝采样条件和代价；不将所有变体统称为无损。
- 约束解码区分有限状态与需要栈的语法，说明 token 边界、EOS、截断及语义正确性的限制。
- 删除 TP 必须使用节点内 NVLink 的通用约束；按实际 rank 网格处理 TP、PP、DP、EP 与 KV 复制。
- 拆分 PD 与 KV 分层，修正十进制/二进制单位，并显式处理首 token 所有权、交接和传输关键路径。
- 以原始 Llama 3 70B 的 8K 上下文为边界。70B 参数采用圆整值，带宽与计算效率均标为未校准假设，移除由单步估算直接推出实测 TTFT、TPOT 或 p99 的结论。
- 模型数学、通用存储与通信机制通过跨系列链接复用。框架文章按请求路径组织，不重复讲完整机制。

框架源码样本固定为 vLLM v0.12.0 V1 与 SGLang v0.5.6 SRT。七个具体源码入口已核对。标准、厂商文档与原始论文分散引用在对应正文；39 个非 GitHub 外部资料 URL 已逐项检查，均返回成功响应。

## 目录、导航与兼容

`website/inference.py` 维护九个专题和 15 条源码移动映射。旧文继续生成原 `series/inference-runtime/topics/` 公开页面，新增正文直接使用专题路径；不生成第二份旧文。

各专题导读的编号阅读列表决定文章顺序和导航短标题。构建检查缺失、重复、越界和错误归属。正文保留完整标题，侧栏、面包屑和当前项对应同一层级。

`website/tests/fixtures/inference-legacy.json` 从修改前提交 `49f5e56d5906e0065c96eb0712fc53be0da4de8e` 的实际 HTML 捕获 18 个原页面与 277 个正文 DOM 锚点。正文兼容锚点位于相关新章节或拆分后的阅读入口附近。测试要求每个旧锚点在原 URL 中恰好出现一次。

两篇相邻文章仅调整受影响链接与过期的草稿说明；历史迁移评审保留正文，将旧源码链接固定到评审所对应的历史提交。没有删除历史评审或改写范围外正文。

## 提交前验收

1. `python website/prepare.py` 和 `mkdocs build` 成功，无构建警告。
2. 全站 95 项回归测试通过。最终表头调整及测试清理后，11 项推理专项测试再次通过。
3. 复算脚本的九项检查通过，覆盖容量、传输单位、分位数、联合 SLO、拒绝采样、推测收益、条件算例和事件不变量。
4. 41 页的源码链接、生成页面内部链接、导航、面包屑、canonical URL 与搜索索引通过检查。18 个历史 URL 与 277 个锚点保留，无重复 ID。
5. 浏览器检查全部 41 页的 1440 px 桌面与 390 px 手机视图，无文档级横向溢出或公式渲染错误。短化估算表头后，手机可直接读取三列数据；长公式可聚焦并用方向键横向滚动。
6. 实际操作检查手机菜单、当前项高亮、章节跳转、旧文章搜索和新增文章精确搜索。三张纵向流程图在窄屏可读。

教学事件模型处理三条构造请求，输出八轮执行、九个 token，结束时间为 10.943 ms。该结果验证模型定义，不代表 GPU 执行耗时。

## 保留事项与验证边界

原有未跟踪资料和动画目录保留，不纳入本次提交。生成目录、临时日志与浏览器截图不作为正文源码提交。

本次没有运行目标 GPU 的框架性能测试、量化质量测试或生产负载 p99 验收。效率系数、缓存收益和并行加速仍需按正文方法在指定硬件、模型和负载上校准。源码入口核对、公式复算、浏览器验收与硬件性能验收是不同证据。
