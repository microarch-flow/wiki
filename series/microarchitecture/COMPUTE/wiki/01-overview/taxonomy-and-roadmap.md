# 学习路线与域边界:原语 → 阵列 → 流水 → 布局

上级:[COMPUTE 域总览](./README.md)
相关:[算力单元要解决什么问题](./problem-statement.md)、[计算 / 通信比(全域纲领)](./compute-communication-ratio.md)

---

## 这页在回答什么问题

两件事:(1) COMPUTE 域内部该按什么顺序读——为什么是"自底向上从门到布局",而不是别的顺序;(2) COMPUTE 域和已有的 BUS/RAM/NOC/DMA/FAB/CIM/Workload 各域的**边界在哪**,避免重复造轮子。

---

## 1. 为什么自底向上

路线从逻辑门出发，逐步引入算术、数据流、时序与系统组织。选路可能增加面积；复用可能减少指定边界的流量。时钟、工艺和制造也引入独立约束，不能全部归结为搬运面积或同一个比值。

```
门 ──▶ MAC ──▶ datapath(mux 暴露搬运问题)
                      │
                      ▼ 如何减少特定边界的数据移动?
              systolic array(局部复用与边界流量)
                      │
                      ▼ 阵列要跑多快?
              时钟 / 流水(同步的代价,频率≠吞吐)
                      │
                      ▼ 这些门要不要可重配?
              FPGA vs ASIC(可配置性的实现代价)
                      │
                      ▼ 算完的数从哪来?
              cache vs scratchpad(数据管理与资源争用)
                      │
                      ▼ 把这些拼成一个核 / 一片芯片
              CPU/GPU core ──▶ 对比 GPU 与 TPU 的局部矩阵结构
                      │
                      ▼ 怎么把它喂进仿真器?
              archax 建模启示
```

每一步引入新的决策。固定工作量和跨边界字节时，改变流水深度或工艺库不会改变 MAC/B；它可能改变频率、面积和能耗。

---

## 2. 章节地图

| 章节 | 主题 | 主要评估对象 |
|---|---|---|
| 01-overview | 问题 + 纲领 + 路线 | 定义比值本身 |
| 02-datapath-foundations | 从门搭 MAC、压缩树、位宽、数字格式、mux 成本 | 位宽、选择网络与实现成本 |
| 03-systolic-array | 阵列、dataflow、trickle-feed、sizing | 利用权重或数据复用，收益取决于映射 |
| 04-clocking-and-pipeline | 全局时钟、流水寄存器、反馈环、频率≠吞吐 | 时钟域路径、II 与代价 |
| 05-fpga-vs-asic | LUT/mux 的可配置开销 | 固定逻辑与可配置实现的权衡 |
| 06-memory-discipline | cache vs scratchpad | 数据放置与服务时间 |
| 07-chip-organization | CPU/GPU 核面积、脑 vs 芯片功耗、GPU 与 TPU | 控制、计算及存储资源的分工 |
| 08-modeling-for-archax | 7 条建模启示升格 | 按边界定义建模指标 |

`[补全]` 篇(长文未展开、本域完整性需要):`dadda-and-adder-trees`、`number-formats-for-ai`、`dataflow-taxonomy`。其余以长文对应内容为**深度下限**。

---

## 3. 域边界:COMPUTE 不重写什么

COMPUTE 域聚焦"数据搬到之后怎么算、为什么算力单元长这样"。数据搬运、存储、互连和制造分别是其他域的主体。下表划清边界——COMPUTE 只建接口,不重写邻域内容:

| 邻域 | 它负责的 | COMPUTE 这边的接口篇 | 边界一句话 |
|---|---|---|---|
| **RAM** | SRAM/DRAM 器件、MC、NPU 存储层次 | [cache-vs-scratchpad](../../../../storage/01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md) | RAM 从器件看 SRAM;COMPUTE 从数据管理和资源争用分析同一块 SRAM |
| **CIM** | 存内计算路线(SRAM/ReRAM/模拟/数字) | [why-systolic-array](../03-systolic-array/why-systolic-array.md)、[dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md) | systolic 权重存数字 register 仍取数后算;CIM 读出即算。边界=驻留处是否就是计算处 |
| **NOC** | 拓扑、路由、flow control | [weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md)、[gpu-as-tiled-tpu](../07-chip-organization/gpu-as-tiled-tpu.md) | COMPUTE 定义阵列边界各方向的字节数、时刻和需求带宽；NOC 根据拓扑和仲裁提供服务与路由 |
| **DMA** | 描述符、多维 stride、double-buffering | [weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md) | trickle 提供窄带权重加载；满足独立 bank 和带宽等条件时可与计算重叠 |
| **FAB** | 工艺节点、PPA、良率、tape-out、封装 | [quadratic-bitwidth-scaling](../02-datapath-foundations/quadratic-bitwidth-scaling.md)、[pipeline-register-insertion](../04-clocking-and-pipeline/pipeline-register-insertion.md) | COMPUTE 给"省多少门";FAB 给"门→mm²→成本/良率" |
| **Workload** | CNN/Transformer/BEV/VLA 等负载特征 | [dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md)、[frequency-is-not-throughput](../04-clocking-and-pipeline/frequency-is-not-throughput.md) | COMPUTE 给硬件结构;Workload 给"什么负载的复用结构适配哪种 dataflow" |

> 原素材引用独立 Workload 仓库的 `cnn-backbone`、`attention-and-transformer`、`attention-variants-and-efficiency`。这里分别提供 [CNN 仓内相关页](../../../CIM/wiki/07-workloads/cnn-on-cim.md)、[Transformer 仓内相关页](../../../CIM/wiki/07-workloads/transformer-on-cim.md)和 [decode/KV 仓内相关页](../../../../interconnect/NOC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache.md)。这些相关页并非原文的镜像。

---

## 4. 怎么读:三种进入路径

- **想从头建立直觉**:按 01→08 顺序通读,每章读完回到[纲领篇](./compute-communication-ratio.md)对一眼"这章在表里哪一行"。
- **只关心某个具体决策**(如 weight- vs output-stationary):直接跳 [dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md),它自带前置链接。
- **为建模而来**:先读[纲领](./compute-communication-ratio.md)再读 [08-modeling-for-archax](../08-modeling-for-archax/modeling-insights.md),中间各章按需回查。

---

## 5. 本篇在主线上的位置

这一篇是地图。COMPUTE 说明运算资源和数据需求，邻域说明各接口如何服务。复用可改变特定边界的 MAC/B；时序和工艺目标应分别评估。

---

## 建模启示

- 这张域边界表本身就是建模时**职责切分**的依据:COMPUTE 模型负责算术单元的面积/吞吐/频率;存储延迟分布交给 RAM 模型、互连带宽交给 NOC 模型、面积→成本交给 FAB 模型。一个 archax 级仿真器应在这些边界上对接,而不是在 COMPUTE 模型里重新实现 cache 命中率或 NOC 路由。
- **可折叠**:邻域的内部机制(DRAM 时序、router 流水)对 COMPUTE 模型可折叠成"边界处的带宽/延迟参数"。
- **必须保留**:边界处的接口量——array 进出口带宽、RF 端口数、跨单元线数——因为它们影响服务时间和吞吐。计算 MAC/B 还需记录该边界实际跨越的字节及有效 MAC 数。
