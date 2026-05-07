# DMA 对照矩阵

上级：[08 DMA IP 与产业视角](./README.md)

相关：[CPU / GPU / NPU 系统中的 DMA 分工](../07-workloads-case-studies/cpu-gpu-npu-comparison.md)、[DMA IP 评估清单](./dma-ip-checklist.md)

## 这页在回答什么问题

把不同类型 DMA 放在同一张矩阵里，对比它们最关键的系统差异。

| 类型 | 典型位置 | 主要路径 | 最核心约束 | 最关键能力 |
| --- | --- | --- | --- | --- |
| SoC AXI DMA | 片上互连 | DDR/SRAM/外设 | burst、仲裁、内存端 | 高效片上搬运 |
| Peripheral DMA | 外设旁 | FIFO<->memory | 实时性、稳定流 | 低 CPU 开销 |
| PCIe NIC DMA | 设备侧 | host<->NIC buffer | ring、completion、小包压力 | batching 与 moderation |
| NVMe DMA | 设备侧 | host<->storage queue | 深队列、completion 稳定性 | 高并发 steady-state |
| GPU Copy Engine | GPU 内外边界 | host<->device / device<->device | overlap、stream 竞争 | 异步数据流水 |
| AI Local DMA | tile/cluster 邻近 | HBM/NoC/SRAM/tile | bank/port、outstanding、供数节奏 | 与 compute 强耦合 |

## 怎么用这张表

先不要问“哪种 DMA 最强”，而是先问：

- 你的系统更像哪一列
- 你的主瓶颈更像哪种约束
- 你需要通用性还是需要固定路径效率

## 一句话理解

不同 DMA 的差异，本质上来自它们服务的数据路径、软件契约和系统瓶颈完全不同。
