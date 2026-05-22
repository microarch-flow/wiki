# AHB-Lite 与 APB 深化

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)、[分层总线与协议分工](./hierarchical-bus-and-protocol-roles.md)、[Boot Path 与地址映射初始化](../04-microarchitecture-integration/boot-path-address-map-initialization.md)、[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)

## 这页在回答什么问题

AHB-Lite 和 APB 为什么不是“落后协议”，而是在 MCU、boot path、外设寄存器子树和低复杂度 SoC 里承担明确的复杂度边界。

## AHB-Lite 的价值是低状态流水

AHB-Lite 的核心定位是单 master 或已完成上游仲裁后的子系统访问。它保留 AHB 的地址/data phase 流水思想，但去掉多 master 总线仲裁相关复杂度，让本地 SRAM、ROM、简单 DMA、外设子系统和 MCU 主干可以用较小状态机实现。

AHB-Lite 访问可以粗略理解成两个 phase：

| Phase | 主要信息 | 作用 |
|---|---|---|
| Address/control phase | `HADDR`、`HTRANS`、`HWRITE`、`HSIZE`、`HBURST` 等 | 描述下一次 transfer |
| Data/response phase | `HWDATA` 或 `HRDATA`、`HREADY`、`HRESP` | 传输数据并反馈完成状态 |

这个流水关系让一个 transfer 的数据阶段和下一个 transfer 的地址阶段可以重叠。与 APB 相比，它能减少连续访问中的空窗；与 AXI 相比，它没有五通道、ID、多 outstanding 和复杂返回匹配，因此状态空间更小。

容易误解：AHB-Lite 只是 AXI 的弱化版。实际上，它是在“需要一定流水，但不需要 AXI 式高并发”的路径上，用更少状态换取可预测实现。

## HREADY/HRESP 是 AHB-Lite 的节流和闭合边界

AHB-Lite 的等待和完成主要通过 `HREADY` 与 `HRESP` 表达。`HREADY` 低表示当前 transfer 尚未完成，地址/data 流水被拉住；`HRESP` 表示响应状态。这样 slave 可以插入 wait state，慢 SRAM、ROM、外设桥或低速子系统不必在固定一拍内完成。

一个构造的 read transfer：

| Cycle | Address/control | Data/response | 状态 |
|---:|---|---|---|
| 0 | 发出 `HADDR=A0` | 上一笔 data phase | read 请求进入地址阶段 |
| 1 | 下一笔地址可准备 | `HREADY=0` | slave 未完成，流水停住 |
| 2 | 保持或等待 | `HREADY=1, HRDATA=D0` | read data 有效，transfer 闭合 |
| 3 | 发出下一笔有效地址 | - | 流水继续 |

这张表说明 AHB-Lite 比阻塞寄存器总线更有流水能力，但它的 stall 会直接拉住后续 transfer。没有 AXI 那种独立 `AR/R` 或 `AW/W/B` channel，慢访问更容易把后续访问串起来。

容易误解：AHB-Lite 简单就代表没有 backpressure。实际上，`HREADY` 就是节流边界；它更集中、更容易推理，但同样会影响尾延迟。

## APB 的价值是把外设访问压成两阶段

APB 的定位是低复杂度外设寄存器访问，不是高性能数据搬运。它把访问压成 setup phase 和 access phase：setup 阶段选择外设并给出地址、方向和写数据；access 阶段拉起 `PENABLE`，等待 `PREADY` 表示完成，必要时用 `PSLVERR` 表示错误。

APB 的典型信号语义可以这样看：

| 信号 | 作用 |
|---|---|
| `PSEL` | 选中目标 peripheral |
| `PENABLE` | 进入 access phase |
| `PADDR/PWRITE/PWDATA` | 地址、方向、写数据 |
| `PRDATA` | 读数据 |
| `PREADY` | peripheral 完成当前访问 |
| `PSLVERR` | peripheral 返回错误状态 |

APB 的交易是把并发能力降到最低，换取外设端小面积、低功耗、低验证成本和清楚的软件可见语义。UART、GPIO、timer、watchdog、clock/reset controller、status register、interrupt controller 配置窗口都适合这种模型。

容易误解：APB 只是慢。实际上，APB 是把低速控制面从复杂主干里隔离出来，让寄存器访问以更简单的 phase 和错误语义闭合。

## APB 不适合承载数据面

APB 不适合高吞吐数据面，不是因为它“旧”，而是因为它刻意不承担这些能力：长 burst、多 outstanding、独立读写返回、高并发 master、复杂 ordering 和宽数据重组。把大块 memory copy、frame buffer、NPU tensor 搬运或 DDR 主路径压到 APB 上，会把每次访问都变成低并发寄存器式交付，吞吐和延迟都会被固定开销吞掉。

这不表示 APB 子树里不能有 FIFO 或数据寄存器。外设可以暴露 data register，让软件或 DMA 通过 APB 读写少量数据；但一旦需求变成持续流量，系统就应该考虑 AHB/AXI、专用 DMA 数据口或 point-to-point streaming path，而不是继续扩大 APB 访问压力。

容易误解：统一用 APB 可以让系统更简单。实际上，APB 让外设端简单；若把主干数据面也压成 APB，复杂度会转移到软件等待、吞吐瓶颈和 timeout 调试上。

## AHB-Lite 适合 MCU 和局部子系统

AHB-Lite 的位置在 APB 和 AXI 之间。它能支撑 instruction fetch、SRAM/ROM 访问、简单 DMA、本地 peripheral bridge 和 MCU 级主干；同时避免 AXI 的 ID、outstanding 和多通道关联状态。对 boot path，AHB-Lite 也很有吸引力：上电早期需要的是少量路径稳定可达，而不是高并发 fabric 全部打开。

一个构造分层可以这样写：

| 层级 | 协议 | 设计理由 |
|---|---|---|
| CPU/MCU 到 SRAM/ROM | AHB-Lite | 低状态流水，适合取指和本地访问 |
| AHB-Lite 到外设子树 | AHB-to-APB bridge | 把主干访问收束成简单寄存器访问 |
| UART/GPIO/timer | APB | 外设端接口小，访问语义清楚 |
| 高性能 DMA/DDR | AXI 或其他高并发路径 | 需要 burst/outstanding 隐藏长延迟 |

这个分层不是固定模板，而是复杂度匹配。AHB-Lite 负责需要一定吞吐但并发压力有限的路径，APB 负责低速控制面，AXI 留给高并发数据面。

## Bridge 是语义边界

AHB-to-APB bridge 或 AXI-to-APB bridge 不只是换信号名。它要把上游的地址、写数据、读请求、错误和等待语义，转换成 APB 的 setup/access 流程。bridge 会引入固定延迟，也会成为 backpressure、ordering 和错误映射的边界。

例如，上游 AHB-Lite 一次 read transfer 到 APB 外设，bridge 需要先锁存地址和控制信息，再发起 APB setup/access，等 `PREADY` 后返回 `HRDATA` 并拉高 `HREADY`。若 APB 外设一直不 ready，AHB-Lite 主干会被 `HREADY=0` 拉住；若外设返回 `PSLVERR`，bridge 需要把它映射成上游能理解的 response。

建模 bridge 时，不应该把它当成零成本连线。它至少会影响 latency、错误类别、低速外设对主干的反压方式，以及 boot/debug 阶段哪些路径已经可用。

## 一句话理解

AHB-Lite 和 APB 的价值不是追求最高并发，而是把 MCU 主干、boot path 和外设寄存器访问控制在更小、更稳、更容易验证的事务复杂度内。

## 建模启示

AHB-Lite 模型要保留 address/data phase 流水、`HREADY` stall、`HRESP` response、transfer size、burst 或连续访问信息。它不需要 AXI 式五通道和 ID matching，但不能被简化成固定一拍访问；慢 slave 或 bridge 会用 `HREADY=0` 直接拉长后续访问。

APB 模型要保留 setup/access 两阶段、`PREADY` wait state、`PSLVERR`、外设服务时间和寄存器副作用。对 control/status register，payload 很小但语义很重；模型要关心访问是否完成、是否报错、是否触发副作用，而不是只统计 byte 数。

Bridge 模型要记录上下游协议的节奏转换：AHB/AXI request 何时被 bridge 接收，APB 访问何时开始，`PREADY` 何时返回，上游 response 何时释放。忽略 bridge 会低估 boot path 延迟、外设 timeout 风险和低速 peripheral 对主干的 backpressure。

选择 AHB-Lite 或 APB 的建模问题不是“协议是否高性能”，而是“这条路径是否需要 AXI 那些并发状态”。如果答案是否定的，低复杂度协议能让模型和硬件都更清楚；如果答案是肯定的，把低复杂度协议推到数据面只会制造瓶颈。
