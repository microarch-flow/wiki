# 学习路线与域边界:原语 → 阵列 → 流水 → 布局

上级:[COMPUTE 域总览](./README.md)
相关:[算力单元要解决什么问题](./problem-statement.md)、[计算 / 通信比(全域纲领)](./compute-communication-ratio.md)

---

## 这页在回答什么问题

两件事:(1) COMPUTE 域内部该按什么顺序读——为什么是"自底向上从门到布局",而不是别的顺序;(2) COMPUTE 域和已有的 BUS/RAM/NOC/DMA/FAB/CIM/Workload 各域的**边界在哪**,避免重复造轮子。

---

## 1. 为什么自底向上

这条路线刻意复刻基准长文(Pope 黑板讲座)的顺序:**从一个逻辑门开始,每上一层都在解决下一层暴露出来的"搬运吃掉面积"问题。** 自底向上的好处是每一层的设计动机都由下一层的痛点驱动,不会变成术语罗列。

```
门 ──▶ MAC ──▶ datapath(mux 暴露搬运问题)
                      │
                      ▼ 搬运占 6/7,怎么办?
              systolic array(上提循环,翻转比值)
                      │
                      ▼ 阵列要跑多快?
              时钟 / 流水(同步的代价,频率≠吞吐)
                      │
                      ▼ 这些门要不要可重配?
              FPGA vs ASIC(可配置性的 10× 税)
                      │
                      ▼ 算完的数从哪来?
              cache vs scratchpad(确定性 discipline)
                      │
                      ▼ 把这些拼成一个核 / 一片芯片
              CPU/GPU core ──▶ GPU = 平铺的 TPU
                      │
                      ▼ 怎么把它喂进仿真器?
              archax 建模启示
```

每一步的"▼ 痛点"就是下一章的存在理由。这正是[计算 / 通信比](./compute-communication-ratio.md)在六个层级反复出现的具体顺序。

---

## 2. 章节地图

| 章节 | 主题 | 在主线上推比值的手段 |
|---|---|---|
| 01-overview | 问题 + 纲领 + 路线 | 定义比值本身 |
| 02-datapath-foundations | 从门搭 MAC、压缩树、位宽、数字格式、mux 成本 | 降精度(分子)+ 暴露 mux(分母) |
| 03-systolic-array | 阵列、dataflow、trickle-feed、sizing | 上提循环,净赚 y 倍 |
| 04-clocking-and-pipeline | 全局时钟、流水寄存器、反馈环、频率≠吞吐 | 同步是纯分母,别过切 |
| 05-fpga-vs-asic | LUT/mux 的可配置开销 | 固化省掉 10× 配置税 |
| 06-memory-discipline | cache vs scratchpad | 把分母变确定 |
| 07-chip-organization | CPU/GPU 核面积、脑 vs 芯片功耗、GPU=平铺 TPU | 砍专用化不需要的分母 |
| 08-modeling-for-archax | 7 条建模启示升格 | 把比值做成 IR 一等量 |

`[补全]` 篇(长文未展开、本域完整性需要):`dadda-and-adder-trees`、`number-formats-for-ai`、`dataflow-taxonomy`。其余以长文对应内容为**深度下限**。

---

## 3. 域边界:COMPUTE 不重写什么

COMPUTE 域聚焦"数据搬到之后怎么算、为什么算力单元长这样"。它的**分母**(数据搬运、存储、互连、制造)恰好是其他域的主体。下表划清边界——COMPUTE 只建接口,不重写邻域内容:

| 邻域 | 它负责的 | COMPUTE 这边的接口篇 | 边界一句话 |
|---|---|---|---|
| **RAM** | SRAM/DRAM 器件、MC、NPU 存储层次 | [cache-vs-scratchpad](../06-memory-discipline/cache-vs-scratchpad.md) | RAM 从器件看 SRAM;COMPUTE 从"算力单元要确定性延迟"看同一块 SRAM |
| **CIM** | 存内计算路线(SRAM/ReRAM/模拟/数字) | [why-systolic-array](../03-systolic-array/why-systolic-array.md)、[dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md) | systolic 权重存数字 register 仍取数后算;CIM 读出即算。边界=驻留处是否就是计算处 |
| **NOC** | 拓扑、路由、flow control | [weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md)、[gpu-as-tiled-tpu](../07-chip-organization/gpu-as-tiled-tpu.md) | COMPUTE 管 array 边界 x 量级带宽;NOC 管这些流怎么在片上路由 |
| **DMA** | 描述符、多维 stride、double-buffering | [weight-loading-and-trickle-feed](../03-systolic-array/weight-loading-and-trickle-feed.md) | trickle 是一次性窄带配置流;DMA double-buffer 是稳态数据流 |
| **FAB** | 工艺节点、PPA、良率、tape-out、封装 | [quadratic-bitwidth-scaling](../02-datapath-foundations/quadratic-bitwidth-scaling.md)、[pipeline-register-insertion](../04-clocking-and-pipeline/pipeline-register-insertion.md) | COMPUTE 给"省多少门";FAB 给"门→mm²→成本/良率" |
| **Workload** | CNN/Transformer/BEV/VLA 等负载特征 | [dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md)、[frequency-is-not-throughput](../04-clocking-and-pipeline/frequency-is-not-throughput.md) | COMPUTE 给硬件结构;Workload 给"什么负载的复用结构适配哪种 dataflow" |

> Workload 是独立仓库(`/mnt/e/workload-wiki`),跨仓链接用 `../../../../workload-wiki/...` 相对路径(同盘可点击)。目标页:[`cnn-backbone`](../../../../workload-wiki/01-foundation-model-components/cnn-backbone.md)、[`attention-and-transformer`](../../../../workload-wiki/01-foundation-model-components/attention-and-transformer.md)、[`attention-variants-and-efficiency`](../../../../workload-wiki/01-foundation-model-components/attention-variants-and-efficiency.md)。若两仓分别发布,这些跨仓链接需按发布结构重映射。

---

## 4. 怎么读:三种进入路径

- **想从头建立直觉**:按 01→08 顺序通读,每章读完回到[纲领篇](./compute-communication-ratio.md)对一眼"这章在表里哪一行"。
- **只关心某个具体决策**(如 weight- vs output-stationary):直接跳 [dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md),它自带前置链接。
- **为建模而来**:先读[纲领](./compute-communication-ratio.md)再读 [08-modeling-for-archax](../08-modeling-for-archax/modeling-insights.md),中间各章按需回查。

---

## 5. 本篇在主线上的位置

这一篇是**地图**,不推比值,只规定看比值的顺序和视角:自底向上,每层由下层痛点驱动;邻域负责分母的器件实现,COMPUTE 负责"为什么算力单元为抬高比值而长成这样"。

---

## 建模启示

- 这张域边界表本身就是建模时**职责切分**的依据:COMPUTE 模型负责算术单元的面积/吞吐/频率;存储延迟分布交给 RAM 模型、互连带宽交给 NOC 模型、面积→成本交给 FAB 模型。一个 archax 级仿真器应在这些边界上对接,而不是在 COMPUTE 模型里重新实现 cache 命中率或 NOC 路由。
- **可折叠**:邻域的内部机制(DRAM 时序、router 流水)对 COMPUTE 模型可折叠成"边界处的带宽/延迟参数"。
- **必须保留**:边界处的接口量——array 进出口带宽、RF 端口数、跨单元线数——因为它们直接决定计算 / 通信比能否在该层级被算出来。
