# Attention 内核：分块计算、在线归一化与并行归约

<div class="inference-legacy-anchors" aria-hidden="true"><span id="05-注意力核与解码-kernelprefill-vs-decode-attention-kernels"></span></div>

上级：[本专题导读](README.md)

Attention 内核的任务是在给定 Q、K、V、掩码和状态布局的条件下计算输出。它不决定哪些请求被接纳，也不负责缓存块的生命周期。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span></div>

## Prefill 与 Decode 的查询形状不同

对单头，$Q$ 为 $[N_q,d_h]$，$K,V$ 为 $[N_k,d_h]$。分数矩阵的形状为 $[N_q,N_k]$。完整 Prefill 常有 $N_q=N_k=N$；普通单 token Decode 则有 $N_q=1$。

如果完整 Prefill 在 HBM 物化分数或概率矩阵，会产生平方级中间存储。单 token Decode 的这一矩阵是一行，不能将两者都称为同样的 $N^2$ 中间矩阵问题。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism"></span><span id="flashattention不落-s-矩阵的-tiling-online-softmax"></span></div>

## 分块与在线归一化

FlashAttention 将查询和 KV 分块，在片上存储中计算分数，并维护在线 softmax 状态，避免将整个概率矩阵写回 HBM。

对一行分数，维护最大值 $m$、指数和 $\ell$ 与未归一化输出向量 $z$。新块的分数为 $a_j$、值为 $v_j$，则：

$$m'=\max(m,\max_j a_j)$$

$$\ell'=e^{m-m'}\ell+\sum_j e^{a_j-m'}$$

$$z'=e^{m-m'}z+\sum_j e^{a_j-m'}v_j,\qquad o=z'/\ell'$$

初始化采用空累积状态；实现需单独正确处理空块和全掩码行，避免无穷值相减。掩码与缩放必须在计算有效分数时保持一致。

这个过程在实数算术中对应完整 softmax；有限精度下的归约顺序不同，不意味着逐位相同。它减少中间 IO，没有改变标准全注意力的主要乘加阶数。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-prefill为什么必须不落-s"></span></div>

## IO 复杂度中的容量单位

原始 FlashAttention 论文以 SRAM 可容纳的**元素数** $M_e$ 建模。对单头，序列长度为 $N$、头维度为 $d_h$，在 $d_h\le M_e\le Nd_h$ 的条件下，其 HBM 元素访问量为：

$$\Theta(N^2d_h^2/M_e)$$

若片上容量用字节 $M_b$ 表示，需先用元素字节数换算 $M_e=M_b/p$，不能直接把两种单位混用。公式也不是一个可直接代入得到真实执行时间的精确流量计数。

批中各序列的工作应按 $\sum_i s_i^2$ 累加；求和后不能再重复乘同一批大小。逐层执行时的峰值中间内存也不等于把每层峰值全部相加。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="decode-为什么不能照搬-flashattention占用率塌方"></span><span id="flashdecoding加第三个并行维split-kv"></span><span id="2-decode占用率条件-split-数"></span></div>

## Decode 的并行度与 split-KV

低请求数、少量查询行时，仅按请求和头分配工作可能无法提供足够并行度。Split-KV 沿历史 KV 分段，各段计算局部最大值、指数和及输出，再用同类归一化关系合并。

它增加可并行工作，也增加临时状态、归约和启动成本。上下文很短或请求已很多时，继续拆分可能得不偿失。实际划分还受 GQA 头分组、内核 tile 和设备资源影响。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="paged-attention-kernel在-gather-之上做-flashdecoding"></span></div>

## 分页布局怎样进入内核

分页内核通过块表找到逻辑位置对应的缓存块。管理器负责分配和引用；内核负责按映射读取并完成 Attention。软件块大小与计算 tile 大小可以不同。

共享前缀只保证可以共享存储。不同请求有不同 Q，仍需计算各自的注意力；KV 是否在缓存层被复用、HBM 实际读取多少次，要看内核布局和观察边界。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="3-把-01-的理想下界接到实测-tpot"></span><span id="与架构建模的接口-modeling-interface"></span><span id="延伸阅读-references"></span></div>

## 选择与验证

至少覆盖短／长查询、短／长 KV、小／大批量、不同头布局和数据类型。先与参考计算核对掩码、位置和数值误差，再测执行时间、工作区及实际流量。不能给某个内核名称附加通用加速倍数。

- [FlashAttention 原论文](https://arxiv.org/html/2205.14135)：在线计算与 IO 分析。
- [Flash-Decoding 官方技术说明](https://pytorch.org/blog/flash-decoding/)：沿 KV 维增加并行度。
- [分页 KV](../04-state-and-memory/06-paged-kv-cache.md)负责状态管理；[性能定位](../09-measurement-and-cases/benchmarking-and-profiling.md)负责把内核测量连接到请求指标。
