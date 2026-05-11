# AXI Narrow Transfer 与 WSTRB

上级：[03 片上总线协议族](./README.md)

相关：[AXI Burst、对齐与边界](./axi-burst-alignment-boundary.md)、[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)

## 这页在回答什么问题

为什么“总线很宽但只写几个字节”会让 AXI 实现和验证复杂很多。

## 什么是 narrow transfer

当一次传输的数据宽度小于总线物理宽度时，就会出现 narrow transfer。  
典型场景包括：

- 32-bit CPU 挂到 128-bit fabric
- MMIO 里大量小粒度更新

在 AXI 语境里，更精确地说，它首先对应的是：  
`AWSIZE / ARSIZE` 小于总线物理宽度，也就是“这次 beat 的传输大小本身就比总线窄”。

## WSTRB 在表达什么

`WSTRB` 用来告诉接收方：

- 当前 beat 里哪些 byte lane 有效
- 哪些 byte lane 不应该被写入

这让宽总线可以承接细粒度写操作，但也带来更多 corner case。

这和 narrow transfer 有关联，但不是一回事：

- `narrow transfer`：这次传输粒度本身就比总线窄
- `partial write with WSTRB`：总线宽度不变，但只写其中部分 byte lane

很多 `1 byte / 2 byte` 的寄存器更新，工程上常会同时牵涉这两件事，但读文档时最好把它们分开理解。

## 它为什么难

因为系统必须同时处理：

- 地址偏移
- byte lane 选择
- 与对齐规则的配合
- bridge 宽窄转换后的重组

如果某一层处理不严谨，就会出现：

- 写错 byte
- 把保留位误写掉
- MMIO 副作用范围扩大

## 在 MMIO 场景里尤其要小心

因为很多寄存器并不适合被“宽写再屏蔽”地对待。  
有些寄存器存在：

- write-1-to-clear
- read-to-clear
- bit field side effect

这时 narrow transfer 语义必须非常明确。

## 一句话理解

`WSTRB` 让 AXI 宽总线具备细粒度写能力，但也把很多实现风险集中到了 byte lane 选择和副作用控制上。
