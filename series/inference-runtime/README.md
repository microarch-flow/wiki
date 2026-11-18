# 推理运行时：从模型执行到在线服务

<div class="inference-legacy-anchors" aria-hidden="true"><span id="大模型推理与推理引擎-学习-wiki"></span></div>

推理运行时把模型计算变成可持续处理请求的系统。本系列以自回归 LLM 服务为主线，连接模型加载、算子执行、状态管理、调度、解码和分布式服务，并说明如何验证性能结论。

读者可以从一次请求的完整路径开始。涉及模型结构的数学基础链接到“算法与模型”；通用存储与通信机制分别链接到“存储系统”和“芯片与系统互连”。GPU 是主要示例平台，硬件相关结论均需保留其条件。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="单机服务栈-single-node-serving-stack"></span><span id="加速与扩展-acceleration-scale-out"></span><span id="应用层与收口-app-layer-synthesis"></span></div>

## 阅读顺序

1. [请求路径与服务指标](01-request-and-metrics/README.md)
2. [模型加载与执行计划](02-model-execution/README.md)
3. [算子内核与低精度执行](03-kernels-and-precision/README.md)
4. [运行时状态与 KV 管理](04-state-and-memory/README.md)
5. [批处理与请求调度](05-batching-and-scheduling/README.md)
6. [采样与解码控制](06-sampling-and-decoding/README.md)
7. [分布式执行与阶段分离](07-distributed-execution/README.md)
8. [服务生命周期与副本管理](08-serving-lifecycle/README.md)
9. [测量、建模与框架案例](09-measurement-and-cases/README.md)

<div class="inference-legacy-anchors" aria-hidden="true"><span id="地基-foundations"></span><span id="推荐阅读顺序"></span></div>

## 先建立主线，再深入机制

第一次阅读可沿一次请求的生命周期前进。

1. 从[完整请求路径](01-request-and-metrics/request-path.md)认清各模块的职责。
2. 先读 [Prefill 与 Decode 的阶段解释](01-request-and-metrics/01-prefill-decode.md#从自回归依赖到两个阶段)，再看[延迟、吞吐与 SLO](01-request-and-metrics/02-metrics-slo.md)。阶段篇的工作量和带宽推导可在第二遍阅读时回看。
3. 用[模型加载与执行后端](02-model-execution/model-loading.md)了解副本如何准备就绪。
4. 连读[状态与内存预算](04-state-and-memory/runtime-state.md)和[分页 KV](04-state-and-memory/06-paged-kv-cache.md)，看请求增长时怎样申请状态空间。
5. 在[连续批处理与分块 Prefill](05-batching-and-scheduling/04-dynamic-shape-batching.md)中手推 A、B 每轮的执行计划。
6. 在[采样、停止与输出](06-sampling-and-decoding/sampling-and-stopping.md)中跟踪 token 怎样变成用户收到的文本，再读[取消、故障与资源回收](08-serving-lifecycle/request-resource-lifecycle.md)，区分停止输出和归还资源的时刻。
7. 用[压测与性能定位](09-measurement-and-cases/benchmarking-and-profiling.md)确定测量口径，再到 [Trace 与事件模型](09-measurement-and-cases/trace-and-event-model.md)加入请求 C，复算等待时间和首 token 时延。

需要优化具体问题时，再进入 Attention 内核、量化、前缀复用、推测解码或多设备执行。分布式章节以单实例的状态和调度为基础。最后可用[容量与性能估算](09-measurement-and-cases/15-quantitative-estimation.md)把各项预算接起来。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="状态总览"></span></div>

## 内容状态与证据边界

本版包含 29 篇正文与 9 个专题导读。原有 15 篇保留主文并完成职责调整，新增或拆出 14 篇。正文区分来源事实、构造示例、条件估算和需要实测的结果。

公式复算与最小事件模型可在本地运行。它们验证算术和事件关系，不证明某个 GPU 配置满足 p99 SLO。框架案例固定源码版本，不提供未经同条件测试的性能排名。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="约定"></span></div>

## 查阅与维护

- [术语表](glossary.md)：跨专题共用概念与定义。
- [写作与建模约定](_conventions.md)：符号、单位、证据和状态边界。
- [测量、建模与框架案例](09-measurement-and-cases/README.md)：从验证方法到综合应用。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="决策记录-changelog"></span></div>

## 历史演进

- v0.1：初版 10 篇骨架。
- v0.2：加入指标、内核、量化、约束解码；将 PD 分离独立，并与 KV 卸载合写。
- v0.3：完成 15 篇初稿及一轮链接、符号和数字一致性检查，仍待技术审阅。
- v0.4：按请求与运行时职责组织九个专题；修正条件模型和统计口径，拆分形状与调度、专家并行、KV 分层存储，补齐执行、服务生命周期和验证。现有公开 URL 与锚点保留。
