# Dataflow 在 CIM 上的映射：Weight Stationary 的天然契合与边界

上级：[05 Architecture And System](./README.md)
相关：[Data Encoding Strategies](../04-circuit-and-macro/data-encoding-strategies.md), [RAM: Data Movement First Principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md), [NoC: Broadcast Multicast Tree](../../../NoC/wiki/06-ai-noc-specifics/broadcast-multicast-tree.md)

## 这页在回答什么问题

CIM 为什么常被说成适合 weight-stationary dataflow？因为权重可以驻留在 cell/array 内，输入流过阵列并产生 partial sum。但这个优势只在权重复用、阵列利用率和归约成本同时成立时才保留。

## 三种 Dataflow

Weight-stationary 把权重固定在 array 内，activation 流过 macro。它适合 SRAM/ReRAM/Flash CIM 的 MVM/GEMM 和固定权重 edge inference；代价是 activation broadcast、partial sum reduction 和 layer 间调度仍然存在。

Input-stationary 把 activation 留在本地，分批送入权重或权重块。它适合输入复用高的卷积或窗口操作，但对 ReRAM/Flash 这类写慢 memory 不自然，因为频繁换权重会破坏路线优势。

Output-stationary 把 partial sum 留在本地累加，减少中间结果移动。它适合 bit-serial digital CIM 和 mixed-signal 多周期累加，但需要更宽 accumulator、更大 local buffer 和更复杂控制。

## 三条 Paradigm 的映射差异

Analog CIM 更偏 weight-stationary MVM。ReRAM/Flash 的权重写入和校准成本高，适合长期驻留；输入编码、ADC 输出和 tile reduction 决定系统瓶颈。

Digital CIM 支持更灵活的数据流。SRAM 可以较快重写，bit-serial 和 popcount 支持多种低比特算子；代价是 accumulator、cycle count 和 local SRAM buffer 增加。

Mixed-signal CIM 要在映射中显式处理边界：哪些 partial sum 在 analog 域形成，哪些在数字域累加，哪些需要 QAT/noise-aware training 配合。mapping 不只是 tensor tiling，还包括误差和 scale 的分配。

## 算子映射差异

GEMM/MVM 是最自然对象。权重矩阵按 array shape 切块，activation 广播到多个 macro，partial sum 在 local accumulator、tile 或 NoC 上合并。

Conv 可通过 direct convolution 或 lowering 映射。im2col 会提高矩阵化程度，却增加 activation buffer 和重复数据搬运；direct mapping 保留局部复用，但控制更复杂。

Transformer 要拆开看。Projection 和 FFN 更接近 GEMM；attention score、softmax、normalization 和 KV cache 访问常常需要 fallback 或不同硬件路径。把整个 Transformer 都称为适合 CIM 是过度概括。

## 一句话理解

CIM 天然偏 weight-stationary，但系统收益取决于 activation、partial sum、fallback 和数据流边界是否一起设计。

## 建模启示

建模 dataflow 时要记录 tensor shape、array shape、tiling、weight residency、weight update frequency、activation source、activation broadcast、partial-sum location、fallback op、reuse factor 和 mapping efficiency。Resource 可抽象为 macro/tile/buffer，Topology 是 broadcast/reduction 结构，Interaction 是 tensor movement 与 synchronization，Capability 是支持的 op、bit-width 和 dataflow 模式。cycle-level WL pulse、RTL FSM 和 cell 波形可折叠为 latency/energy/precision 参数；tiling、reuse、partial-sum merge point 和 fallback 不能折叠。
