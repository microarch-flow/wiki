# MMIO、Cache 与 Interrupt 视角

上级：[04 微架构与系统集成](./README.md)

相关：[Coherent Bus vs Non-Coherent Bus](../03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)、[CPU、DMA、外设与内存之间的总线路径](./dma-cpu-peripheral-memory-path.md)

## 这页在回答什么问题

软件看到的 MMIO、cacheable memory 和 interrupt，为什么会直接影响你该怎么理解 BUS。

## MMIO 不是普通内存

MMIO 虽然也通过地址访问，但语义不同：

- 读可能带副作用
- 写可能触发状态变化
- 访问顺序往往更敏感
- 不能简单当作 cacheable data 来处理

这意味着 BUS 不只是搬数据，还要配合系统定义好访问属性。

## Cacheable memory 路径更关注吞吐与一致性

CPU 访问普通 memory 时，更关心：

- cache hit/miss 后的填充路径
- cache line 粒度
- reorder 和 outstanding 能力
- 和 DMA 之间的一致性边界

所以同样是地址访问，MMIO 和 DRAM path 的要求完全不同。

## Interrupt 为什么也属于 BUS 视角的一部分

中断信号本身未必总走 BUS transaction，但它和 BUS 强相关，因为：

- 中断控制器通常通过 MMIO 配置
- 中断状态寄存器和清除路径走 BUS
- DMA completion 常通过 doorbell/status/interrupt 协同出现

理解 interrupt 路径时，不能只看一根 irq 线，还要看它背后的配置与状态访问是怎么接在 BUS 上的。

## 继续阅读

- 如果你在追 `doorbell、status 和 interrupt 是怎么串起来的`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `为什么 MMIO 不能按普通内存来想`：看 [APB、MMIO 与普通内存的软件模型对照](../06-scenarios-case-studies/apb-mmio-memory-software-model.md)
- 如果你在追 `访问属性和 barrier 为什么会影响 MMIO correctness`：看 [AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)
- 如果你在追 `CPU 读寄存器为什么会直接卡死`：看 [CPU 读 MMIO 卡死案例卡](../06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)

## 常见误区

- “统一地址空间就代表语义一样”
- “MMIO 只是慢一点的内存”
- “中断系统和 BUS 无关”

## 一句话理解

MMIO、cacheable memory 和 interrupt 共同决定了 BUS 不只是物理互连，而是软件可见的系统语义边界。
