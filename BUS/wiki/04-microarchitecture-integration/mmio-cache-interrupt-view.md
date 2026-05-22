# MMIO、Cache 与 Interrupt 视角

上级：[04 微架构与系统集成](./README.md)

相关：[Coherent Bus vs Non-Coherent Bus](../03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)、[AXI Narrow Transfer 与 WSTRB](../03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)、[AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)、[CPU、DMA、外设与内存之间的总线路径](./dma-cpu-peripheral-memory-path.md)、[Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)

## 这页在回答什么问题

软件看到的是同一个地址空间：读写内存、访问寄存器、处理中断状态。BUS 看到的却不是同一种事务。MMIO、cacheable memory 和 interrupt 分别代表三类软件可见语义：寄存器副作用、缓存一致性边界、异步事件通知。

这页讨论这些语义如何落到 BUS 路径上。核心问题不是“地址是否能访问”，而是访问属性是什么、能不能缓存、能不能重排、读写是否有副作用、完成事件通过什么路径返回软件。

## MMIO 不是慢一点的内存

MMIO 使用 load/store 形式访问，但它的语义接近设备命令和状态查询。一个寄存器读可能清除状态，一个寄存器写可能启动 DMA、清中断、复位模块或改变时钟。

| 访问类型 | Memory 语义 | MMIO 语义 |
| --- | --- | --- |
| read | 读取数据，重复读取应得到内存状态 | 可能触发 clear-on-read、pop FIFO、采样硬件状态 |
| write | 写入可缓存数据，后续可被合并或回写 | 可能触发动作，写入顺序和 byte strobe 有意义 |
| reorder | 可在规则允许下重排 | 设备寄存器访问需要更严格的顺序 |
| cache | 可进入 cache hierarchy | 不应按普通 cacheable data 处理 |
| partial access | 可由 memory system 支持 | 可能违反寄存器定义或触发错误 |

MMIO 路径的设计动机是让软件用统一指令访问设备，同时保留设备语义。代价是 BUS 必须携带或推导访问属性，例如 device、non-cacheable、strongly ordered、secure、privileged、read/write permission。若这些属性在 bridge 或互连中被丢弃，软件代码看似正确，硬件行为仍可能错误。

## Cacheable Memory 路径关注吞吐和一致性

cacheable memory 的目标是降低平均访问延迟并提升带宽。CPU load/store 可能命中 cache，也可能通过 miss path 触发 cache line fill；DMA 访问 memory 可能绕过 CPU cache，也可能走 coherent path。

| 问题 | Cacheable memory | MMIO |
| --- | --- | --- |
| 粒度 | cache line、burst、bank | register、field、side effect |
| 优化目标 | 吞吐、命中率、bank locality | 顺序、可见性、错误可诊断 |
| 合并写 | write combine 可能提升效率 | 合并可能改变设备语义 |
| 预取 | 可提升顺序读性能 | 预取寄存器可能触发副作用 |
| outstanding | 可用来隐藏 memory latency | 需要避免破坏寄存器顺序 |

这也是 DMA 与 CPU 共享 memory 时容易出错的原因。CPU 修改 descriptor 后，DMA 看到的 memory 状态取决于 cache clean、coherence、barrier 和访问属性；DMA 写回 completion 后，CPU 读取结果前可能需要 invalidate 或等待 coherent completion。BUS 模型不能只记录“CPU 和 DMA 都能访问 DDR”，还要记录 cache 可见性边界。

## Interrupt 是异步事件，但配置和状态走 BUS

interrupt signal 本身可以是专用线、消息、中断控制器输入或更复杂的 fabric 事件，但它背后的配置、mask、pending、clear、priority 和 completion 常落在 MMIO 路径上。

| 环节 | BUS 相关动作 | 建模关注点 |
| --- | --- | --- |
| enable | CPU 写 interrupt controller 或外设 enable 寄存器 | 写顺序、寄存器副作用、是否需要 barrier |
| event | 外设或 DMA 产生 completion/event | event 与 status 写入的先后关系 |
| pending | interrupt controller 记录 pending 状态 | pending 位是否通过 MMIO 可见 |
| service | CPU 读 status、读取 completion queue | MMIO read 是否清状态，memory read 是否需要 cache 同步 |
| clear / EOI | CPU 写 clear 或 end-of-interrupt | clear 是否到达设备，是否可能丢事件 |

因此，理解 interrupt 不能只看一根 irq 线。若 DMA 先拉中断、后写 completion status，CPU 可能被唤醒后读到旧状态；若 CPU 清中断的 MMIO write 被缓存在 write buffer 里，设备可能继续保持 pending；若 status 在 cacheable memory 中，CPU 还要处理 cache 可见性。

## 例子：DMA Completion 到 CPU ISR

一个 DMA 完成传输后通知 CPU，可以拆成下面的 BUS 事件链：

| 阶段 | 事件 | BUS 路径 | 风险 |
| --- | --- | --- | --- |
| T0 | CPU 写 DMA descriptor | CPU -> cache/memory path | descriptor 可能仍在 cache 中 |
| T1 | CPU 写 DMA start MMIO | CPU -> interconnect -> DMA register | start write 需要在 descriptor 可见之后发生 |
| T2 | DMA 读取 descriptor | DMA -> DDR/SRAM | 若非 coherent，需要依赖 clean/barrier |
| T3 | DMA 写 completion status | DMA -> memory 或 MMIO status | 写入是否对 CPU 可见 |
| T4 | DMA 触发 interrupt | DMA -> interrupt controller | interrupt 不应早于 completion 可见 |
| T5 | CPU ISR 读取 status | CPU -> MMIO 或 memory | MMIO read 可能清状态，memory read 可能需要 invalidate |
| T6 | CPU 写 clear/EOI | CPU -> MMIO | clear write 是否真正到达设备 |

这个例子把三类路径放到一起：descriptor 和 completion 是 memory 语义，DMA start 和 clear 是 MMIO 语义，interrupt 是异步通知。正确性依赖它们之间的 ordering，而不是依赖某一条路径单独正确。

## 属性、Barrier 与可见性

访问属性和 barrier 的价值在于把软件意图变成 BUS 约束。

| 软件意图 | BUS 需要表达的约束 | 缺失后的症状 |
| --- | --- | --- |
| descriptor 先于 DMA start 可见 | memory write 完成后再发 MMIO start | DMA 读取旧 descriptor |
| status 写入先于 interrupt 可见 | DMA write completion 后再触发 event | ISR 读不到完成状态 |
| 清中断写必须到达设备 | MMIO write 不被无限延后 | 中断反复进入 |
| MMIO read 不能被预取 | device/non-cacheable 属性 | 读取触发意外副作用 |
| 多寄存器配置保持顺序 | ordered device access 或 barrier | 设备进入非法中间状态 |

barrier 不是替代协议的魔法指令。它约束 CPU、cache、store buffer 和 interconnect 对某些访问的可见顺序，但前提是地址属性、bridge 映射和设备语义都匹配。若某段 MMIO 被错误标成 cacheable，barrier 也无法把被缓存的寄存器访问变成正确设备访问。

## Side Effect 与访问粒度

MMIO 寄存器带有 field 级语义时，BUS 的 byte lane 和 strobe 会影响结果。

| 寄存器行为 | BUS 风险 | 建模方式 |
| --- | --- | --- |
| write-one-to-clear | 宽写或合并写可能清错 bit | 记录 WSTRB、写值和 field mask |
| clear-on-read | speculative read 或重复读改变状态 | 禁止预取，记录 read side effect |
| FIFO data register | 每次 read pop 一个元素 | read 事件不能被合并或重放 |
| command register | write 触发动作 | 写入顺序和 completion 要可观察 |
| split 64-bit register | 两个 32-bit access 组成一个值 | 记录 latch 规则和访问顺序 |

位宽适配器和 bridge 在 MMIO 路径上必须更保守。把两个 32-bit register 合并成一次 64-bit write，或者把一次 64-bit write 拆成两个 32-bit write，都可能改变设备行为。模型需要把寄存器粒度和 bus transfer 粒度同时表达出来。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| 统一地址空间代表统一语义 | 地址形式相同，不代表 cache、ordering、side effect 相同 |
| MMIO 只是延迟更高的 memory | MMIO 是设备命令和状态路径，读写可能有副作用 |
| interrupt 和 BUS 无关 | interrupt 的 enable、status、clear、EOI 和 completion 多数通过 BUS 可见 |
| coherent path 能解决所有同步问题 | coherence 解决 cache 可见性，不替代设备寄存器顺序和 interrupt 协议 |

## 一句话理解

MMIO、cacheable memory 和 interrupt 共同定义了软件可见的 BUS 语义：数据何时可见、设备何时动作、事件何时通知。

## 继续阅读

- 如果你在追 `doorbell、status 和 interrupt 是怎么串起来的`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `为什么 MMIO 不能按普通内存来想`：看 [APB、MMIO 与普通内存的软件模型对照](../06-scenarios-case-studies/apb-mmio-memory-software-model.md)
- 如果你在追 `访问属性和 barrier 为什么会影响 MMIO correctness`：看 [AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)
- 如果你在追 `CPU 读寄存器为什么会直接卡死`：看 [CPU 读 MMIO 卡死案例卡](../06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)

## 建模启示

MMIO、cacheable memory 和 interrupt 要一起建模，因为软件流程会跨越三种语义。性能模型要区分 memory path、MMIO path 和 interrupt/status path 的 latency、队列、bridge、cache 可见性和回压。功能模型要记录访问属性、side effect、WSTRB、ordering、barrier、coherence、interrupt pending/clear 和 completion 可见性。

事件模型建议显式表达 `mmio_write_accept`、`mmio_side_effect`、`cache_clean_done`、`dma_read_descriptor`、`completion_write_visible`、`interrupt_assert`、`isr_status_read`、`interrupt_clear_done`。这些事件的相对顺序，决定软件看到的是正确完成、旧状态、重复中断，还是一次难以定位的 hang。
