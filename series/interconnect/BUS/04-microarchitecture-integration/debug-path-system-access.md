# Debug Path 与 System Access

上级：[04 微架构与系统集成](./README.md)

相关：[Boot Path 与地址映射初始化](./boot-path-address-map-initialization.md)、[互连组件与数据路径分解](./interconnect-components.md)、[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

Debug path 就像大楼里的**消防通道**——平时不走，但火灾时（CPU hang、boot 失败、系统崩溃）它是唯一能进入现场的路径。外部调试器通过这条通道进入系统，检查寄存器、读取内存、暂停/恢复 CPU、采集”事故现场”。

它的特殊性不在于”权限更高”，而在于它必须在**大楼停电、电梯停运、门禁失效**的情况下仍然能用。设计 debug path 时，核心问题是：消防通道能到哪些楼层（可达性）、会不会误触报警器（副作用）、会不会和正常人流抢电梯（优先级）、安全门怎么管（隔离）。

## Debug Master 是一个特殊 Bus Master

从 BUS 角度看，debug access 不是神秘通道，而是一类 master 发起的 transaction。它可以接在主互连、低速配置互连、always-on island、access-port bridge 或专门的 debug fabric 上。

| Debug 能力 | BUS 上的对应行为 | 建模关注点 |
| --- | --- | --- |
| memory read/write | debug master 发起 memory transaction | cache 可见性、权限、目标是否上电 |
| MMIO read/write | 访问寄存器和状态位 | side effect、WSTRB、访问顺序 |
| halt/resume CPU | 写 debug/control 寄存器或专用接口 | CPU 状态机和 BUS 请求的交互 |
| trace / snapshot | 读取 trace buffer 或系统状态 | 带宽、回压、读清副作用 |
| fault forensics | 在异常后读取寄存器、memory、status | 访问路径是否仍然可用 |

debug master 的设计动机是提高可观察性和可恢复性。代价是它可能绕过普通软件权限、干扰正在运行的系统、与 CPU/DMA 竞争互连资源，甚至改变要观察的现场。因此 debug path 必须被当成真实 master 建模，而不是“外部工具读一下”。

## 可达性：异常状态下还能访问什么

debug path 的价值来自异常状态下的可达性。不同系统状态下，可访问范围会变化。

| 系统状态 | Debug 期望 | BUS 风险 |
| --- | --- | --- |
| reset 后早期 boot | 读 strap/fuse、ROM 状态、最小 MMIO | 主互连未 ready，只能走 always-on 或 debug bridge |
| CPU hang | 读取 CPU debug 状态和关键 memory | CPU 持有锁或 outstanding，debug 访问可能被同一热点阻塞 |
| 外设 timeout | 读取 bridge、slave、timeout counter | 访问同一故障路径可能再次 hang |
| low power | 唤醒或访问 always-on 状态 | 目标 power domain 关闭，isolation 未释放 |
| secure locked | 限制对 key、fuse、secure memory 的访问 | 未授权 debug 不能成为安全绕过路径 |

可达性设计的 trade-off 很直接：debug 越独立，异常取证能力越强，面积和安全风险越高；debug 越依赖主互连，成本低但在主互连 hang 时可能一起失效。

## 接入位置决定故障可见性

debug path 接在哪里，会决定它能看见什么、会被什么阻塞。

| 接入位置 | 收益 | 限制 |
| --- | --- | --- |
| 主 crossbar 的普通 master 端口 | 访问范围广，模型与其他 master 一致 | 主互连故障时 debug 也可能被阻塞 |
| always-on debug bridge | boot/low power 可用性高 | 带宽低，访问范围受限 |
| APB/低速配置互连入口 | 适合寄存器取证 | 难以访问高带宽 memory 或 trace |
| CPU debug interface | 可 halt/resume、读核心状态 | 不能替代系统级 memory/MMIO 访问 |
| trace fabric / buffer | 适合事后分析 | trace 数据本身需要 BUS 读出，可能受带宽限制 |

架构上常见的折中是双路径：一条低速 always-on debug path 保证最小取证能力，一条系统 access path 进入主互连访问 memory 和外设。模型要区分这两条路径的 clock、reset、权限和错误返回。

## Debug 与正常流量的争用

debug access 会改变系统时序。在线调试时，debug master 可能与 CPU、DMA、display 或 memory controller 竞争同一互连资源。

| 争用点 | 可能结果 | 设计取舍 |
| --- | --- | --- |
| memory controller | debug memory dump 增加 CPU/DMA latency | 限速 debug，或给 debug 低 QoS |
| APB bridge | debug 读寄存器阻塞软件配置访问 | debug 优先可取证，低优先可减少干扰 |
| timeout path | debug 访问故障目标再次触发 timeout | 需要 bypass/status-only 路径 |
| response path | 大量 debug read 占用返回带宽 | 限制 burst/outstanding |
| lockstep/实时系统 | debug halt 改变实时行为 | 需要明确 halt 权限和状态冻结范围 |

debug 优先级不是越高越好。高优先级能在系统忙时取证，也可能破坏实时流或掩盖原始性能问题；低优先级减少干扰，但在拥塞场景下读不到关键状态。建模时要显式记录 debug QoS、限速、outstanding 上限和仲裁策略。

## Cache、MMIO 与 Side Effect

debug 访问 memory 和 MMIO 时，语义不能混用。

| Debug 操作 | 风险 | 建模方式 |
| --- | --- | --- |
| 读 CPU 正在修改的 memory | 可能看到 cache 中未写回的数据之外的旧值 | 记录是否 snoop cache、是否 halt CPU、是否 flush/invalidate |
| 写 memory patch | 与 CPU cache line 不一致 | 需要 cache maintenance 或 coherent debug access |
| 读 clear-on-read 状态寄存器 | 改变被调试对象状态 | 标记 read side effect |
| 写 command register | 触发设备动作 | 需要确认 debug 写是否允许触发副作用 |
| 读 FIFO data register | pop 掉设备数据 | 不应把所有 MMIO read 视为无害观察 |

debug 的取证目标是观察现场，但 BUS 访问本身可能改变现场。硬件可以提供 shadow register、snapshot buffer、freeze-on-halt 或 read-only debug alias 来降低副作用；没有这些机制时，模型要把 debug read/write 当成会影响状态的 transaction。

## 低功耗、Reset 与 Isolation

debug path 在 power/reset 场景里最容易被误建模。一个目标地址在运行态可访问，不代表 suspend、retention、partial reset 或 isolation 状态下可访问。

| 状态 | Debug 访问结果 | 需要定义 |
| --- | --- | --- |
| target power off | 返回错误、触发唤醒，或被 debug bridge 拦截 | 哪些目标可 wake，哪些只能读 status |
| target reset asserted | 寄存器可能为 reset value 或不可访问 | reset 域与 debug 域关系 |
| isolation enabled | transaction 不应穿过 power boundary | debug 是否能解除 isolation |
| clock gated | access 可能需要唤醒时钟 | 唤醒延迟和 timeout 策略 |
| debug domain reset | 外部工具连接但内部 debug 不可用 | 连接状态与 BUS 可达性分离 |

调试工具显示“connected”，不代表 system access path 已经可用。模型需要分离 external link、debug controller、access port、system bus path 和 target domain 的状态。

## 安全与权限

debug path 是安全边界的一部分。未授权 debug 不能绕过 secure boot、firewall、IOMMU/SMMU、memory protection 或 fuse lock。

| 保护对象 | Debug 设计要求 |
| --- | --- |
| secure memory / key | 未 unlock 时返回错误或屏蔽数据 |
| fuse / OTP | 读取权限随 lifecycle state 改变 |
| debug unlock | 必须有认证、生命周期和失败锁定策略 |
| firewall window | debug master 也要有 master ID 和权限检查 |
| DMA / peripheral register | debug 写不能绕过软件期望的安全状态 |

安全取舍在于 bring-up 便利性和资产保护。开发模式需要高可见性，量产模式需要锁定或缩小 debug 能力。BUS 模型要把 debug master ID、secure/non-secure 属性、privilege、firewall 命中和错误返回写清楚。

## 例子：CPU Hang 后读取现场

CPU 因一次 MMIO read 卡住后，debugger 试图读取现场。路径可能如下：

| 阶段 | Debug 事件 | BUS 依赖 | 风险 |
| --- | --- | --- | --- |
| T0 | 外部工具连接 debug controller | debug domain clock/reset | connected 不代表 system access 可用 |
| T1 | halt CPU 或读取 CPU debug status | CPU debug interface | CPU 可能停在未完成 bus transaction 上 |
| T2 | 读取 timeout/status register | always-on 或 APB debug path | 若走同一故障 bridge，可能再次 hang |
| T3 | 读取 faulting address 附近 memory | system access path -> memory | cache 可见性和权限影响结果 |
| T4 | 读取 target peripheral status | APB/MMIO path | read side effect 可能清掉状态 |
| T5 | 写 reset/clear 寄存器恢复目标 | MMIO write path | 写入可能改变现场，需记录顺序 |

这个例子的关键不是 debug 能不能读某个地址，而是它读这个地址要不要经过故障点。独立 status path 能把 hang 变成可诊断错误；依赖同一故障路径的 debug access 可能只复制故障。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| debug 访问不影响系统 | debug 是真实 BUS transaction，会争用资源并可能触发 MMIO side effect |
| 连接上调试器就能访问全系统 | external link、debug controller、system access path、target domain 是不同状态 |
| debug master 应该最高优先级 | 高优先级利于取证，也会干扰实时流和性能测量 |
| 安全锁只影响 CPU 软件 | debug master 也必须经过权限、firewall 和 lifecycle 检查 |

## 一句话理解

debug path 是用于观察和救援的侧向 BUS master；它越有用，越需要被严格建模为会争用、会受限、会改变状态的访问路径。

## 建模启示

debug path 要按 master、路径和目标状态建模。性能模型要记录 debug 接入点、QoS/priority、限速、outstanding 上限、共享仲裁点、return path 带宽和低功耗唤醒延迟。功能模型要记录 debug master ID、权限、secure 属性、firewall、target power/reset/isolation、MMIO side effect、cache 可见性和错误返回。

事件模型建议显式表达 `debug_link_connected`、`debug_auth_passed`、`debug_master_request`、`debug_route_select`、`debug_qos_grant`、`target_domain_ready`、`debug_read_side_effect`、`debug_error_return`、`debug_halt_cpu`、`debug_clear_fault`。这些事件决定 debug path 是能帮助定位问题，还是在故障、低功耗或安全状态下成为另一条不可解释的访问路径。
