# Boot Path 与地址映射初始化

上级：[04 微架构与系统集成](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[互连组件与数据路径分解](./interconnect-components.md)、[AXI 属性、Cacheability 与 Barrier](./axi-attributes-cacheability-barrier.md)、[CPU、DMA、外设与内存之间的总线路径](./dma-cpu-peripheral-memory-path.md)

## 这页在回答什么问题

芯片上电后，BUS fabric 不是一次性进入最终运行态。CPU 能取到第一条指令，只代表一条最小路径可用：reset vector、boot ROM、少量 always-on 寄存器和必要的错误返回路径。SRAM、DRAM、外设、DMA、中断和高性能互连要靠固件逐步打开。

boot path 的核心问题是：在每个启动阶段，哪些地址能访问，访问会经过哪条路径，失败时返回错误还是 hang。地址映射初始化不是软件表格问题，而是把硬件电源、时钟、复位、隔离、decoder window 和访问属性按正确顺序拉起来。

## 启动早期只有最小可用互连

启动最早期的 BUS 目标是让 CPU 从 reset vector 走到第一段可信固件。这个阶段追求确定性，不追求完整性能。

| 资源 | 启动早期责任 | 设计取舍 |
| --- | --- | --- |
| boot ROM | 提供 reset vector 和最小固件 | 固定映射可靠，但容量小、不可更新 |
| always-on register | 暴露 strap、fuse、clock/reset 控制 | 路径要跨 power/reset 边界，设计必须保守 |
| minimal decoder | 把少量地址映射到 ROM 和控制寄存器 | 简单稳定，但覆盖范围有限 |
| default error path | 对非法访问返回可诊断错误 | 需要避免未上电 slave 导致永久等待 |
| debug entry | 在 CPU 或固件失败时提供观察入口 | 可达性和安全隔离要同时满足 |

这个阶段的互连不等于运行态互连的缩小版。某些 crossbar、DDR controller、DMA、外设 bridge 还没出 reset；某些地址窗口可能暂时指向 ROM，后面才 remap 到 SRAM 或 DRAM。

## 地址映射会随阶段变化

boot 过程中的地址映射有两个层次：硬件 reset 默认映射，以及固件初始化后的运行态映射。模型要区分“地址存在于最终 map”与“当前阶段可访问”。

| 阶段 | 可访问路径 | 关键动作 | 风险 |
| --- | --- | --- | --- |
| reset release | CPU -> boot ROM | 从 reset vector 取指 | ROM path 时钟/复位错误会导致无取指 |
| early ROM | CPU -> ROM / always-on MMIO | 读 strap/fuse，配置初始 clock | MMIO window 错误会返回 decode/slave error |
| SRAM enable | CPU -> SRAM | 打开 SRAM power/clock，释放 reset | SRAM 未 ready 时访问可能 timeout |
| remap | reset vector 或低地址从 ROM 切到 SRAM/DRAM | 修改 decoder/remap register | 指令流和 data access 需要避开切换窗口 |
| DRAM init | CPU -> DDR controller -> DRAM | 训练、校准、设置时序 | DRAM 可寻址不代表数据稳定 |
| runtime map | CPU/DMA/debug/peripheral paths | 打开中断、DMA、cache 属性 | 属性错误会破坏 MMIO 或 cache 可见性 |

地址映射初始化的设计动机是让同一个 SoC 可以从 ROM、flash、SRAM 或 debug boot 等入口进入系统。代价是启动阶段形成了多个临时语义：同一地址在不同阶段可能指向不同目标；同一外设在 power-on、reset、clock enabled、configured 四个状态下的访问结果不同。

## Remap 不是简单改一张表

remap 会改变地址到路径的绑定。若 CPU 正在执行低地址代码，同时固件把低地址从 ROM 切到 SRAM，就要保证切换前后的指令流、异常向量和 data access 都有定义。

| remap 设计 | 收益 | 风险 |
| --- | --- | --- |
| 固定 ROM at reset，运行态切到 SRAM | boot 稳定，运行态可更新 vector/code | 切换时需要保证 CPU 不再依赖旧窗口 |
| ROM mirror 到多个地址 | 降低 reset vector 配置复杂度 | alias 可能让调试和权限配置混乱 |
| per-master remap | CPU、debug、DMA 可有不同视图 | 一致性和安全策略更复杂 |
| lockable remap register | boot 后防止恶意修改 | lock 时机错误会阻断合法固件流程 |

remap 模型要记录生效时刻。写 remap register 的 MMIO transaction 完成，不一定等于后续 fetch 已经使用新映射；需要考虑 store buffer、barrier、pipeline、I-cache 和异常向量更新。启动代码常需要在 remap 后执行跳转、刷新或同步操作，本质上是在让软件控制流和 BUS 地址视图重新对齐。

## Clock、Reset、Power 与 Isolation

一类高风险 boot hang 来自“地址 decode 成功，但目标还不能服务”。BUS 路径上的 slave、bridge、clock domain、power domain 和 isolation cell 都可能决定访问结果。

| 状态 | 对 BUS 访问的影响 | 建模方式 |
| --- | --- | --- |
| clock disabled | 目标无法推进握手 | 返回 timeout、保持 backpressure，或禁止访问 |
| reset asserted | 目标寄存器状态不可用 | 访问 default value、error，或不接收事务 |
| power off | 信号需要 isolation | 访问应被互连拦截或由 power controller 约束 |
| isolation enabled | transaction 不应穿过边界 | 记录 isolation release 事件 |
| calibration pending | DDR/PHY 未完成训练 | 地址已 decode，但 data path 不可用 |

设计取舍在于错误可诊断性和硬件成本。给每个未 ready 目标返回明确错误，需要 default slave、timeout 或 ready-status 机制；直接让访问等待，硬件简单但会把 CPU 卡死在一次 load 上。boot 代码的可恢复性取决于硬件选择了哪种行为。

## 例子：从 ROM 到 DRAM 的启动路径

下面的阶段表展示一次典型启动链如何逐步扩大 BUS 可访问范围。

| 阶段 | 事件 | 可访问路径 | 不应访问 |
| --- | --- | --- | --- |
| T0 | reset deassert | CPU fetch -> ROM | DDR、DMA、高速外设 |
| T1 | ROM 读取 strap/fuse | CPU -> always-on MMIO | 未供电外设 |
| T2 | ROM 打开 SRAM clock/reset | CPU -> clock/reset controller | 仍未 ready 的 SRAM data window |
| T3 | SRAM ready | CPU -> SRAM | DDR memory window |
| T4 | 初始化 DDR controller/PHY | CPU -> DDR controller MMIO | 普通 DDR data access |
| T5 | DDR training done | CPU -> DDR memory | 属性未配置的 DMA/coherent path |
| T6 | 配置 cache/MMU/interrupt/DMA | CPU -> system MMIO + memory | 未授权 debug/DMA window |

这个表的建模重点不是固定周期数，而是阶段条件。`sram_ready`、`ddr_training_done`、`remap_active`、`cache_attr_valid` 这些状态决定同一个地址访问是成功、错误、等待还是产生未定义软件后果。

## 错误路径比成功路径更重要

boot 阶段最危险的失败不是返回错误，而是没有返回。一次 CPU load 卡在未响应的 slave 上，可能让系统失去继续初始化和输出日志的机会。

| 访问结果 | 含义 | 对 boot 的影响 |
| --- | --- | --- |
| decode error | 地址窗口不存在或尚未打开 | 固件可通过异常或状态定位问题 |
| slave error | 目标存在但拒绝访问 | 可诊断，适合未配置或权限错误 |
| timeout error | 目标未响应但 timeout 逻辑介入 | 可恢复性取决于异常处理是否已就绪 |
| permanent stall | 没有错误也没有完成 | CPU 可能无法进入异常处理 |

因此，boot path 模型要显式写出 default slave、timeout、error response 和异常处理路径何时可用。早期没有中断和完整异常栈时，错误处理能力也受限；这会反过来影响硬件是否应允许某些访问进入未 ready 的目标。

## Boot 与安全边界

地址映射初始化还涉及安全和权限。secure boot、debug unlock、fuse read、ROM patch、firewall window 都在早期发生。BUS fabric 必须在“足够开放以完成初始化”和“足够封闭以保护资产”之间取舍。

| 设计对象 | 需要保护的语义 |
| --- | --- |
| fuse / key storage | 只允许可信 boot 阶段读取，后续锁定 |
| debug access | 未授权时不能绕过 CPU/firmware 读写安全区域 |
| remap register | boot 后应锁定，避免重定向 vector 或代码区 |
| DMA window | 初始化前不能访问未授权 memory |
| peripheral firewall | 外设打开前后权限可能不同 |

这类状态不能只放在安全章节里。它们改变 BUS 的 decode、access permission 和 error response，必须进入 boot path 的模型。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| 上电后地址 map 已经完整可用 | reset 默认 map 只覆盖最小启动路径，运行态 map 要逐步建立 |
| 地址 decode 成功就代表访问安全 | 目标 clock/reset/power/isolation 未 ready 时仍可能 error 或 hang |
| remap 只是软件表格变化 | remap 改变硬件路径，影响 fetch、异常向量、debug 和 DMA 视图 |
| boot 只关心 CPU | debug、DMA、防火墙、interrupt 和 cache 属性也会在启动中逐步纳入 |

## 一句话理解

boot path 是把最小可用 BUS 逐步扩展成完整系统 BUS 的状态机，地址映射只是这个状态机的可见表面。

## 建模启示

boot path 要按阶段建模，而不是按最终地址表建模。性能模型要记录每个阶段可用的 master、slave、bridge、clock domain、power domain 和 timeout 路径。功能模型要记录 reset 默认 map、remap 生效条件、clock/reset/power/isolation 状态、访问属性、安全权限、错误返回和异常处理可用性。

事件模型建议显式表达 `reset_deassert`、`rom_fetch_ok`、`strap_read`、`clock_enable_done`、`reset_release_done`、`sram_ready`、`remap_write_accept`、`remap_active`、`ddr_training_done`、`runtime_attr_programmed`、`security_lock_done`。这些事件决定某个地址在某一刻是 ROM、SRAM、DRAM、MMIO、错误路径，还是一次会让系统停止前进的未完成访问。
