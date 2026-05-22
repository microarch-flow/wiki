# Timeout、Fault 与 Hang 定位框架

上级：[05 性能与调试](./README.md)

相关：[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)、[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)、[Boot Path 与地址映射初始化](../04-microarchitecture-integration/boot-path-address-map-initialization.md)、[AXI Waveform Debug 方法](./axi-waveform-debug-method.md)

## 这页在回答什么问题

系统表现为“卡住了”时，不能马上把所有波形都摊开看。第一步要把现象分成 timeout、fault、hang 三类排查入口：有没有返回，返回的是错误还是超时，波形是否仍有 forward progress。

这三类不是互斥根因，而是观察层级。一个下游 slave 永不响应，在 fabric 层可能表现为 no-progress，在 timeout wrapper 层可能被包装成 timeout，在软件层可能变成异常、fault status 或任务超时。定位框架要把这些层级串起来。

## 三类现象的边界

| 类型 | 软件/系统看到什么 | BUS 层含义 | 首要问题 |
| --- | --- | --- | --- |
| timeout | 等了过长时间后得到错误、状态或 watchdog 触发 | 某处超时机制把长等待闭环 | 谁慢，还是谁把 hang 包装成 timeout |
| fault | 得到明确错误 response、fault record 或异常 | 某层主动拒绝或报告错误 | 谁报错，错误是否被中间层映射 |
| hang | 没有成功、没有错误、没有前进 | transaction 或状态机没有 forward progress | 哪个握手、队列或 response 永远不完成 |

timeout 是“等太久后有人收尾”；fault 是“有人明确说这笔访问不合法或失败”；hang 是“没有人收尾”。工程风险从 timeout 到 hang 逐步上升，因为 hang 可能让 CPU、DMA slot、bridge FIFO 或整个 fabric 永久占住资源。

## Timeout：有收尾，但超过预期

timeout 的价值是把 no-progress 或超长等待转换成可诊断事件。它可能由 software watchdog、DMA task timer、bridge timeout、fabric timeout wrapper、slave timeout 或 memory controller timeout 产生。

| Timeout 位置 | 说明 | 调试入口 |
| --- | --- | --- |
| software timeout | driver 等 completion 超时 | completion/status/interrupt path |
| DMA timeout | DMA 任务或 channel 等待过久 | descriptor/data/writeback 哪段未完成 |
| bridge timeout | 下游 APB/AHB/slave 不响应 | bridge request、PREADY/HREADY、error mapping |
| fabric timeout | transaction 在互连中等待过久 | route、arbiter、slave response |
| memory/controller timeout | DDR/SRAM controller 未按期返回 | queue、power state、ECC、training |

timeout 的关键问题是：timeout 报告的是根因位置，还是上游包装位置。一个 CPU MMIO read timeout 可能不是 CPU 附近的问题，而是低速 bridge 后面的外设未出 reset。

## Fault：明确错误也要追来源

fault 表示系统给出了错误语义。它比 hang 好定位，但仍要区分原生错误和映射错误。

| Fault 来源 | 典型信号或状态 | 归因要点 |
| --- | --- | --- |
| decode error | unmapped address、default slave response | 地址窗口或 remap 错误 |
| slave error | slave 拒绝访问或内部错误 | 目标存在但访问非法或失败 |
| permission fault | firewall/security/privilege fail | master ID、secure/privileged 属性 |
| IOMMU/SMMU fault | translation/context/permission fault | stream ID、IOVA、page table、TLB |
| protocol/bridge error | bridge 不支持 burst/width/attribute | 转换层语义收缩 |
| ECC/data fault | memory controller 报错 | data integrity、syndrome、response mapping |

fault 还要看传播路径。IOMMU fault 可能写 fault record 并触发 interrupt；AXI slave error 可能变成 RRESP/BRESP；bridge error 可能被上游合成为 SLVERR。调试时要记录原始 fault source 和软件最终看到的错误是否一致。

## Hang：没有 Forward Progress

hang 的判断标准不是“时间很长”，而是关键状态不再前进。

| Hang 形态 | 波形/状态表现 | 可能原因 |
| --- | --- | --- |
| request stuck | VALID 保持，READY 永远不来 | 下游 backpressure、queue full、clock/reset/power 未 ready |
| response missing | request 已接受，response 永远不回 | slave 无返回、bridge 丢 response、ID/slot 泄漏 |
| circular backpressure | 多个 FIFO/通道互相等待 | deadlock、ordering 约束、资源依赖环 |
| CDC no-progress | 一侧 push 后另一侧不 pop | clock stop、reset mismatch、CDC FIFO 状态错误 |
| software-visible hang | 硬件完成但软件等不到 | completion/interrupt/clear 路径断裂 |

hang 的危险在于它不会自动释放资源。一个未返回的 read 占住 outstanding slot，一个未释放的 bridge transaction 占住 FIFO，一个丢失的 completion 让 driver 停在等待状态。定位 hang 要找最后一个已确认完成的事件和第一个未完成的事件。

## 分层判断流程

| 步骤 | 问题 | 可能结论 |
| --- | --- | --- |
| 1 | 软件是否收到错误、异常、fault status 或 timeout status | 有则进入 timeout/fault 路径 |
| 2 | fabric 或 bridge 是否生成 timeout/error response | 有则定位包装层和下游原始等待 |
| 3 | 原始 request 是否被接受 | 未接受看 upstream backpressure；已接受看下游 |
| 4 | response 是否返回 | 未返回看 slave/bridge/ID/return path |
| 5 | 关键 handshake 是否还在变化 | 无变化则找 no-progress 点 |
| 6 | completion/interrupt 是否可见 | 硬件完成但软件未看到，查完成路径 |

这个流程的设计动机是先缩小层级，再看细节波形。若没有先判断“有没有 response”“错误从哪一层生成”，波形会把所有等待都混成同一种卡顿。

## 例子：CPU 读 MMIO 卡住

| 阶段 | 观察 | 结论 |
| --- | --- | --- |
| T0 | CPU 发起 MMIO read，AR 握手完成 | request 已进入 fabric |
| T1 | fabric route 到 AXI-to-APB bridge | 地址 decode 成功 |
| T2 | APB PSEL/PENABLE 后 PREADY 一直为 0 | 下游外设没有完成 access |
| T3 | bridge timeout counter 到阈值 | bridge 把 no-progress 包装成 timeout |
| T4 | CPU 收到错误 response 或异常 | 软件看到 timeout/fault |

若 T3 不存在，CPU 可能一直等不到 R response，现象就是 hang。是否配置 timeout wrapper，决定同一个根因最终是 timeout 还是 hang。

## 例子：DMA 任务无声停止

| 阶段 | 观察 | 可能分类 |
| --- | --- | --- |
| doorbell 已写入 | 控制路径完成 | 任务应启动 |
| descriptor fetch 发出但 IOMMU fault | 有 fault record | fault |
| descriptor fetch 发出但无 response | outstanding slot 不释放 | hang 或 timeout 前等待 |
| data move 完成但 completion 未写回 | 软件等不到完成 | completion path hang |
| completion 写回但 interrupt 未触发 | polling 能看到完成 | interrupt path fault/hang |

这个例子说明，DMA “没完成”必须拆段。descriptor fault、data timeout、writeback hang 和 interrupt 丢失在软件层看起来都像等待超时，但 BUS 归因完全不同。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| timeout 就是目标太慢 | timeout 可能是上游包装，根因可能是下游 hang |
| fault 一定比 hang 严重 | fault 至少有错误语义，hang 更可能泄漏资源并阻断系统 |
| 有 timeout wrapper 就不用看 hang | timeout 前的等待仍可能造成 tail latency 和资源占用 |
| 软件超时等于 BUS timeout | 软件 timer、DMA timer、fabric timeout 是不同层级 |
| 波形没错就不是 BUS 问题 | completion/interrupt/cache 可见性也会让软件等待 |

## 一句话理解

Timeout、fault 和 hang 是三种观察入口：timeout 有收尾但太晚，fault 有明确错误，hang 没有 forward progress。

## 继续阅读

- 如果你已经确定是 `fault`：先看 [AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)
- 如果你怀疑是 `IOMMU / permission` 一类 fault：看 [IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
- 如果你已经打开波形：看 [AXI Waveform Debug 方法](./axi-waveform-debug-method.md)
- 如果你想把现象收敛成可复盘记录：看 [BUS 故障复盘模板](../07-reference/bus-debug-postmortem-template.md)

## 建模启示

调试模型要把 timeout、fault 和 hang 建成不同终态。性能模型要记录 max latency、timeout threshold、last progress timestamp、outstanding age、queue high watermark 和 response wait。功能模型要记录 fault source、error mapping、timeout wrapper、resource release、completion visibility 和 interrupt/clear 状态。

事件模型建议显式表达 `request_accepted`、`last_forward_progress`、`response_missing`、`timeout_start`、`timeout_fire`、`fault_recorded`、`error_response_return`、`resource_release`、`completion_missing`。这些事件能把“卡住了”拆成可定位、可复盘、可修复的系统状态。
