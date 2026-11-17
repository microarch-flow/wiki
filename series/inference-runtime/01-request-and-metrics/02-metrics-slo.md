# 延迟、吞吐与 SLO：先确定测量边界

<div class="inference-legacy-anchors" aria-hidden="true"><span id="02-服务指标与-slo-serving-metrics-slos"></span></div>

上级：[本专题导读](README.md)

测量延迟之前，先确定计时位置、统计对象和失败处理规则。设备执行时间、服务端生成时间和用户收到文本的时间是不同指标。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism定义表"></span><span id="1-e2e-分解-sla-判定的骨架式"></span></div>

## 在同一条时间线上定义延迟

本文的客户端指标使用同一单调时钟。$t_0$ 是客户端发出请求的时间，$t_1,\ldots,t_N$ 是客户端观测到各输出 token 的时间。输入上传、网络、排队和服务端处理都可能包含在内。

| 指标 | 定义 | 边界条件 |
|---|---|---|
| TTFT，首 token 时延 | $t_1-t_0$ | 首次收到有效输出；不能把空响应头当首 token |
| ITL，token 间时延 | $t_j-t_{j-1}$，$j=2,\ldots,N$ | 每个相邻 token 间隔都是一个样本 |
| TPOT，每输出 token 时间 | $(t_N-t_1)/(N-1)$ | 仅在 $N>1$ 时定义 |
| E2E，端到端时延 | $t_N-t_0$ | 此处终点为最后一个 token；完整响应结束可另计 |

因此，对单个请求且 $N>1$：

$$\mathrm{E2E}=\mathrm{TTFT}+(N-1)\mathrm{TPOT}$$

同一请求的 TPOT 等于其 ITL 样本均值。但“先对每个请求求 TPOT 再平均”和“把所有 ITL 放在一起平均”权重不同。输出只有一个 token 时，TPOT 应记为不适用，而不是 0；无输出、失败和取消应单独统计。

流式协议可能一次返回多个 token，甚至返回经过文本缓冲后的片段。只有 chunk 到达时间时，应报告 chunk 间隔，不能伪造 chunk 内每个 token 的真实到达时间。服务端 token 时间可作为另一个观测口径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="2-throughputlatency-tradeoff-与-batch-旋钮"></span><span id="3-goodput-架构探索的目标函数"></span></div>

## 吞吐与 goodput 的单位必须明确

在固定观察窗口 $\Delta t$ 内，可以统计完成请求数、输出 token 数或输入加输出 token 数。它们分别对应 request/s、output token/s 等单位，不能混写为 TPS。

先给每个请求定义成功条件。令 $I_i=1$ 表示请求成功，且其 TTFT、TPOT 等请求级阈值全部满足；否则 $I_i=0$。窗口归属规则也需固定，例如按完成时间归属。

$$G_{\rm req}=\frac{\sum_i I_i}{\Delta t},\qquad
G_{\rm tok}=\frac{\sum_i I_iN_i}{\Delta t}$$

长输出请求对第二个指标权重更高。因此最大化请求 goodput 与最大化 token goodput 不等价。只报成功请求的延迟而不报失败数，会掩盖过载。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span></div>

## 请求阈值与总体百分位不是同一层

“99% 请求的 TTFT 不超过 1 s”是总体目标。“本请求 TTFT 为 800 ms”是一个样本。若同一请求集合中 TTFT 与 TPOT 各有 99% 达标，联合达标比例可能只有 98%，因为两类失败可能落在不同请求上。

单次停顿也不能决定 p99。构造 1,000 个样本：999 个为 25 ms，1 个为 570 ms。最近秩 p99 取排序后的第 990 个，仍为 25 ms。报告百分位时，应给样本量、估计方法、观察窗口及错误比例。

排队让 TTFT 与 TPOT 相互影响。即使采用 PD 分离，两个池仍可能通过到达过程、KV 传输和资源配比耦合，不能把两个 SLO 当作天然独立。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="4-mbu-decode-效率的单一数字"></span></div>

## 利用率需要说明分子来自哪里

模型算力利用率 MFU 常用“估算的模型 FLOP ÷ 时间 ÷ 指定精度峰值”。它描述模型工作量相对于设备规格，不等于硬件计算单元忙碌比例。

模型带宽利用率 MBU 可以定义为“逻辑字节估算 ÷ 时间 ÷ 峰值带宽”，但必须明确它是模型口径。若要声称实测 HBM 带宽，应使用相应硬件计数器，并说明读写、缓存和时间边界。

低 MBU 可能来自计算、通信、同步、启动或批组成，并不自动证明内核访存实现差。软件优化还可能降低实际字节量，此时利用率变化与性能收益未必同向。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="算例示意非某型号实测"></span><span id="延伸阅读-references"></span></div>

## 一个可核对的小例子

假设一个请求在发送后 100、120、160 ms 收到三个 token，且每次只有一个 token。则 TTFT 为 100 ms，两个 ITL 为 20、40 ms，TPOT 为 30 ms，E2E 为 160 ms。只报 TPOT 会隐藏后一个较慢间隔。

[NVIDIA 指标文档](https://docs.nvidia.com/aiperf/dev/reference/ai-perf-metrics-reference)给出工具使用的计时与流式口径。实际工具名称可能不同，应按定义对齐。如何设计到达过程和统计窗口，见[压测与性能定位](../09-measurement-and-cases/benchmarking-and-profiling.md)。
