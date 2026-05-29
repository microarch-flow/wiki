# 03 片上总线协议族

上级：[BUS Wiki](../README.md)

相关：[02 基础对象与事务语义](../02-fundamentals/README.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)、[AXI 与 DMA 的系统接口](../04-microarchitecture-integration/axi-dma-system-interface.md)

## 这一章在回答什么问题

02 章讲的是交通系统的基本原理——什么是路网、什么是出行、什么是交通规则。03 章要回答的是：市面上具体有哪几种交通系统（AXI、AHB-Lite、APB、TileLink），它们各自的设计哲学是什么，为什么不同的路段会选择不同的系统。

本章不是把每种协议的信号表逐条翻译，而是把协议当成**设计选择题**：它支持多少并发，如何拆分事务，如何返回 completion，如何处理 burst、byte lane、错误和 cache 可见性，以及这些能力要付出多少实现和验证成本。就像选车不是比谁更贵，而是看你的路况、载客量和预算。

## 本章阅读顺序

1. [AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)
2. [AXI Channel、ID 与 Outstanding](./axi-channel-id-outstanding.md)
3. [AXI 五通道与 VALID/READY](./axi-five-channels-handshake.md)
4. [AXI Burst、对齐与边界](./axi-burst-alignment-boundary.md)
5. [AXI Narrow Transfer 与 WSTRB](./axi-narrow-transfer-wstrb.md)
6. [AXI Response 与错误路径](./axi-response-error-path.md)
7. [AHB-Lite 与 APB 深化](./ahb-lite-and-apb-deep-dive.md)
8. [分层总线与协议分工](./hierarchical-bus-and-protocol-roles.md)
9. [Coherent Bus vs Non-Coherent Bus](./coherent-bus-vs-noncoherent-bus.md)
10. [TileLink 概览](./tilelink-overview.md)

这个顺序先建立协议复杂度坐标，再深入 AXI 的 channel、ID、burst、WSTRB 和 response，随后回到低复杂度协议、分层组织、一致性边界和 TileLink 这类参数化框架。

## 本章核心判断

APB、AHB-Lite 和 AXI 的差异，不是”经济舱、商务舱、头等舱”的等级差异，而是**拆解动作的精细程度不同**——就像路边摊老板一个人搞定点单做菜上菜，快餐店把点单和取餐分开，大餐厅把预订、点菜、厨房、上菜、结账全部独立成不同工位。APB 把寄存器访问压成低复杂度流程；AHB-Lite 用 address/data phase 流水支撑 MCU 和局部子系统；AXI 用五通道、ID、outstanding、burst 和 response matching 支撑高并发路径。

AXI 的强大来自解耦，也复杂在解耦。`VALID && READY` 只说明当前 channel 当前 beat 完成交付，不等于整笔 transaction 闭合。写事务要靠 `AW/W/B` 重新闭合，读事务要靠 `AR/R` 和 last beat 闭合；ID 和 outstanding 让多个事务同时在飞，也要求实现维护匹配和释放状态。

Burst、narrow transfer、WSTRB 和 response error 都不是格式细节。Burst 决定地址生成和边界约束，WSTRB 决定写 lane 有效性，response 决定 completion 和错误闭合。忽略这些细节，性能模型会丢掉真实占路和回压，功能模型会漏掉 byte lane、跨界、错误和副作用问题。

Coherent 和 non-coherent 的分界在共享内存可见性。Non-coherent 路径负责事务搬运，cache 可见性由软件或上层机制闭合；coherent 路径还要维护 cache-line ownership、副本失效和共享视图。MMIO/device 路径又是另一类语义，不能和普通 cacheable memory 混成一类。

TileLink 的价值在参数化事务框架，而不是替代所有总线。它把简单访问、高能力 uncached 访问和 coherent 访问放进同一套生成式 SoC 生态中；建模时要看节点能力、source/sink、manager/client、ordering 和 coherence 范围。

## 和后续章节的关系

04 章会把这些协议能力落到真实结构里：decoder、arbiter、crossbar、bridge、CDC、width adapter、IOMMU/SMMU、DDR controller 和 DMA interface。读 04 章时，要持续追问每个组件改变了哪类协议语义：地址、数据、response、ordering、属性、error 还是 backpressure。

05 章会把这些协议语义转成调试口径。AXI waveform debug、timeout/fault/hang、counters/trace、QoS 和拥塞分析，都离不开本章定义的 channel、ID、burst、response 和 coherence 边界。

06 章会用案例检验协议选型。MCU、SoC、AI 芯片、AXI crossbar、APB peripheral subsystem、DMA completion 丢失和 IOMMU fault，本质上都是在不同系统压力下选择和组合这些协议能力。

## 一句话总纲

选片上 BUS 协议时，最重要的不是“谁更新”或“谁更快”，而是事务能力、复杂度、软件语义、系统规模和验证成本是否匹配。

## 建模启示

03 章给模型提供协议能力参数。性能模型至少要记录：协议层级、channel/phase 拆分、最大 outstanding、ID/source 匹配、burst 规则、byte lane/WSTRB、response path、bridge 转换和 coherence 范围。功能模型还要保留错误映射、ordering 规则、属性传播、cacheability/shareability、MMIO 副作用和 completion 释放条件。

不要用协议名直接推导行为。AXI 路径可能因为 slave slot、bridge FIFO、response path 或强保序而表现很慢；APB 路径可能在 boot/debug 中是最稳的选择；TileLink 节点是否 coherent 取决于能力参数和系统配置；coherent path 也不替代软件同步。

读完本章后，应该能把一个协议接口转换成建模问题：这条路径拆成哪些 phase/channel，事务在飞上限是多少，response 如何匹配和释放，错误如何返回，byte lane 如何落到目标，cache 可见性由谁维护。
