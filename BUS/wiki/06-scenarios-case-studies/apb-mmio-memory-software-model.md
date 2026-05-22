# APB、MMIO 与普通内存的软件模型对照

上级：[06 典型系统与案例](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[AXI 属性、Cacheability 与 Barrier](../04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)、[APB Peripheral Subsystem 案例卡](./apb-peripheral-subsystem-case-card.md)、[AHB-Lite 与 APB 深入理解](../03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)

## 这页在回答什么问题

软件写下的都是 load/store，但普通内存、MMIO 和落在 APB 外设上的 MMIO 不属于同一种语义对象。普通内存面向数据存取和性能优化；MMIO 面向设备状态和副作用；APB 是 MMIO 的一种低速实现落点，会进一步引入 bridge、PREADY wait、PSLVERR 和低速外设状态。

这页用软件模型对照说明：为什么不能把寄存器当普通变量，不能把 APB 当“慢一点的内存”，也不能用 cache/barrier 规则替代设备协议。

## 三种对象的核心差异

| 对象 | 软件形式 | 系统语义 | 主要风险 |
| --- | --- | --- | --- |
| 普通内存 | load/store buffer | 数据存取，可 cache、可局部性优化 | cache coherence、重排、可见性 |
| MMIO | load/store register | 设备命令、状态、side effect | 顺序、副作用、barrier、访问粒度 |
| APB 外设访问 | load/store 到 MMIO 地址 | MMIO 语义落到 APB bridge/slave | PREADY wait、PSLVERR、timeout、低速路径长尾 |

普通内存是性能对象，MMIO 是设备语义对象，APB 是一种实现路径。三者混淆后，bug 会表现为旧数据、丢中断、读寄存器卡死或设备状态被调试访问改变。

## 普通内存：优化空间更大

普通内存访问受 ISA memory model、MMU/page attribute、cacheability、shareability 和 coherence 规则约束。它的目标是高效搬运数据。

| 特性 | 对软件的意义 | 边界 |
| --- | --- | --- |
| cache | 降低平均延迟 | DMA/non-coherent 场景需要 clean/invalidate |
| prefetch | 提升顺序访问性能 | 不应用到有 side effect 的设备寄存器 |
| write combine | 提升写吞吐 | 不能用于寄存器命令语义 |
| reorder | 提升执行效率 | 同步点、barrier 和 memory model 限制 |
| burst/locality | 提升 BUS/DDR 效率 | 不代表单笔 latency 稳定 |

普通内存的设计动机是允许系统优化访问顺序和数据路径。代价是软件必须明确同步和可见性，尤其在 CPU 与 DMA 共享 buffer 时。

## MMIO：访问就是设备事件

MMIO 使用地址访问形式，但它访问的是设备状态机。

| MMIO 类型 | 语义 | 风险 |
| --- | --- | --- |
| status register | 读取设备状态 | read-clear、latch、旧状态 |
| control register | 写入配置 | 顺序错误导致设备用旧配置 |
| command/doorbell | 写入触发动作 | descriptor/buffer 尚未可见 |
| interrupt clear | 写入清 pending | clear/EOI 顺序错误 |
| FIFO data register | read pop / write push | debug read 也会改变状态 |

MMIO 的设计动机是让软件用统一地址空间控制设备。代价是访问属性必须约束 cache、prefetch、merge 和 reorder。把 MMIO 标成普通 cacheable memory 会破坏设备协议。

## APB：MMIO 的低速实现落点

APB 是实现路径，不是新的软件内存类型。软件看到的仍是 MMIO，但访问会经过 bridge 和 APB setup/access 节拍。

| APB 特性 | 软件可见影响 |
| --- | --- |
| setup/access 两阶段 | 每次访问有固定节拍成本 |
| PREADY wait | 外设慢或未 ready 会拉长 load/store |
| PSLVERR | 错误要被 bridge 映射成上游 response |
| bridge slot | APB 长等待会占住上游转换资源 |
| low-speed clock/reset/power | 访问依赖外设 domain 状态 |

APB 的价值是低成本和易集成；风险是访问闭环更依赖低速外设状态。CPU 读 APB 寄存器卡住，不是“内存慢”，而是 device read 没有返回数据、错误或 timeout。

## 软件场景对照

| 软件代码意图 | 普通内存 | MMIO | APB 落点 |
| --- | --- | --- | --- |
| `x = *addr` | 读数据，可受 cache 影响 | 读设备状态，可能有副作用 | 还要等待 bridge/APB slave 完成 |
| `*addr = v` | 写数据，可能缓冲/合并 | 写命令或配置，顺序敏感 | PREADY/PSLVERR 决定闭环 |
| polling | 可能读 cache 中数据 | 反复读设备状态 | 可能堵住 APB bridge |
| debug read | 观察内存内容 | 可能触发 read side effect | 可能改变外设状态或造成 timeout |
| barrier | 约束顺序 | 保证配置/start/clear 顺序 | 不能替代 PREADY/timeout/error |

这个表说明，同一条 load/store 指令在不同地址属性和路径上，含义完全不同。

## 例子：Doorbell 前的 Descriptor

| 阶段 | 普通内存语义 | MMIO/APB 语义 |
| --- | --- | --- |
| T0 | CPU 写 descriptor memory | 只是普通数据写 |
| T1 | cache clean / barrier | 建立 DMA 可见性和顺序 |
| T2 | CPU 写 doorbell register | MMIO write，触发设备动作 |
| T3 | APB bridge 完成 access | doorbell 才真正到达低速设备 |
| T4 | DMA 读取 descriptor | 依赖 T1 的可见性 |

barrier 约束 T1 到 T2 的顺序，APB PREADY 决定 T2 到 T3 的完成。二者解决的问题不同。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| MMIO 是慢一点的 memory | MMIO 是设备状态机接口，读写可能有副作用 |
| APB 是一种软件内存类型 | APB 是 MMIO 的实现路径，软件语义仍由 device 属性定义 |
| barrier 能修复所有可见性问题 | barrier 约束顺序，cache maintenance/coherence 才建立数据可见性 |
| debug read 不会改变系统 | 读 status/FIFO/read-clear 寄存器可能改变设备状态 |
| polling 只是多读几次 | APB polling 会占用 bridge 和低速控制路径 |

## 一句话理解

普通内存关注高效访问数据，MMIO 关注按设备语义访问状态，APB 则把这种 MMIO 语义落到低成本但更慢的总线路径上。

## 建模启示

这个对照要把软件地址访问拆成 Resource、Topology、Interaction、Capability。普通内存的 Resource 是 cache line、memory controller 和 coherence state；MMIO 的 Resource 是寄存器、side effect 和设备状态机；APB 的 Resource 还包括 bridge slot、PREADY/PSLVERR 和低速 clock/reset domain。Topology 决定访问是否经过 bridge/APB；Interaction 决定 load/store 是数据访问、设备命令还是 APB access；Capability 决定 cacheability、ordering、timeout、error 和 debug 可见性。

事件模型建议显式表达 `memory_load_store`、`cache_clean_done`、`mmio_read_side_effect`、`mmio_write_command`、`apb_setup`、`apb_access_done`、`pslverr_seen`、`polling_loop_wait`。这些事件能防止模型把普通数据访问、设备状态访问和 APB 低速闭环混成同一种 load/store。
