# AXI Crossbar 案例卡

上级：[06 典型系统与案例](./README.md)

相关：[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)、[Shared Bus、Bus Matrix 与 Crossbar](../04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)、[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[Counters、Trace 与观测点设计](../05-performance-debug/counters-trace-observation-points.md)

## 这页在回答什么问题

AXI crossbar 就像一个**多进多出的立交桥**——它的价值不是”看起来高级”，而是让去不同方向的车可以同时走，不用都挤在同一个红绿灯路口排队。但如果多辆车都要去同一个出口，在那个出口处还是得排队。

这个案例卡用四个视角——谁在共享什么（Resource）、路怎么连的（Topology）、车怎么走完全程（Interaction）、基础设施够不够（Capability）——判断一个 AXI crossbar 是否设计合理。

## 案例背景

假设系统有这些参与者：

| 类型 | 示例 |
| --- | --- |
| Master | CPU cluster、DMA、display controller、accelerator、debug master |
| Slave | DDR controller、SRAM、APB bridge、configuration block、trace buffer |
| 关键流量 | CPU read、DMA burst write、display read、debug MMIO、accelerator data movement |

如果使用 shared bus，CPU 读 SRAM、DMA 写 DDR、debug 读 APB 都要排在同一全局时间轴上。AXI crossbar 的设计动机是让访问不同目标的流量并行，同时把同一目标的争用限制在目标端口附近。

## 四个视角

| 视角 | Crossbar 中要回答的问题 |
| --- | --- |
| Resource | 哪些 master、slave、ID slot、buffer、return path 是共享资源 |
| Topology | 是否全连接，哪些路径被裁剪，仲裁在入口还是出口 |
| Interaction | AW/W/B、AR/R 如何配对，ID/outstanding 如何分配和释放 |
| Capability | 支持多少并发、QoS、错误返回、ID remap、observability |

这四个视角能避免把 crossbar 简化成“多输入多输出开关”。真正决定行为的是每个输出端口的仲裁、每条 return path 的带宽、每个 ID slot 的释放条件。

## 典型并发矩阵

| 流量 A | 流量 B | Crossbar 期望行为 | 仍可能阻塞的位置 |
| --- | --- | --- | --- |
| CPU -> SRAM | DMA -> DDR | 并行 | master input queue、return path |
| CPU -> DDR | display -> DDR | 同出口竞争 | DDR output arbiter、DDR scheduler |
| DMA -> APB bridge | debug -> APB bridge | 同 bridge 竞争 | APB bridge FIFO、PREADY wait |
| accelerator -> SRAM | CPU -> APB | 并行 | 若共享内部 register slice 或 clock crossing |
| two DMA -> same SRAM | 目标端口仲裁 | SRAM port、output queue |

这个矩阵是评估 crossbar 的核心。若系统的主要流量都打到同一个 DDR controller，crossbar 只能减少其他目标的串行化，不能消除 DDR 热点。

## 设计收益

| 收益 | 来自哪里 | 边界 |
| --- | --- | --- |
| 不同目标并行 | 多输出端口和独立仲裁 | 同一 slave 仍会竞争 |
| 降低全局 head-of-line blocking | 按目标或通道分队列 | 若每 master 单队列，仍可能 HOL |
| 提升 outstanding 利用 | 多 ID、多 slave 并发 | 受 slave slot、ID remap、return path 限制 |
| 保护关键流 | QoS/priority per port | 配置错误会饿死低优先级流 |
| 错误路径更清晰 | decoder/default slave/port error | 需要记录错误来源和映射 |

crossbar 的演化动机是局部并发。代价是面积、布线、时序、验证和可观测性复杂度上升。

## 主要风险

| 风险 | 具体表现 | 建模/验证要点 |
| --- | --- | --- |
| return path 被低估 | R/B response 回不来，outstanding slot 不释放 | response FIFO、return arbiter、RREADY/BREADY |
| ID remap slot 耗尽 | 上游还能发，下游 slot 已满 | ID table、slot release、error recovery |
| AW/W 配对复杂 | write address 和 data 到达节奏不同 | W buffering、目标选择、WLAST |
| 慢 slave 反压扩散 | APB bridge 或低速目标拖住相关路径 | 队列粒度、per-target isolation |
| QoS 失效 | realtime/display 被 DMA 挤压 | grant counter、wait histogram |
| error source 不清 | 软件只看到 SLVERR/DECERR | decoder、bridge、slave、timeout 归因 |

这些风险说明 crossbar 的复杂度集中在“并发之后如何闭环”。能并行发出请求只是第一步；response 能正确返回并释放资源，才是 transaction 完成。

## 例子：CPU、DMA、Display 共享 DDR

| 阶段 | 事件 | Crossbar 行为 | 可观察风险 |
| --- | --- | --- | --- |
| T0 | CPU 发 read 到 DDR | 进入 DDR output queue | 与 display/DMA 竞争 |
| T1 | display 发实时 read 到 DDR | QoS 应提高优先级 | QoS 错误会 underflow |
| T2 | DMA 发长 burst write 到 DDR | write queue 积累 | CPU read tail latency 上升 |
| T3 | DDR return data 回 crossbar | return arbiter 分配 R path | R channel 抖动 |
| T4 | CPU read response 回来 | CPU outstanding slot 释放 | 若 response 卡住，CPU 后续 AR 停止 |

这个例子里，crossbar 已经消除了 APB/SRAM 等无关目标的干扰，但 DDR 仍是热点。调试时不应把所有慢都归给 crossbar，也不能忽略 crossbar return path。

## 观测点

| 观测点 | 要记录 |
| --- | --- |
| master input | request count、VALID/READY stall、outstanding |
| per-output arbiter | grant、wait cycles、QoS class、winner |
| ID/remap table | allocated slot、release、overflow |
| per-target queue | occupancy、high watermark、head-of-line blocking |
| return path | R/B response count、wait、FIFO occupancy |
| error path | decode miss、slave error、timeout source |

这些观测点要能按 master、slave、ID、read/write、QoS class 分类。否则 crossbar 的性能问题会被淹没在总带宽指标里。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| crossbar 等于无阻塞 | 不同目标可并行，同一目标和 return path 仍会竞争 |
| full connection 一定最好 | 裁剪无用路径可以节省面积和验证成本 |
| ID 越多越快 | 还受 slave slot、return path、controller 和 QoS 限制 |
| 慢 slave 只影响自己 | 队列粒度不当时会造成 head-of-line blocking |

## 一句话理解

AXI crossbar 用更多 Resource 和更复杂 Topology 换取不相关 Interaction 的局部并发，但 Capability 上限仍受目标端口、ID slot 和 return path 限制。

## 建模启示

AXI crossbar 要建模成多 service point 系统，而不是单一带宽资源。性能模型要记录 per-output arbiter、per-target queue、ID/remap slot、return path、QoS class、head-of-line blocking 和 hotspot slave。功能模型要记录 route decode、AW/W 配对、RID/BID 匹配、ordering、error source 和 timeout/resource release。

事件模型建议显式表达 `route_decode`、`output_queue_enqueue`、`output_arbiter_grant`、`id_slot_allocate`、`write_data_match`、`return_path_grant`、`id_slot_release`、`crossbar_error_route`。这些事件能解释 crossbar 哪些路径真正并行，哪些路径仍被热点、return path 或 ID slot 限制。
