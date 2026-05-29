# APB Peripheral Subsystem 案例卡

上级：[06 典型系统与案例](./README.md)

相关：[AHB-Lite 与 APB 深入理解](../03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[CPU 读 MMIO 卡死案例卡](./cpu-mmio-read-hang-case-card.md)

## 这页在回答什么问题

APB peripheral subsystem 就像大楼里的**物业管理柜台**——不需要多快（不是高吞吐），但要稳定、可靠、出了事能说清楚。UART、SPI、GPIO、timer、watchdog 这些外设就像门禁卡系统、空调控制、消防报警器，它们不需要 AXI 的高速多车道能力，但需要清晰地址映射、稳定的操作语义和出错时的明确反馈。

这个案例卡关注：什么时候 APB 子系统是合适选择，bridge 如何改变上游 transaction，低速外设如何影响软件可见 latency，以及中断/status/clear 寄存器为什么要特别小心。

## 典型结构

```text
CPU / debug / DMA control master
  -> high-performance interconnect
  -> AXI/AHB-to-APB bridge
  -> APB decoder
  -> UART / SPI / I2C / GPIO / timer / watchdog / interrupt block
```

| 组件 | 责任 | 风险 |
| --- | --- | --- |
| high-performance interconnect | 承接 CPU/debug/control master | 控制访问与数据流争用 |
| bridge | 把上游协议压缩成 APB setup/access | outstanding 收缩、timeout、错误映射 |
| APB decoder | 选择外设寄存器块 | decode miss 和 default slave |
| APB slave | 执行寄存器读写 | PREADY stall、PSLVERR、side effect |
| interrupt/status block | 暴露事件和清除路径 | clear/read side effect、软件长尾 |

APB 子系统的设计动机是把低速控制资源从高性能主干中分离出来。代价是 bridge 成为语义收缩点：上游 burst/outstanding/ID 能力会被压成单笔 APB access。

## APB 节拍与 Bridge 收缩

APB access 至少有 setup 和 access 两个阶段。PREADY 可以拉长 access phase，PSLVERR 在完成时返回错误。

| 阶段 | APB 信号语义 | 上游可见结果 |
| --- | --- | --- |
| setup | PSEL=1, PENABLE=0 | bridge 已选择目标，但访问未完成 |
| access wait | PSEL=1, PENABLE=1, PREADY=0 | 上游 request 或 bridge slot 被占用 |
| access done | PREADY=1 | 读数据/写完成可返回上游 |
| error done | PREADY=1, PSLVERR=1 | bridge 映射成上游 error response |

这说明 APB 子系统不是零成本低速尾巴。一个 PREADY 长等待会占住 bridge slot；若 bridge 前没有足够隔离，低速 APB access 会反压上游控制路径。

## 适合挂 APB 的资源

| 资源 | 适合原因 | 注意点 |
| --- | --- | --- |
| GPIO / pinmux | 寄存器控制为主 | 写顺序和 side effect |
| UART / SPI / I2C control | 低频配置和状态读取 | FIFO data register 可能有 read side effect |
| timer / watchdog | 控制寄存器少，延迟可接受 | clear/enable 顺序关键 |
| clock/reset controller | 控制语义强 | 访问时目标 domain 状态要定义 |
| interrupt controller low-speed view | pending/mask/clear 寄存器 | read/clear 语义要清楚 |

不适合把高吞吐数据搬运路径硬压到 APB。大量 polling、FIFO 数据搬运或高频 status read 会让 APB bridge 变成控制路径瓶颈。

## 软件交互风险

APB 访问大多是 MMIO，因此软件语义比吞吐更重要。

| 软件动作 | BUS 风险 | 设计要求 |
| --- | --- | --- |
| polling status | 大量 APB read 占住 bridge | 限制 polling 频率或提供 interrupt |
| clear interrupt | write-one-to-clear 或 read-clear 语义 | WSTRB、写值、顺序要定义 |
| read FIFO data | read 可能 pop 数据 | 禁止无意 debug read 或 speculative read |
| write command | 写入触发硬件动作 | 与配置寄存器顺序要受控 |
| debug read status | 取证可能改变状态 | 提供 shadow/snapshot 或只读 alias |

APB 简化了硬件接口，但没有简化软件契约。寄存器 side effect、interrupt clear、status latch 和 timeout/error 返回仍要建模。

## 例子：Timer Interrupt Clear

| 阶段 | 事件 | APB/BUS 关注点 |
| --- | --- | --- |
| T0 | timer 产生 interrupt pending | pending bit 对 CPU 可见 |
| T1 | CPU ISR 读 status | APB read 是否有 clear-on-read |
| T2 | CPU 写 clear register | PREADY wait 会延迟 clear 到达 |
| T3 | APB slave 完成 clear | PSLVERR/OKAY 决定软件是否认为成功 |
| T4 | interrupt controller 取消 pending | clear 与 EOI 顺序要匹配 |

若 T2 被 APB bridge 堵住，CPU 可能退出 ISR 前中断仍 pending；若 status read 本身清 pending，debugger 读取也可能改变现场。这个例子说明 APB 低速路径会影响 interrupt 行为。

## 观测点

| 观测点 | 要记录 |
| --- | --- |
| bridge input | upstream request accept、backpressure、slot occupancy |
| APB phase | setup count、access wait cycles、PREADY low cycles |
| APB error | PSLVERR、decode miss、timeout |
| per-slave access | 每个外设 read/write count、max wait |
| side-effect register | status read、clear write、command write |
| software-visible path | interrupt pending、clear done、polling latency |

这些观测点可以回答：是 CPU 没发出 MMIO，bridge 没接收，APB slave 不 ready，还是 clear/status 已经完成但 interrupt controller 没同步。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| APB 慢一点没关系 | APB 卡住会影响 driver 配置、polling、interrupt clear |
| APB 子系统没有性能问题 | bridge slot、PREADY wait 和 polling 会形成控制路径拥塞 |
| MMIO read 都是无害观察 | status/FIFO/read-clear 寄存器可能有 side effect |
| 上游 AXI 支持 outstanding 就能隐藏 APB 慢 | bridge 会把并发窗口收缩到很浅 |

## 一句话理解

APB 子系统用低 Resource 和简单 Topology 承接低速控制 Interaction，但 Capability 边界必须覆盖错误返回、side effect、interrupt/status 和可观测性。

## 建模启示

APB peripheral subsystem 要建模成 bridge 收缩点加低速 MMIO 事务集合。性能模型要记录 bridge slot、APB setup/access、PREADY wait、per-slave latency、polling rate 和 interrupt clear latency。功能模型要记录 address decode、PSLVERR、timeout、WSTRB、read/write side effect、status/clear 语义和 debug access。

事件模型建议显式表达 `bridge_accept`、`apb_setup`、`apb_access_wait`、`apb_access_done`、`pslverr_seen`、`mmio_side_effect`、`interrupt_clear_done`。这些事件能解释 APB 子系统为什么低成本可行，也能定位它何时把控制路径拖成长尾或 hang。
