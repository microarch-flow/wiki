# CNN：CIM 的标准应用场景及其上限

上级：[07 Workloads](./README.md)
相关：[Dataflow Mapping](../05-architecture-and-system/dataflow-mapping-on-cim.md), [Weight Mapping](../06-software-stack/weight-mapping-to-arrays.md), [NoC: Workload GEMM](../../../NoC/wiki/06-ai-noc-specifics/workload-gemm-on-noc.md), [RAM: NPU Memory Hierarchy](../../../RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md), [BUS: DMA Path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)

## 这页在回答什么问题

为什么 CNN 是 CIM 论文最常见的 workload？因为卷积可规整映射为 MVM/GEMM，权重复用高，固定模型 edge inference 容易让 CIM 的局部节能变成系统收益。

## CNN 为什么适合

Conv layer 有清晰的 sliding window、channel reduction 和权重复用。通过 direct mapping 或 im2col/lowering，它可以转成多个 array-friendly 矩阵块。weight-stationary dataflow 与 CIM 天然契合：权重放在 array，activation 流过，partial sum 在 macro/tile 合并。

CNN 也更容易接受低比特推理和 QAT。许多 edge vision/audio 模型可以在 INT8、INT4 或 mixed precision 下保持任务精度，这给 analog/mixed-signal CIM 留出空间。

## 上限在哪里

im2col 会扩大 activation traffic，可能把 array 友好性换成 buffer 和 NoC 压力。depthwise convolution、small channel layer、residual connection 和 normalization 不一定适合 CIM。整网部署还要处理 pooling、activation、resize、post-processing 和 host fallback。

CNN benchmark 也不能代表全部 AI workload。它证明规整固定模型可行，但不能自动外推到 Transformer、LLM decode、MoE routing 或动态场景。

## 三条 Paradigm 的 CNN 落点

Analog CIM 适合固定权重、低比特 CNN，尤其是 edge inference。ReRAM/Flash/SRAM charge-domain 路线可以利用高复用 MVM，但必须处理 ADC、校准和模型 accuracy。

Digital SRAM-CIM 适合产品化 CNN 加速，因为精度、DFT、SoC 集成和 runtime 更稳。XNOR/popcount、bit-serial convolution 和低比特 accumulator 是常见路径；代价是 accumulator、buffer、NoC 和周期数。它的挑战是和传统 NPU/SRAM buffer + MAC 做公平比较。

Mixed-signal CIM 常是现实折中：array 内做局部 charge/current accumulation，数字端做校正、累加和后处理。CNN 的规则结构让这种边界更容易被 compiler 捕捉。

CNN 映射到 cell、bitline、wordline、sense path 或紧邻 array path 时才是 CIM。普通 SRAM buffer + MAC 仍是传统加速器路径；memory die/bank 内 bank/channel offload 是 PIM；HBM base die、interposer 或 package-side accelerator 是 NMC。

## 一句话理解

CNN 是 CIM 最友好的标准场景，但它的价值来自规整低比特高复用子图，不是来自“CNN 有很多卷积”这个表面事实。

## 建模启示

CNN 建模要记录 layer shape、kernel size、channel count、feature map size、batch、tiling、lowering/direct mapping 策略、weight reuse、activation buffer、activation expansion、partial-sum merge point 和 non-CIM op。Resource 可抽象为 macro/tile/buffer，Topology 是 activation broadcast 与 reduction，Interaction 是 lowering 后 tensor movement，Capability 是支持的 bit-width、kernel pattern 和 error tolerance。具体 WL pulse 可折叠，但 im2col expansion、partial-sum merge 和 fallback 不能折叠。
