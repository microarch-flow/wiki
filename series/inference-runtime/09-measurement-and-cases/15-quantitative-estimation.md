# 容量与性能估算：Llama 3 70B 与 H100 条件算例

<div class="inference-legacy-anchors" aria-hidden="true"><span id="15-量化估算算例llama-3-70b-on-h100-worked-example"></span></div>

上级：[本专题导读](README.md)

本例展示如何把模型参数、容量预算和执行工作量连接起来，并说明哪些结论仍需要实测。它是条件估算，不是 H100 服务性能或 SLO 的验收结果。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="0-配置与常数setup"></span></div>

## 固定对象与输入性质

模型采用原始 Llama 3 70B 的结构，使用全注意力 GQA。其官方上下文长度为 8K，本例不假定已完成上下文扩展。

| 输入 | 值 | 性质 |
|---|---|---|
| 层数、查询头、KV 头、头维度 | 80、64、8、128 | 官方模型结构 |
| 参数量 $P$ | $70\times10^9$ | 为便于估算采用的圆整值，非精确参数计数 |
| 权重与 KV 元素字节 | 2、2 | 本例精度假设 |
| 设备与布局 | 4 张 H100 SXM，TP=4 | 本例配置，假定切分均衡且 KV 不额外复制 |
| 单卡带宽、标称容量 | 3.35 TB/s、80 GB | 厂商规格；运行时可用容量需另测 |
| 单卡 FP16/BF16 稠密峰值 | 约 989.5 TFLOP/s | 厂商稀疏规格除以 2 的口径换算 |
| 聚合可用预算、其他开销 | 288 GB、8 GB | 构造预算，不是实测 |

GB 与 TB 使用十进制，KiB 与 GiB 使用二进制。标称容量不能直接当作进程可分配字节数。

来源：[Meta 模型卡](https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md)、[Meta 结构配置](https://github.com/meta-llama/llama-models/blob/main/models/sku_list.py)、[NVIDIA H100 规格](https://www.nvidia.com/en-eu/data-center/h100/)。实际复现实验还应记录下载的模型修订与运行时版本。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="1-kvtoken01"></span><span id="2-显存-最大并发0608"></span></div>

## 先算载荷，再算容量

$$k_{kv}=2\times80\times8\times128\times2
=327680\ {\rm byte/token}=320\ {\rm KiB/token}$$

4,096 个位置的有效 KV 为 1.25 GiB，即 1.34217728 GB。按圆整参数量，权重约为 140 GB，构造 KV 池预算为：

$$M_{\rm KV}=288-140-8=140\ {\rm GB}$$

按[分页 KV 的分配规则](../04-state-and-memory/06-paged-kv-cache.md#块大小的量化取舍)，假定每块容纳 16 个位置，按需从池中取块，各请求不共享前缀，忽略 KV 元数据。每条序列当前已有 4,096 个位置，恰好占 256 个整块。此时能容纳的序列数上限为：

$$\left\lfloor\frac{140\times10^9}{4096\times327680}\right\rfloor=104$$

接纳 100 条时，已用块占 134.217728 GB。若每条再处理一个位置，新增有效载荷合计是 32.768 MB。但每条的末块都已写满，下一轮需要 100 个新块。按 16 个位置计，每块跨四卡占 5.24288 MB，合计占用 **524.288 MB 的空闲块池容量**。对预分配的池，这是把空闲块转为已用块，进程已为池占用的显存不变。

140 GB 的池可提供 26,702 个完整块。若接纳 104 条，已占用 $104\times256=26{,}624$ 块，只剩 **78 块**。104 条当前都放得下，但下一轮需要 104 块。若没有释放或共享带来的余量，[调度器](../05-batching-and-scheduling/08-scheduling.md#准入是资源承诺)必须减少本轮推进的请求，或先腾出空间。这里按四卡均衡切分记账，实际部署还需逐 rank 核对预算。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="3-tpot-itl-vs-batch0105"></span><span id="汇总表配置-allama-3-70b-4h100-fp16-s4k"></span></div>

## 资源时间估算不能直接称为 TPOT

假设本轮每条请求各做一次普通 Decode，且每条已有 4,096 个缓存位置。读取模型按权重和旧 KV 有效载荷各读一次估算：

$$D_{\rm logical}=140\times10^9+
B_{\rm req}\times4096\times327680$$

为展示模型，取有效带宽为聚合峰值的 0.7。这个比例是未校准假设。仅带宽项为：

| 本轮请求数 | 逻辑读取量 | 带宽项估算 |
|---|---|---|
| 1 | 141.342 GB | 15.068 ms |
| 32 | 182.950 GB | 19.504 ms |
| 100 | 274.218 GB | 29.234 ms |

还需检查计算项。按[阶段模型](../01-request-and-metrics/01-prefill-decode.md)，每条的近似线性层与 Attention 工作合计为 $2P+4Lh_qd_hs$ FLOP，其中可见长度 $s=4097$ 包含本轮新增位置。上表也未完整计入内核启动、通信、KV 写入和其他算子。

峰值资源给出下界；使用假设效率后的数值是模型估计，不是严格下界。只有明确所有请求每轮执行、输出无额外等待等条件后，才可将迭代时间近似连接到平均 token 间隔。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="4-ttft0102"></span></div>

## Prefill 计算与 TTFT 分开

构造输入长度 $s_p=3500$，没有前缀命中。线性层近似工作为 $2Ps_p$。若按有效因果位置对计数，Attention 的 QK 与 AV 约为：

$$F_{\rm attn}\approx2Lh_qd_hs_p(s_p+1)$$

假设计算效率为聚合稠密峰值的 0.5，则这两项对应约 255.715 ms。实际内核可能执行额外掩码区域，其他算子和通信也未计入。

TTFT 还包含输入准备、排队、执行开销、采样与输出。不能将 255.715 ms 写成“空载实测 TTFT”，更不能据此宣布 p99 达标。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="5-吞吐与-goodput-工作点0208"></span><span id="6-旋钮敏感度sweeps"></span><span id="a-上下文翻-4-倍-显存绑吞吐崩kv-主导01"></span><span id="b-fp8-量化-砍一半-gpu配置-b10"></span></div>

## 吞吐、goodput 与灵敏度

若额外假定 100 条请求持续每轮各输出一个 token，并把 29.234 ms 当作完整迭代时间，可得到约 3,421 token/s。该数值仅是同一条件模型的除法结果。

goodput 还需要请求到达、完整输出过程、成功条件与延迟分布。平均资源时间低于阈值，不证明 p99 低于阈值。

在相同 140 GB KV 池中，将当前状态长度从 4,096 增到 8,192，载荷容量上限从 104 变为 52；这是容量关系，不是吞吐自动减半。8,192 也已到本模型声明的上下文边界，不能再无条件追加。

若只把 KV 有效字节减半，固定池的载荷容量上限可翻倍。若同时改变权重精度、卡数、TP 和内核，必须重建整张预算与成本表；不能通过让效率系数保持相同，就证明“两张卡等价四张卡”。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span><span id="延伸阅读-references"></span></div>

## 如何完成实测闭环

先测加载峰值和各 rank 状态预算，再测不同批与长度的执行、通信和实际流量，最后按[压测方法](benchmarking-and-profiling.md)回放请求并检查 SLO。

[复算脚本](https://github.com/microarch-flow/wiki/blob/main/series/inference-runtime/examples/verify_examples.py)检查本页的算术；[事件模型](trace-and-event-model.md)解释从迭代到请求指标的转换。二者都不替代目标硬件验证。
