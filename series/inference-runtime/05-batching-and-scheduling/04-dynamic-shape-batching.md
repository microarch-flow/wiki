# 连续批处理与分块 Prefill

<div class="inference-legacy-anchors" aria-hidden="true"><span id="04-动态-shape-与变长处理-dynamic-shape-variable-length-serving"></span></div>

上级：[本专题导读](README.md)

连续批处理在迭代边界调整批组成，分块 Prefill 则限制一次安排的输入工作。两者共同提高调度灵活性，但不会自动消除资源竞争或尾延迟。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="3-continuous-batchingiteration-级调度"></span></div>

## 批的生命周期可以短于请求

静态批通常在一组请求之间保持固定成员。连续批处理每轮根据可运行状态重新选择成员：已完成的退出，有条件的等待请求进入，暂停的请求暂不执行。

普通 Decode 请求每轮通常贡献一个输入 token；Prefill 请求可以贡献多个。混合批需要分别记录请求数、本轮 token 数、各请求的查询长度和历史 KV 长度。

连续批处理是调度机制。它可以与分页 KV 配合，也可以使用其他内存管理实现。[Orca](https://www.usenix.org/conference/osdi22/presentation/yu)的迭代级调度与[vAttention](https://arxiv.org/abs/2405.04437)的内存方案说明这两层不应绑定为必然依赖。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span></div>

## 一个两请求执行例子

构造请求 A、B，输入长度分别为 8、3，输出上限分别为 4、2。本轮输入 token 预算为 5；优先处理已进入 Decode 的请求，剩余预算按 A、B 顺序处理 Prefill。假设 Prefill 完成时采样首 token。

| 轮次 | A 的输入工作 | B 的输入工作 | 本轮新增输出 |
|---|---|---|---|
| 1 | Prefill 5 | 等待 | 无 |
| 2 | Prefill 3 | Prefill 2 | A 的第 1 个 token |
| 3 | Decode 1 | Prefill 1 | A 第 2 个、B 第 1 个 |
| 4 | Decode 1 | Decode 1 | A 第 3 个、B 第 2 个，B 完成 |
| 5 | Decode 1 | 已完成 | A 第 4 个，A 完成 |

表格表示逻辑依赖，不给各轮设定相同时间。预算没有用满的轮次，也不一定应为了凑满而延迟执行。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="4-chunked-prefill分块预填充"></span></div>

## 分块没有改变注意力语义

分块 Prefill 将输入位置分多轮处理。第一个块建立前缀状态，后续块的查询仍需访问允许的历史 KV。它不是把长输入切成互不相关的短请求。

减小块可以缩短一次不可让出的工作，但可能增加启动、调度和重复读状态的成本。过小的形状也可能降低矩阵乘效率。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-chunked-prefill-的-stall-上界与代价"></span><span id="3-实测收益论文报告值作量级参照"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## Token 预算不等于时间上限

同样安排 128 个查询 token，若它们对应的历史长度、阶段、头布局或并行通信不同，执行时间可以不同。更严格的延迟控制需要形状与状态相关的成本估计，并留出误差余量。

“优先 Decode”可减轻生成间隔抖动，但持续高负载下也可能延迟新请求。调度需明确 TTFT、ITL、吞吐和公平性的取舍。

Sarathi-Serve 研究分块 Prefill 与 Decode 的组织方式；论文的 stall-free 术语描述其设计，不代表任意硬件和负载下的硬实时保证。[原论文](https://www.usenix.org/conference/osdi24/presentation/agrawal)

<div class="inference-legacy-anchors" aria-hidden="true"><span id="1-为什么不-padding"></span><span id="2-cu_seqlens-与-raggedpacked-varlen布局"></span><span id="1-ragged-vs-padding-的计算量"></span><span id="延伸阅读-references"></span></div>

## 与输入布局的边界

原先混在本文中的 padding、packed 和 `cu_seqlens`，现由[动态形状与数据布局](../02-model-execution/dynamic-shapes.md)完整解释。调度器产生工作清单，执行器再将清单转换为匹配内核的输入。

验证时应检查请求能否及时进入、完整 Prefill 是否只在输入完成后采样、结束请求是否退出，以及资源压力下是否发生反复暂停。准入与抢占策略见[请求调度](08-scheduling.md)，可复算事件例子见[Trace 模型](../09-measurement-and-cases/trace-and-event-model.md)。
