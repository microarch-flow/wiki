# PD 分离：KV 交接与请求关键路径

<div class="inference-legacy-anchors" aria-hidden="true"><span id="12-pd-分离-kv-传输-分层存储-prefill-decode-disaggregation"></span></div>

上级：[本专题导读](README.md)

PD 分离把 Prefill 与 Decode 放到不同执行实例或资源池。它减少某些阶段共置的竞争，也增加 KV 交接、路由和队列协调。是否有收益，需要比较同一负载与服务目标。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="两池分工slo-解耦"></span></div>

## 从一个池拆成两个池

Prefill 池处理输入并建立状态，Decode 池承接后续生成。两池可以采用不同并行布局或硬件配置，但这会影响 KV 格式、切分和传输路径。

两个池可以独立扩缩，两个 SLO 却不天然独立。Prefill 产出过快可能挤满传输和 Decode 队列；Decode 容量不足也会限制可接纳的 Prefill。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism"></span><span id="kv-传输"></span></div>

## KV 交接的关键事件

<ol class="inference-flow">
<li><strong>确定接收端。</strong>选择 Decode 实例，确认其模型身份、布局和接收预算。</li>
<li><strong>产生可传输状态。</strong>Prefill 计算完成全部或某一可交接片段，并记录版本与位置范围。</li>
<li><strong>传输与安装。</strong>发送 KV 和元数据；接收方必要时重排，更新本地映射。</li>
<li><strong>确认就绪。</strong>接收方确认执行所需状态完整可见，再启动依赖它的计算。</li>
<li><strong>移交与释放。</strong>按协议确定后续状态所有者；源端等待引用与传输结束后回收。</li>
</ol>

可以按层或块流水，隐藏部分传输，但只能在依赖允许时重叠。失败重试需识别已经安装的片段，防止重复提交或读取不完整状态。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-kv-传输成本复用-0108-的带宽式"></span></div>

## 传输量先按实际布局计算

若需要传输 s 个位置，且标准模型每位置所有层 KV 为 $k_{kv}$ byte/token，则：

$$D_{\rm KV}=s\,k_{kv}$$

$k_{kv}$ 已包含层数，不能再乘一次 L。接收方已有相同有效前缀时可以减少缺失范围；布局转换、复制和协议元数据另算。

沿用[分层存储的传输算例](../04-state-and-memory/tiered-kv.md#搬运与重算怎样比较)，625 MiB 在 64 GB/s 有效带宽下的单向纯传输项为 10.24 ms。PD 交接还需单独估计目标端何时有预算、何时安装完成。

链路规格、双向聚合带宽和实际单向有效带宽不能混用。TP/PP 配置不同还可能要求多对多传输或重排，而非一条连续复制。

## 首 token 在哪里产生很重要

以 Prefill 结束并完成首 token 采样的时刻为 0，假设上述 10.24 ms 全在关键路径上。接收端就绪后再花 2 ms 计算并产生第二个 token，省略其他等待和网络送达时间。

- **先返回首 token。** 客户端在 0 ms 和 12.24 ms 看到两个 token，第一段 ITL 为 12.24 ms。交接等待落在第一段 ITL。
- **交接就绪才返回首 token。** 客户端在 10.24 ms 和 12.24 ms 看到两个 token，第一段 ITL 为 2 ms。交接等待使 TTFT 增加 10.24 ms。

两种策略的第二个 token 同时就绪，用户感受到的停顿位置不同。这些时刻相对 Prefill 结束计。实际验收应从请求发送时刻按[指标定义](../01-request-and-metrics/02-metrics-slo.md)计算 TTFT。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-何时值得分离"></span><span id="3-goodput坐实-02"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 用同一目标比较分离收益

可比较固定硬件预算下、相同到达过程与质量要求下的请求 goodput；也可比较满足同一 SLO 所需的资源。不能把吞吐增加量与毫秒延迟直接相减。

收益可能来自减少共置干扰、不同阶段资源配比和独立扩缩。成本包括传输、队列、两池闲置、接收预算及故障处理。高负载本身不是收益保证，还要看哪一池和哪一条路径先饱和。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="kv-offload-分层存储"></span><span id="4-分层-kv-的取舍"></span><span id="延伸阅读-references"></span></div>

## 与 KV 分层存储的边界

KV 留在主机内存或存储设备中等待以后复用，属于[分层存储](../04-state-and-memory/tiered-kv.md)。PD 分离强调执行阶段和所有权交接。两种机制可以组合，但应分别计算传输目的、恢复时限和失败处理。

[DistServe 原论文](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf)讨论资源分配、带宽约束与 goodput；论文结果依赖其模型与工作负载。工程测量方法见[压测](../09-measurement-and-cases/benchmarking-and-profiling.md)，副本选择见[路由](../08-serving-lifecycle/routing-and-scaling.md)。
