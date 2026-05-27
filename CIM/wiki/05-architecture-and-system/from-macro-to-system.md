# 从 Macro 到 System：Tile、Bank、Chip 三级组织

上级：[05 Architecture And System](./README.md)
相关：[Macro Design Framework](../04-circuit-and-macro/macro-design-tradeoff-framework.md), [Peripheral Overhead](../04-circuit-and-macro/peripheral-overhead.md), [NoC: Tile Architecture](../../../NoC/wiki/06-ai-noc-specifics/tile-architecture-and-noc.md)

## 这页在回答什么问题

macro-level TOPS/W 为什么不能直接外推成 chip-level 能效？因为每升一级都会新增组件、调度和瓶颈，且这些新增成本常常正好落在 CIM 试图减少的数据搬运路径上。

## 层级链

| 层级 | 证明什么 | 最容易遗漏什么 |
| --- | --- | --- |
| cell | cell/device 支持 compute-storage 同混 | 大阵列误差、外围、映射 |
| macro | array + peripheral 可闭合 | 输入供给、输出归约、真实 workload |
| tile | 多 macro 能协同 | local buffer、controller、load balance |
| chip | 多 tile 可规模化 | NoC、global buffer、thermal、utilization |
| system | host/runtime 可部署 | DMA、同步、fallback、软件栈 |

cell 到 macro 的第一道损耗来自外围和阵列规模。单个 SRAM bitline、ReRAM cell 或 Flash threshold state 能参与计算，不代表大阵列中的 driver、SA/ADC、IR drop、variation 和 calibration 已经闭合。

macro 到 tile 的第一道损耗来自 buffer 和 local reduction。一个 256x256 macro 可以高效完成局部 MVM，但完整 layer 往往需要切块、重复输入、合并 partial sum 和处理边界碎片。

tile 到 chip 的第二道损耗来自 NoC、global buffer 和同步。CIM 把部分计算压进 array，不代表全局通信消失；多 tile 的 partial sum、activation broadcast 和 weight reload 仍会形成 traffic。

chip 到 system 的第三道损耗来自 host 协同。host 要把算子下发、管理 DMA、处理不支持的 op、同步结果并处理异常路径；BUS wiki 的 [DMA path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md) 是理解这类系统开销的基础。

## 三条 Paradigm 的收益衰减链

Analog CIM 的 macro 指标最容易在系统层缩水，因为 ADC、calibration、effective precision、tile reduction 和模型补偿都必须计入。它适合固定低比特 MVM，但系统需要保证误差可控、输入输出不被搬运吞掉。

Digital CIM 的缩水来自面积和周期。SRAM digital macro 可验证性强，但 bit-serial 扩展、local accumulator、buffer 和 NoC 会限制 chip 级有效吞吐。

Mixed-signal CIM 的缩水来自边界后处理。array 内 analog 局部收益需要通过数字校正、分块累加和 runtime mapping 保存；边界设计越复杂，系统模型越不能只用一个 peak TOPS/W 参数。

## PIM/NMC 边界

DRAM/HBM/GDDR-PIM 的系统组织是 bank/channel/device 级，不是 CIM macro 堆叠。它要问 memory command、bank conflict、host offload 和 result return。HBM base die、interposer 或 package-side compute 属于 NMC，需要按 die-to-die、package bandwidth 和 host interface 建模，不能与 array-native CIM macro 横比。

## 一句话理解

从 macro 到 system，CIM 的问题从“阵列能不能算”变成“局部收益经过 buffer、NoC、memory 和 host 后还剩多少”。

## 建模启示

建模时至少要保留五级状态：cell/device 约束折叠后的 macro 参数、macro count 与 array size、tile count 与 buffer capacity、chip NoC bandwidth 与 global memory、host stall 与 fallback。Resource 是 macro/tile/buffer/NoC/host，Topology 是层级连接，Interaction 是 traffic、sync 和 fallback，Capability 是 op、bit-width、ADC sharing 与 accumulator width。cell 波形、WL pulse 和 RTL FSM 可折叠成 macro latency/energy/error；utilization、traffic、synchronization 和 unsupported-op ratio 不能折叠掉，否则会高估系统收益。
