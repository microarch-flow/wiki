# Coherent Bus vs Non-Coherent Bus

上级：[03 片上总线协议族](./README.md)

相关：[BUS 分类框架](../01-overview/taxonomy.md)、[AXI 属性、Cacheability 与 Barrier](../04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)、[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)、[DMA 与 NoC](../../../DMA/wiki/05-system-integration/dma-and-noc.md)

## 这页在回答什么问题

什么时候片上互连只需要搬运 memory-mapped transaction，什么时候还要维护多个 cacheable agent 之间的共享内存可见性。

## Coherence 解决的是共享内存视图

Non-coherent interconnect 负责把 request 送到目标、把 data 和 response 带回来，并按协议处理地址、属性、burst、ordering 和 error。它可以很高性能，也可以支持 AXI outstanding、burst 和复杂 arbitration；但它不负责维护 CPU cache、DMA、accelerator 或其他 cacheable agent 之间的缓存副本一致性。

Coherent interconnect 在 transaction 搬运之外，还要维护共享内存视图：谁拥有某条 cache line 的最新数据，谁可以读，谁可以写，哪些副本需要失效，写入何时对其他 agent 可见。它处理的不只是“把数据送到哪里”，而是“多个观察者看到同一地址时，哪个值是合法可见值”。

这个差异是系统语义差异，不是性能等级差异。Non-coherent 路径可以很快，coherent 路径也可能因为 snoop、目录、状态转换和冲突而变慢。选择哪一种，取决于软件和硬件是否需要自动维护 cache-line 可见性。

容易误解：coherent bus 就是更高级的 AXI。实际上，coherence 是额外的共享内存语义；普通 AXI 数据通路可以 non-coherent，带一致性扩展或一致性协议的路径才承担这类状态。

## Non-coherent 路径把可见性交给软件或上层机制

Non-coherent DMA 的典型问题是：CPU cache 里有一份数据，DMA 直接访问 memory 中的另一份数据。CPU 写了 descriptor，如果 dirty cache line 没有被 clean 到 memory，DMA 可能读到旧 descriptor；DMA 写回 completion buffer 后，如果 CPU cache 里仍有旧副本，CPU 可能看不到最新 completion。

这不是 DMA 搬运失败，而是可见性契约没有闭合。Non-coherent 路径需要软件、driver、runtime 或系统库显式管理 ownership、cache clean/invalidate、memory attribute 和 barrier 顺序。

一个最小方向判断：

| 方向 | 风险 | 需要建立的可见性 |
|---|---|---|
| CPU -> DMA/device | CPU 写仍停在 cache | clean/flush 后 device 才能读到新数据 |
| DMA/device -> CPU | CPU cache 仍有旧副本 | invalidate 后 CPU 才能重新取到 device 写回 |
| CPU 写 descriptor 后敲 doorbell | doorbell 先被 device 看见 | descriptor 可见性要早于 MMIO doorbell |

Barrier 只能约束顺序，不能凭空把脏 cache line 变成 device 可见；IOMMU/SMMU 解决地址翻译和权限，也不自动解决 cache coherence。把这些机制混成一件事，是 non-coherent DMA bug 的主要来源。

容易误解：non-coherent 只影响性能。实际上，它直接影响正确性；软件看到的“DMA 数据错了”，常来自 cache 可见性没有按方向处理。

## Coherent 路径把可见性维护放进硬件协议

Coherent interconnect 会让 cacheable agent 的访问参与一致性协议。一个 master 读某条 cache line 时，系统可能需要查询其他 cache 是否持有更新副本；一个 master 想写时，系统可能需要获取 ownership 并让其他副本失效；一个 DMA 或 accelerator 若作为 coherent agent 接入，也可能通过一致性协议访问 CPU cacheable memory。

硬件自动维护可见性后，软件模型更简单：driver 不必为每个 buffer 手工 clean/invalidate，CPU 和 device 更容易共享同一份 memory view。代价是协议状态大幅增加：snoop、directory、cache line state、ownership、probe response、data intervention、ordering 和 deadlock avoidance 都会进入设计和验证范围。

Coherent 并不等于“软件无需管理”。软件仍要处理同步顺序、lock/barrier、device ownership、IOMMU mapping、权限、NUMA/cluster 拓扑和性能竞争。Coherence 解决 cache-line 可见性，不替代并发编程里的同步约束。

容易误解：coherent DMA 不需要 barrier。实际上，coherence 解决数据可见性，barrier/lock 仍负责访问之间的顺序和同步点。

## MMIO 和普通内存不能混成一类

MMIO/device register 路径即使经过同一个 interconnect，也不应该按普通 cacheable memory 理解。寄存器访问可能有 write side effect、read-to-clear、write-1-to-clear、状态触发和强顺序需求。把 MMIO 标成 cacheable，或让它参与普通 cache line 填充，会破坏设备语义。

因此，一个系统可以同时存在：

- coherent memory path：CPU cluster、coherent DMA、shared cacheable memory。
- non-coherent data path：显式 managed DMA buffer、NPU local SRAM、device memory window。
- device/MMIO path：寄存器配置、doorbell、status、interrupt controller。

这些路径可能共享某些物理 fabric 或 bridge，但软件属性和协议语义不同。互连必须把 cacheability、shareability、device memory、barrier 和 response 语义传递或转换清楚。

容易误解：统一地址空间表示统一缓存语义。实际上，同一个地址空间里可以有 cacheable memory、non-cacheable memory 和 device/MMIO 区域，访问语义完全不同。

## Coherent 边界是局部系统设计选择

一致性边界不一定覆盖整颗芯片。CPU cluster 内部、LLC 附近、某些 coherent accelerator 或 coherent DMA 端口可能参与一致性；低速外设、APB 寄存器子树、debug 访问、本地 scratchpad 和部分 NPU dataflow 仍然可以是 non-coherent 或 device 语义。

判断一条路径是否需要 coherence，可以问三个问题：

- 这个 agent 是否会直接访问 CPU cacheable memory。
- 软件是否希望省掉显式 clean/invalidate ownership 切换。
- 硬件是否愿意为 cache-line state、snoop/directory 和验证复杂度付费。

如果答案是否定的，non-coherent transaction 加清楚的软件契约可能更合适。如果答案是肯定的，coherent interconnect 能降低软件维护成本，但会把复杂度搬到硬件协议和系统验证里。

## 一句话理解

Non-coherent bus 负责事务搬运和 completion，cache 可见性由软件或上层机制闭合；coherent bus 还要维护 cache-line ownership、副本失效和共享内存可见性，因此换来更简单的软件共享模型和更高硬件复杂度。

## 建模启示

建模 coherent/non-coherent 边界时，不能只记录协议名字。模型要记录每条路径的 memory attribute：cacheable 还是 device，shareable 还是 non-shareable，agent 是否参与 coherent domain，DMA buffer 是否需要 software ownership transfer，MMIO 是否有副作用。

Non-coherent 模型要显式表示 cache maintenance 和同步点。CPU 写 buffer 后，device 不能自动看到 cache 中的脏数据；device 写回后，CPU 也不能自动绕过旧 cache 副本。性能模型可以把 clean/invalidate 折叠成开销，功能模型必须把它们当作可见性前置条件。

Coherent 模型要增加 cache-line state、snoop/probe、ownership、directory 或广播范围、response dependency 和可能的 deadlock/backpressure。若只把 coherent path 当作普通 AXI read/write，会漏掉一致性流量和状态转换对延迟、带宽和正确性的影响。

MMIO 路径要单独建模。寄存器访问的关键不是 cache coherence，而是副作用、顺序、错误和 completion。把 MMIO 放进 coherent memory 模型，或把 coherent memory 当成普通 non-coherent DMA buffer，都会在系统级仿真里产生错误结论。
