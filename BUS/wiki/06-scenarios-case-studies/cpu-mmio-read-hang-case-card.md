# CPU 读 MMIO 卡死案例卡

上级：[06 典型系统与案例](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[APB Peripheral Subsystem 案例卡](./apb-peripheral-subsystem-case-card.md)、[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)、[AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)

## 现象

CPU 执行一次 MMIO read 后，软件线程、驱动初始化流程或整个系统停住。软件没有拿到寄存器值，也没有进入预期的错误处理路径。

这张案例卡默认讨论“读 transaction 没有正常闭环”。若软件已经收到 abort、exception、SLVERR/DECERR 或明确 fault status，应先走 fault 分支；若 fabric/bridge 生成 timeout error，应按 timeout 分支继续追下游原始等待点。

## 典型路径

```text
CPU load
  -> cache/MMU attribute check: device / non-cacheable
  -> main interconnect
  -> bridge / APB subsystem
  -> peripheral register block
  -> read data / error response return
  -> CPU retires load or takes exception
```

| 阶段 | 期望事件 | 可能卡住的位置 |
| --- | --- | --- |
| T0 | CPU 发出 read request | CPU store/load unit 或属性配置 |
| T1 | interconnect 接收并 decode 地址 | unmapped address、firewall |
| T2 | bridge 接收请求 | bridge slot full、CDC/reset |
| T3 | APB setup/access | PREADY 永远不来、clock gated |
| T4 | slave 返回 PRDATA/PSLVERR | 目标未出 reset、非法寄存器 |
| T5 | bridge 生成上游 R response | error mapping 或 response FIFO |
| T6 | CPU 收到 R beat 或异常 | return path backpressure |

读 MMIO 的危险点在于 CPU load 需要 response 才能退休。若系统没有 timeout/error wrapper，一次低速外设无响应就可能让 CPU 停在这条 load 上。

## 根因矩阵

| 根因 | BUS 表现 | 分类 |
| --- | --- | --- |
| 地址 decode 没命中，且没有 default slave | request 无目标或无 response | hang |
| 地址 decode miss 被 default slave 接住 | 返回 DECERR/SLVERR | fault |
| 外设 clock/reset 未 ready | PREADY/HREADY 不来 | hang 或 timeout |
| power/isolation 未释放 | bridge 或 slave 不响应 | hang 或 timeout |
| APB bridge 内部 slot 泄漏 | 后续 MMIO 都卡住 | hang |
| 访问非法寄存器窗口 | slave 拒绝或不响应 | fault 或 hang，取决于设计 |
| return path FIFO 被堵 | slave 已返回但 CPU 收不到 | hang/timeout |
| CPU 属性把 MMIO 当 cacheable | 行为偏离设备语义 | stale value、side effect 或不可预期 |

同一个根因最终表现为何种类型，取决于系统是否有 default slave、timeout wrapper、error mapping 和异常处理路径。

## 排查顺序

| 步骤 | 问题 | 观察点 |
| --- | --- | --- |
| 1 | 软件有没有收到异常或错误 response | CPU exception、RRESP、driver status |
| 2 | AR/read request 是否真正发出 | `ARVALID && ARREADY` 或等价握手 |
| 3 | 地址是否 decode 到预期 slave | decoder hit、route trace、firewall |
| 4 | bridge 是否接受并发出下游访问 | bridge slot、APB PSEL/PENABLE |
| 5 | APB slave 是否完成 access | PREADY、PSLVERR、PRDATA |
| 6 | response 是否回到 CPU | RVALID/RREADY、response FIFO |
| 7 | timeout/fault 是否释放资源 | outstanding slot、bridge FIFO、CPU load |

这个顺序的目标是找第一个未闭环点，而不是只确认 CPU 端卡住。

## 波形判断

| 波形现象 | 解释 |
| --- | --- |
| CPU side AR 没有 fire | 请求还没进入 fabric，查 CPU 属性、outstanding、上游 backpressure |
| AR fire 后 bridge 没收到 | route/decode/firewall/interconnect 问题 |
| APB PSEL/PENABLE 出现但 PREADY 永远为 0 | 外设未 ready、clock/reset/power 问题 |
| APB 完成但上游 R 不回 | bridge response path 或 return path 问题 |
| 返回 RRESP 错误 | 进入 fault 路径，追错误源 |
| timeout 后返回错误 | 下游等待被 timeout wrapper 包装 |

波形里最关键的是 `request accepted` 和 `response returned`。中间任何一层只要没有 forward progress，就要看它是应返回错误、应 timeout，还是设计上允许等待。

## 例子：APB 外设时钟没开

| 阶段 | 事件 | 结果 |
| --- | --- | --- |
| T0 | CPU read `timer.STATUS` | AR fire 成功 |
| T1 | interconnect route 到 APB bridge | decode 正确 |
| T2 | APB bridge 发出 PSEL/PENABLE | 下游 access active |
| T3 | timer clock disabled | PREADY 维持 0 |
| T4a | bridge 有 timeout | 返回错误，软件进入 fault/timeout 处理 |
| T4b | bridge 无 timeout | CPU load 永不退休，系统 hang |

这个例子说明，修复方式不只是“打开时钟”。系统还要决定未 ready 外设被访问时应返回错误、等待 timeout，还是通过 power/clock controller 阻止访问。

## 修复与设计边界

| 修复方向 | 适用场景 | 风险 |
| --- | --- | --- |
| 增加 default slave/error response | decode miss 或非法 window | 软件要能处理错误 |
| bridge timeout | 下游可能不响应 | timeout 阈值过短会误伤慢外设 |
| ready/status guard | 访问前检查 clock/power/reset 状态 | 软件流程更复杂 |
| power-aware firewall | target 未 ready 时拦截访问 | 权限和状态配置要可靠 |
| debug/status side path | hang 后仍可取证 | 增加面积和安全边界 |

好的设计不是让所有 MMIO read 都成功，而是让失败以可诊断方式闭环，并且释放占用的资源。

## 观测点

| 观测点 | 要记录 |
| --- | --- |
| CPU/master side | read request accepted、outstanding age |
| decoder/router | address hit/miss、target port |
| bridge | slot occupancy、downstream request、timeout |
| APB | PSEL/PENABLE/PREADY/PSLVERR、wait cycles |
| return path | R response latency、FIFO occupancy |
| fault/timeout | error source、resource release |

这些观测点能把“CPU 卡住”拆成 decode、bridge、slave、return path 或软件属性问题。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| CPU 读卡住就是 CPU 问题 | CPU 只是等待一个未闭环的 BUS response |
| APB 外设慢一点没关系 | 无 timeout 的慢/死外设会让 CPU load 永久等待 |
| 有错误返回就不是问题 | 错误返回要可归因、可恢复，并释放资源 |
| 只要打开外设时钟就修好了 | 还要处理 reset、power、isolation、非法地址和 timeout |

## 一句话理解

CPU 读 MMIO 卡死，本质是一笔 device read 没有完成闭环：要么返回数据，要么返回错误，要么 timeout 后释放资源。

## 建模启示

这个案例要建模成 MMIO read transaction 的闭环状态机。Resource 包括 CPU load slot、interconnect route、bridge slot、APB slave、return FIFO 和 timeout wrapper；Topology 决定 read 经过哪些 bridge 和 power/reset boundary；Interaction 是 AR/request、APB access、R response 或错误返回；Capability 是 default slave、timeout、error mapping、debug status 和 resource release。

事件模型建议显式表达 `cpu_mmio_read_issue`、`read_request_accept`、`decode_hit_or_miss`、`bridge_accept`、`apb_access_start`、`pready_seen`、`timeout_fire`、`r_response_return`、`resource_release`。这些事件能把 fault、timeout 和 hang 分开，并给软件、硬件和验证各自明确的修复入口。
