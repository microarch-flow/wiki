# UPMEM：同 die 可编程 PIM 案例

上级：[公司卡片](README.md)
相关：[CIM/PIM/NMC 分类](../../01-overview/cim-pim-nmc-taxonomy.md), [运行时与调度](../../06-software-stack/runtime-and-scheduling.md), [存储层次](../../05-architecture-and-system/memory-hierarchy-with-cim.md)

## 这页在回答什么问题

这页说明同 die DPU 的 PIM 结构、DIMM 产品形态和 host+DPU 编程边界。

| 字段 | 内容 |
| --- | --- |
| 公司/对象 | UPMEM DPU/PIM DIMM/server platform |
| 本 wiki 分类 | PIM：DPU 与 DRAM bank 位于同一 memory die |
| 技术路线 | DDR4 DIMM/server 形态下的大量 programmable DPU 近数据处理 |
| compute paradigm | programmable digital RISC near-data processing |
| 产品层级 | DIMM module、server reference platform、SDK |
| 目标市场 | database、analytics、data-intensive kernels、部分 AI/data preprocessing |

[UPMEM 实机研究](https://www.usenix.org/system/files/atc21-nider.pdf)描述 DPU 和 DRAM bank 集成在同一 DRAM die；每个 DPU 执行自己的程序并有私有工作存储，通过显式 DMA 在 MRAM 和 WRAM 间搬数据。DIMM/server 是交付层级，旧 `nmc-` 路径只为兼容。其他文献的 near-memory/PIM 可能采用更宽口径。聚合内部 DPU↔bank 带宽与 host DDR 通道带宽是不同边界，不能互换。

这张卡按同 die 独立处理归 PIM，并以 DIMM/server 形态讨论系统集成。它没有 analog array、没有 weight stored as conductance、没有 bitline MAC，主要工程问题转成 host orchestration、DPU code、DMA/data placement 和同步。

UPMEM 的软件栈是它的核心。官方材料强调 DPU 可用 C 或 Rust 编程，不需要 OS；GitHub 上也公开了 DPU SDK demo、LLVM fork 和应用示例。来源：[UPMEM GitHub](https://github.com/upmem)。这使它比 analog CIM 更容易被系统软件工程师理解，但也要求程序员显式划分 host 代码和 DPU 代码，管理数据局部性。

产业上，UPMEM 说明 near-data 路线可以先绕开 analog CIM 的校准和良率问题，但不能绕开系统集成问题。DPUs 数量越多，host 调度、数据分区、DPU-to-DPU 通信、global reduction、debug/profiling 和 fault isolation 就越重要；这些问题更接近 [NoC/backpressure/reduction](../../../../NOC/wiki/README.md) 与 [BUS/DMA/doorbell](../../../../BUS/wiki/README.md)，而不是 analog cell 物理。

主要风险：

| 风险 | 为什么重要 |
| --- | --- |
| 编程模型 | 客户需要重写或改造程序，把 work 分给 DPU |
| 通信与同步 | DPU 间缺少低成本全局通信时，reduction 和 irregular workload 会受限 |
| host integration | BIOS、driver、SDK、memory allocation 和 DMA 都影响可部署性 |
| 生态规模 | 可用库、示例和开发者数量决定 adoption |
| 分类边界 | 本书按同 die 独立 DPU 归 PIM；DIMM 是交付形态 |

## 一句话理解

UPMEM 是同 die 可编程 PIM：DIMM/server 部署仍需 host+DPU 程序划分、数据搬运和系统集成。

## 产业启示

独立数字 DPU 不需模拟阵列 ADC，但要计本地 DMA、host 分发与回收。该平台 DPU 间交换由 host 路径协调；不应假设存在直接全局互连。能效优劣须在相同工作量、精度、数据边界和系统功率下测量，不能由物理距离直接排序。
