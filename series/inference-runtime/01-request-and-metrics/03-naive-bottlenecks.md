# 朴素推理引擎的三类瓶颈

<div class="inference-legacy-anchors" aria-hidden="true"><span id="03-朴素实现的瓶颈-bottlenecks-of-a-naive-engine"></span></div>

上级：[本专题导读](README.md)

一个能够正确生成文本的循环，还不一定能高效服务多个请求。这里用三个最小反例，分别观察内存预留、批组成和阶段干扰。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span></div>

## 基线实现及其限制

构造一个朴素引擎：每个请求预留最大长度的连续 KV 空间；一批请求一起进入，等整批完成后再接收下一批；Prefill 与 Decode 共享同一执行队列。它便于实现，但将几种不同的资源问题叠在一起。

这些问题的改进方向不同，不能用“GPU 利用率低”统一解释。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="瓶颈-1kv-显存碎片"></span><span id="量化与公式-quantification"></span><span id="1-碎片-显存利用率乘子-eta_textmem"></span></div>

## 预留空间与实际状态不相等

假设四个请求各预留 8,192 个 token 的 KV 容量，而当前各只保存 1,024 个位置。仅看这四份预留区，有效载荷比例为：

$$\eta_{\rm reserved}=\frac{4\times1024}{4\times8192}=12.5\%$$

这是预留策略产生的空置空间。如果改成变长连续分配，还可能产生另一问题：释放后留下多个空洞，总空闲空间够用，却没有足够大的连续区。

分页可减少大块连续分配要求，但仍有末块空置和池间不均衡。应分别计算预留空置、固定块尾部以及其他内存占用，不能把同一空间重复算成几种碎片。细节见[分页 KV](../04-state-and-memory/06-paged-kv-cache.md)。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="瓶颈-2静态批处理的尾部浪费"></span><span id="2-尾部浪费-batch-效率乘子-eta_textbatch"></span></div>

## 静态批的尾部浪费

构造三条请求，分别需要 2、4、8 次 Decode 迭代。若固定保留三个槽位直到最长请求结束，总共提供 $3\times8=24$ 个槽位迭代，其中有效生成只有 $2+4+8=14$ 个。

$$\eta_{\rm slot}=\frac{14}{24}\approx58.3\%$$

这个比例只描述槽位占用。实际执行器可能跳过已完成行，迭代耗时也可能随批大小变化；不能直接说延迟或吞吐损失了 41.7%。

[连续批处理](../05-batching-and-scheduling/04-dynamic-shape-batching.md)在迭代边界补入等待请求，减少空槽位持续时间。收益还取决于是否有等待任务，以及新任务需要多少 Prefill 和 KV。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="瓶颈-3prefill-decode-互相干扰"></span><span id="3-prefill-干扰-itl-尾部惩罚"></span></div>

## 长 Prefill 怎样影响正在生成的请求

假设普通 Decode 一轮耗时 25 ms。若一个 545 ms 的 Prefill 被串行插入两个 Decode 轮之间，一条请求可能出现约 570 ms 的间隔。这是一个构造事件，不是 p99 测量结果。

干扰发生在共享执行资源与调度边界上。分块 Prefill 可以缩短一次占用；阶段分离可以减少某些共置干扰。两者都增加新的调度或传输成本，也不保证每次间隔都低于某个阈值。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="三乘子合一为什么朴素-goodput-只剩零头"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 为什么不能把三个效率因子相乘

空闲内存允许接纳更多请求，批组成又改变内核效率和每轮耗时；Prefill 选择影响 KV 增长和 Decode 等待。这些量相互作用。

因此，“理想 goodput × 内存效率 × 批效率 × SLO 通过率”不是通用性能模型。三个比例甚至可能采用不同分母。更可靠的过程是：

1. 用内存模型判定当前状态能否容纳。
2. 用调度规则决定本轮执行计划。
3. 根据形状、状态长度与资源竞争估算或测量本轮时间。
4. 沿时间线积累请求输出，再计算延迟分布与 goodput。

可以先用[事件模型](../09-measurement-and-cases/trace-and-event-model.md)验证这条因果链，再用实测校准每轮成本。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="延伸阅读-references"></span></div>

## 来源与下一步

[PagedAttention](https://arxiv.org/abs/2309.06180)研究 KV 内存管理；[Orca](https://www.usenix.org/conference/osdi22/presentation/yu)研究迭代级调度。这些论文说明不同机制解决不同问题，论文中的加速比仍依赖其基线、模型和负载。

接下来先读[模型执行计划](../02-model-execution/model-loading.md)，再进入内存和调度专题。
