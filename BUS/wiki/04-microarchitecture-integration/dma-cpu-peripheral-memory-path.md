# CPU、DMA、外设与内存之间的总线路径

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[RAM Wiki 首页](../../../RAM/wiki/01-overview/README.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)、[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)

## 这页在回答什么问题

BUS 不能孤立成“某个协议接口”来看。一次真实系统行为会同时经过 CPU 控制路径、DMA 取任务路径、数据搬运路径、completion/writeback 路径、interrupt/status 路径，以及 debug/boot/低功耗路径。CPU、DMA、外设和 memory 之间的关系，决定了 BUS 设计是否能支撑软件流程闭环。

这页作为第 04 章的系统路径收束：把前面讨论的 bridge、MMIO、IOMMU、doorbell、DMA、DDR controller、return path 放回同一个端到端流程里。

## 控制路径：CPU 配置设备

控制路径的目标是让软件能配置、启动、查询和恢复硬件。它的流量小，但语义强。

```text
CPU
  -> main interconnect
  -> bridge / low-speed peripheral bus
  -> DMA or peripheral register block
```

| 控制动作 | BUS 语义 | 风险 |
| --- | --- | --- |
| 写配置寄存器 | MMIO write，带 side effect | 写顺序错误导致设备使用旧配置 |
| 写 doorbell/start | MMIO write 触发硬件状态机 | descriptor 或 buffer 尚未可见 |
| 读 status/error | MMIO read，可能有 read side effect | 读清状态或读到未同步状态 |
| 写 clear/reset | MMIO write 改变中断或设备状态 | clear/EOI 顺序错误导致丢事件 |

控制路径偏向可诊断性和稳定性。它可能走 APB/AHB/AXI-Lite 或厂内低速 fabric；协议名不是重点，重点是访问顺序、side effect、错误返回和 low-power/reset 状态。

## 数据路径：DMA 与 Memory 交换数据

数据路径的目标是高吞吐、可并发和可恢复。DMA 作为 master 发起 read/write，目标可能是 DDR、SRAM、外设 FIFO、accelerator local memory 或另一片互连。

```text
DMA master
  -> IOMMU/SMMU or permission check
  -> interconnect / crossbar
  -> memory controller / SRAM / peripheral bridge
  -> response / return path
```

| 数据路径问题 | 影响 |
| --- | --- |
| DMA 与 CPU 争同一 DDR controller | CPU tail latency 或 DMA throughput 下降 |
| DMA source/destination 落在不同 fabric | bridge、CDC、width adapter 改变节奏 |
| DMA 经过 IOMMU/SMMU | translation miss 和 fault 改变 latency/错误归因 |
| DMA 写 completion 与 data write 共用路径 | 软件可见完成被拖后 |
| return path 与其他 master 共享 | read data 或 response 抖动 |

数据路径不能只看峰值带宽。source、destination、burst、outstanding、address mapping、QoS、SMMU、DDR scheduler 和 return path 一起决定实际体验。

## 完成路径：软件如何知道硬件做完了

硬件完成一件事，不等于软件已经知道。完成路径把硬件状态重新带回 CPU。

```text
DMA / peripheral
  -> completion writeback or status update
  -> interrupt controller or polling-visible state
  -> CPU ISR / driver
  -> clear / EOI / next task
```

| 完成对象 | BUS 路径 | 正确性条件 |
| --- | --- | --- |
| completion record | DMA write memory | CPU 能看到最新 completion |
| status register | MMIO visible state | status 与 completion 一致 |
| interrupt | event 到 interrupt controller | interrupt 不早于 completion/status 可见 |
| clear/EOI | CPU MMIO write | clear 真正到达目标 |
| next descriptor | CPU/DMA 再次访问 memory | 前一任务资源已释放 |

完成路径是控制路径和数据路径的闭环。若 completion 丢失、interrupt 早到、clear 延迟或 cache 可见性错误，软件会把已经完成的任务当成未完成，或把未完成的任务当成完成。

## 四类路径的组合

| 路径 | 主要发起方 | 典型目标 | 主要关注 |
| --- | --- | --- | --- |
| control path | CPU/debug | MMIO register | 顺序、副作用、错误可诊断 |
| descriptor path | DMA | memory descriptor | cache 可见性、IOMMU、fetch latency |
| data path | DMA/CPU/device | memory/SRAM/peripheral | bandwidth、outstanding、QoS、return path |
| completion path | DMA/device/CPU | memory/status/interrupt controller | completion 可见性、interrupt/clear 顺序 |

同一个系统行为会跨越这些路径。建模时若只画一条 `CPU -> DMA -> memory`，就会漏掉 descriptor 可见性、doorbell 顺序、writeback、interrupt 和 clear/EOI。

## 例子：CPU 启动 DMA 搬运外设数据到内存

| 阶段 | 事件 | BUS 路径 | 关键状态 |
| --- | --- | --- | --- |
| T0 | CPU 分配 destination buffer | CPU memory path | cache/IOMMU mapping 准备 |
| T1 | CPU 写 descriptor | CPU -> memory | descriptor fields 完整 |
| T2 | CPU clean/barrier | cache/memory system | descriptor 对 DMA 可见 |
| T3 | CPU 写 DMA doorbell | CPU -> MMIO -> DMA | control path 完成 |
| T4 | DMA fetch descriptor | DMA -> SMMU -> memory | descriptor read success |
| T5 | DMA 从外设或 memory 读源数据 | DMA data read path | source ready、response 正确 |
| T6 | DMA 写 destination memory | DMA data write path | write response、DDR/SRAM 可见性 |
| T7 | DMA 写 completion record | writeback path | completion visible to CPU |
| T8 | DMA 触发 interrupt | interrupt path | CPU 被唤醒 |
| T9 | CPU ISR 读 completion/status | CPU memory/MMIO path | cache/coherence 正确 |
| T10 | CPU 写 clear/EOI | CPU -> MMIO | interrupt 状态释放 |

这个例子把第 04 章的多数主题串在一起：MMIO doorbell、cache/barrier、IOMMU、DMA AXI master、DDR controller、completion writeback、interrupt 和 clear。任何一段出错，软件看到的都可能只是“DMA 没完成”。

## BUS 与 NoC 的边界

在大规模 SoC 或 AI 芯片里，BUS 与 NoC 的分工应按语义而不是按名字划分。

| 系统部分 | 更适合 BUS 的责任 | 更适合 NoC/高吞吐 fabric 的责任 |
| --- | --- | --- |
| 控制寄存器 | 配置、启动、状态、错误 | 不适合承载大量配置碎片 |
| DMA/队列控制 | doorbell、completion、interrupt | 大规模数据搬运可走高吞吐网络 |
| memory access | 中小规模共享路径、SRAM、DDR 接入 | 多 tile、多 HBM、多 accelerator 流量 |
| debug/boot | 最小可达、可诊断路径 | 不宜依赖复杂运行态网络 |

边界的设计取舍是：BUS 提供软件语义、可诊断性和低复杂度；NoC 或高吞吐 fabric 提供规模化并发和长距离带宽。两者需要通过 bridge、address map、QoS 和错误路径连接，而不是互相替代。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| BUS 只负责连通 | BUS 还承载软件可见语义、错误、顺序和完成 |
| 控制路径流量小，可以忽略 | doorbell/status/clear 的延迟和顺序会改变软件行为 |
| 数据路径带宽够，系统就完成 | completion、interrupt 和 cache 可见性仍可能失败 |
| DMA 是单一 master | DMA 至少涉及控制、descriptor、data、writeback 多条路径 |
| NoC 出现后 BUS 不重要 | BUS 仍负责配置、状态、boot、debug 和系统语义边界 |

## 一句话理解

CPU、DMA、外设和 memory 之间的 BUS 路径是一组控制、数据、完成和诊断路径的闭环，而不是一条孤立连线。

## 建模启示

系统级 BUS 要按端到端软件流程建模。性能模型要分别记录 control path、descriptor path、data path、completion path、interrupt path 的 latency、bandwidth、queue、QoS、bridge、SMMU/IOMMU、DDR controller 和 return path。功能模型要记录 MMIO side effect、cache/coherence、barrier、address translation、error response、completion visibility、interrupt pending/clear、debug access 和 boot/low-power 可达性。

事件模型建议显式表达 `cpu_config_write`、`descriptor_visible_to_dma`、`doorbell_write_accept`、`dma_descriptor_fetch_done`、`dma_data_move_done`、`completion_visible_to_cpu`、`interrupt_assert`、`isr_status_read`、`interrupt_clear_done`、`debug_read_state`。这些事件把 BUS 从“连线图”提升为软件流程能否闭环的状态机。
