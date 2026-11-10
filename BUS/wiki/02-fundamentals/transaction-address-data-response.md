# 地址、数据、响应与事务语义

上级：[02 基础对象与事务语义](./README.md)

相关：[AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)、[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)、[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)

## 这页在回答什么问题

一次 BUS transaction 为什么需要分别描述地址、控制属性、数据和响应，以及这些信息如何在时间上关联。

## Transaction 是一段生命周期

Transaction 是发起方请求一次访问，到协议规定的响应被接收为止的过程。一次事务可能包含多个握手、多个 data beat，或由 bridge 拆成多个内部子访问。各阶段的资源和等待条件不同。

| 信息 | 输入与作用 | 例子 |
| --- | --- | --- |
| 地址 | 选择目标或地址范围，供 decode 和路由使用 | `ARADDR` 选择 SRAM 地址 |
| 控制属性 | 规定访问大小、长度、权限及其他处理规则 | `ARLEN`、`ARSIZE`、`ARPROT` |
| 数据 | 搬运有效载荷；写由 master 发出，读由 slave 返回 | `WDATA/WSTRB`、`RDATA` |
| 响应 | 标识协议完成状态并关联请求 | `BRESP`、`RRESP`、ID |

## 地址语义必须先于路由和提交被确定

互连根据地址和属性选择目标、检查权限及边界，并建立返回上下文。AXI 的 `AW` 和 `W` 可以独立到达：若 `W` 先握手，接收端可暂存数据；在向正确目标路由或提交之前，仍要取得与该数据对应的地址上下文。

一个 burst 用起始地址、长度和大小规则生成后续 beat 地址。合法性包括协议和目标约束；详见 [AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)。

## 控制属性描述的是处理规则

地址决定访问哪里；属性决定如何处理。例如 `AxPROT` 影响权限检查，`AxQOS` 可供实现的仲裁策略使用，`AxLEN/AxSIZE/AxBURST` 决定 burst 的长度、粒度和地址序列。cacheability 和缓冲属性的效果还取决于系统映射和接收端实现；设置 QoS 字段本身也不保证带宽。

属性与地址可在同一地址通道传输，但不能把它们视为同一语义。建模时需要保留会改变路径、权限、服务顺序或有效数据粒度的属性。

## 数据的节奏天然不同于地址

AXI 写事务的 `AW`、`W` 和 `B` 可独立握手，但它们属于同一事务。读事务的 `AR` 由 master 发往 slave；slave 在 `R` 通道向 master 返回数据和状态。读写方向与响应方向必须分别记录。

以下构造例使用 AXI4 四拍写 burst，且 AW 先于 W。每行表示一个采样沿；该顺序不是协议要求。cycle 3 假设 master 已提出 beat 2，但接收端暂不能接收，master 在握手前保持该 beat 稳定。

| Cycle | AW 地址/属性 | W 数据 | B 响应 | 事务状态 |
|---:|---|---|---|---|
| 0 | `AWVALID && AWREADY` | - | - | 地址上下文被接收 |
| 1 | - | beat 0 fire | - | 第一拍数据被接收 |
| 2 | - | beat 1 fire | - | 第二拍被接收 |
| 3 | - | beat 2：`WVALID=1, WREADY=0` | - | 等待并保持 payload |
| 4 | - | beat 2 fire | - | 回压解除 |
| 5 | - | beat 3 fire，`WLAST=1` | - | 全部写数据被接收 |
| 6 | - | - | `BVALID && BREADY` | 写响应被消费，接口事务闭合 |

例如一次两拍读可以在 cycle 0 接收 AR，在 cycle 4、5 分别以 `RVALID && RREADY` 接收两拍；第二拍携 `RLAST`。若第二拍被反压，数据、状态和 `RLAST` 保持稳定，直到握手。收到首拍不代表完整 burst 已完成。

## 响应是事务闭环的证据

AXI 写响应在独立的 B 通道返回。AXI 读状态 `RRESP` 随 `RDATA` 一起在 R 通道返回。即使返回了数据，也要检查响应状态；错误 beat 不允许提前截断已接受的 burst。B fire 或最后 R beat fire 才可按接口契约回收对应事务状态。

多笔在途请求需要关联响应。AXI 的同一 ID 可有多笔按序事务，不能把 ID 当成唯一事务序号；不同 ID 的响应在协议允许时可乱序。详见 [AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md) 和 [AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)。协议响应不等同 DMA 任务的软件 completion，也不自动证明非一致缓存已同步。

## 分裂程度就是协议复杂度的度量

| 接口 | 阶段和并发 | 代价与适用条件 |
| --- | --- | --- |
| APB | setup 后 access，可等待目标完成 | 状态较少，适合低速寄存器访问 |
| AHB-Lite | 地址和数据阶段可流水 | 流水受 `HREADY` 等待传播影响 |
| AXI | AW/W/B/AR/R 分开握手，可有多笔 outstanding | 需管理数据关联、ID、排序、缓存和回压 |

独立握手不等于互不阻塞。共享缓冲、返回队列和跨通道依赖可能把一处堵塞传播到其他通道。

## 拆分是在换取流水与可诊断性

多笔事务在途可以隐藏目标服务延迟，但需要足够的请求槽、返回缓冲和正确匹配。对简单、低流量寄存器路径，额外状态可能没有收益；对 DMA 与内存之间的高吞吐路径，并发和 burst 可能提高资源利用率。具体收益需要按目标服务速率和负载测量。

## 一句话理解

地址选目标，属性规定处理规则，数据承载 payload，响应闭合协议事务；它们可以在不同时刻传输，但必须按协议重新关联。

## 建模启示

模型应分别记录地址接受、每个数据 beat、响应生成和响应消费。写事务允许 AW/W 先后不同；读事务以最后 R beat 的握手作为接口完成。对 burst 保留 beat index、last 和 byte strobe；对多笔在途保留 ID、同 ID 请求顺序及资源释放点。

性能模型还要保留各通道队列、仲裁、有限 outstanding 和返回回压。功能模型要检查 decode、权限、边界、有效 byte 与错误响应。若只统计一个固定延迟事件，就无法解释哪一段等待或哪个状态未被释放。
