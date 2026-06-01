# AXI / PCIe 视角下的 DMA

上级：[05 系统集成](./README.md)

相关：[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[PCIe NIC DMA 案例卡](../07-workloads-case-studies/pcie-nic-dma-case-card.md)、[AXI DMA 案例卡](../07-workloads-case-studies/axi-dma-case-card.md)

## 这页在回答什么问题

为什么同样叫 DMA，挂在 AXI 互连里的 DMA 和跑在 PCIe 设备里的 DMA，在约束、瓶颈和软件契约上会显著不同；以及 DMA 语义分别是如何落到 AXI 五通道和 PCIe TLP/completion 上的。

## AXI 视角下，DMA 是片上 master

在 AXI 语境里，DMA 最核心的身份是 master。descriptor 被解析后，DMA 会在读路径上发 `AR`，在写路径上发 `AW/W`，并接收 `R/B` 返回。也就是说，`DMA ↔ BUS(AXI)` 的关键关系，不是“DMA 用 AXI 访问内存”这么泛，而是：

- descriptor 描述的逻辑搬运会被拆成若干 `AR/AW` request
- data read 通过 `R` 通道返回
- write completion 通过 `B` 通道闭环
- outstanding 深度、本地 reorder 能力和 AXI ID 组织共同决定 latency hiding

这正是为什么你必须把 DMA 的 burst 行为映射到 [BUS wiki 的 AXI 五通道](../../../BUS/wiki/03-on-chip-protocol-families/axi-five-channels-handshake.md) 和 [ID / outstanding](../../../BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding.md) 上去看。DMA 的“并发能力”在 AXI 视角里并不是抽象词，而是具体表现为它能同时挂多少 `AR/AW`、如何接 `R/B`、能否处理乱序返回。

## AXI DMA 最常见的系统约束是什么

AXI DMA 典型地深耦合于片上 memory hierarchy，因此它最常见的约束包括：

- burst 长度与对齐
- 4KB 边界或实现定义边界拆分
- read/write 通道共享的 endpoint 压力
- AXI arbitration、QoS 与返回路径尾延迟

所以 AXI DMA 常像“片上供数器”或“片上搬运器”，它关心的是怎样把 descriptor 变成互连友好的 burst 形状，并在 shared fabric 上维持 forward progress。

## PCIe 视角下，DMA 是设备侧发起者

到了 PCIe，DMA 的身份变成设备侧事务发起者。它面对的不是片上共享 memory hierarchy，而是 host memory、IOMMU、BAR、TLP、MSI-X 和 host software contract。此时 `DMA ↔ PCIE` 的关键关系是：

- device DMA read / write 会被编码成 memory read / memory write TLP
- posted write 与 non-posted read 的代价不同
- read 结果通过 completion TLP 返回
- 软件侧 completion interrupt / completion queue 是另一层语义，不能与 PCIe completion 混同

这里必须明确区分两种 completion。PCIe 协议里的 completion 是“read request 在事务层得到了返回”；DMA 软件栈里的 completion 是“这笔数据移动对软件可见且可以推进状态机”。两者相关，但绝不是同一个概念。

如果要系统补齐这条链，建议回看：

- [PCIE: Posted / Non-Posted / Completion 与 Ordering](../../../PCIE/wiki/02-link-transaction-basics/posted-nonposted-completion-ordering.md)
- [PCIE: TLP、DLLP 与 Completion 语义](../../../PCIE/wiki/02-link-transaction-basics/tlp-dllp-completion-basics.md)
- [PCIE: PCIe Read Completion 延迟为什么敏感](../../../PCIE/wiki/04-data-path-dma-interrupts/pcie-read-completion-latency.md)
- [PCIE: 队列、Doorbell、Completion 与 MSI-X](../../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 为什么 PCIe DMA 的“完成”更像软件契约问题

AXI DMA 的很多完成语义仍然发生在片上硬件域里；PCIe DMA 则往往必须穿过 host memory、IOMMU、interrupt moderation 和 host software path。于是同样一笔“数据已经到了”的动作，在 PCIe 路径里还要再经过更多层，才能变成软件可见 completion。

这也是为什么 PCIe DMA 常常比 AXI DMA 更强调 queue pair、doorbell、completion queue、interrupt moderation。它面对的不是单一片上 fabric，而是一条更长、更分层的 host-device 契约链。

## 一个对照判断

AXI DMA 更像片上数据路径问题：重点是 `AR/AW/R/W`、burst、outstanding、片上仲裁和 memory return path。PCIe DMA 更像 host-device 协议问题：重点是 TLP 事务成本、posted/non-posted 区别、completion latency、IOMMU 和 host software 可见性。

两者都在做 DMA，但“慢”的原因和“完成”的定义都不同。把它们混成一类，通常会直接误导分析。

## 常见误解

常见误解：`AXI completion 和 PCIe completion 是同一个 completion`。实际上前者常指 DMA/总线层完成闭环，后者是 PCIe 事务层 read response 语义。

常见误解：`DMA 的 burst 行为和 AXI 通道没必要细看`。实际上 `AR/AW/R/W/B` 的组织正是 DMA 并发和尾延迟表现的底层原因。

常见误解：`PCIe DMA 慢主要是链路带宽不够`。实际上 read completion latency、IOMMU、host queue/interrupt 路径经常更早主导体验。

## 一句话理解

从 AXI 看 DMA，更像片上 master 如何组织 `AR/AW/R/W/B` 事务；从 PCIe 看 DMA，更像设备如何把 host-device 数据移动映射到 TLP、completion 和软件可见契约上。

## 建模启示

这一页适合把 AXI 和 PCIe 建成两种不同的 interaction profile，而不是一套统一“总线延迟”参数。

可以先用这样的抽象：

```text
DMAFabricProfile {
  fabric: axi | pcie
  req_form
  resp_form
  completion_semantics
  translation_cost
}
```

在 `05-system-integration`、`06-performance-modeling`、`07-workloads-case-studies` 三章里，这类 profile 很适合映射到 `Interaction` 与 `Capability` 抽象。若只关心粗粒度比较，可以把 AXI/PCIe 折叠成两套 latency/bandwidth 配置；若关心正确性与尾延迟，就必须保留 `resp_form` 和 `completion_semantics` 的区别。
