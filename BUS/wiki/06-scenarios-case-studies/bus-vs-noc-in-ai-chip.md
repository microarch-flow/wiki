# AI 芯片里的 BUS vs NoC

上级：[06 典型系统与案例](./README.md)

相关：[BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)、[MCU / SoC / AI 芯片中的 BUS 对照](./mcu-soc-ai-bus-comparison.md)、[CPU、DMA、外设与内存之间的总线路径](../04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)、[NoC Wiki 首页](../../../NOC/wiki/README.md)

## 这页在回答什么问题

AI 芯片同时需要 BUS 和 NoC，因为它们解决的不是同一个问题。BUS 更擅长承载软件可见的控制语义：寄存器配置、doorbell、status、completion、boot、debug、power/clock 管理。NoC 更擅长承载大规模数据交换：tile 间流量、DMA/NI 到 SRAM/HBM 的高吞吐访问、分布式计算单元之间的并发传输。

关键不是“有 NoC 后是否还需要 BUS”，而是控制语义和数据吞吐应该在哪个边界分开，以及这个边界如何被软件、debug 和故障恢复观察到。

## 典型分工

| 路径 | 更适合 BUS | 更适合 NoC |
| --- | --- | --- |
| 寄存器配置 | tile/control block 的 MMIO 配置 | 大量配置广播可通过 NoC 承载，但边缘仍呈现 MMIO 语义 |
| doorbell/start | CPU/runtime 启动 DMA、NI、kernel | doorbell 进入网络边界后触发大规模任务 |
| status/completion | 软件可见完成、错误码、interrupt | 分布式完成聚合可在 NoC 内传播 |
| tensor/data movement | 小规模或控制数据 | tile-to-tile、SRAM/HBM、大规模并发 |
| debug/boot | 最小可达路径、寄存器取证 | trace/telemetry 可通过网络汇聚 |
| power/clock/reset | 管理寄存器和状态机 | 分布式控制消息可辅助传播 |

BUS 的设计动机是语义清楚和可诊断；NoC 的设计动机是规模化并发和拓扑扩展。二者不是替代关系，而是系统分层。

## Resource、Topology、Interaction、Capability 对照

| 视角 | BUS 控制骨架 | NoC 数据网络 |
| --- | --- | --- |
| Resource | 寄存器、status、debug、DMA/NI control、interrupt | tile、router、link、VC、SRAM/HBM port、NI |
| Topology | 分层 bus、bridge、低速外设子系统、debug path | mesh、torus、tree、ring、custom fabric |
| Interaction | MMIO read/write、doorbell、completion、fault/status | packet/flit、credit、routing、multicast、collective |
| Capability | ordering、side effect、error/timeout、软件可见性 | bandwidth、flow control、deadlock avoidance、QoS、scalability |

这个对照说明：BUS 的 Capability 重点是“软件能否正确控制和观察硬件”，NoC 的 Capability 重点是“数据能否在大规模节点之间持续流动”。

## 边界：NI / DMA / Bridge

AI 芯片里，BUS 与 NoC 的边界常落在 network interface、DMA engine、command queue、doorbell register 或 bridge 上。

```text
CPU/runtime
  -> BUS MMIO: configure DMA/NI/tile
  -> BUS doorbell: start command
  -> NI/DMA translates command into NoC packets
  -> NoC moves tensor/control data
  -> completion/status returns to BUS-visible state
  -> interrupt or polling wakes software
```

| 边界对象 | 责任 | 风险 |
| --- | --- | --- |
| NI register block | 暴露配置、doorbell、status | MMIO side effect、interrupt/clear 顺序 |
| DMA command queue | 把软件任务转成 data movement | descriptor 可见性、IOMMU、completion |
| BUS-NoC bridge | 协议/packet 转换 | ordering、error mapping、backpressure |
| completion aggregator | 汇总 tile/NI 完成状态 | partial completion、lost event |
| debug/telemetry bridge | 把分布式状态带回软件 | trace 带宽、snapshot 一致性 |

边界设计的 trade-off 是：把更多控制流放进 NoC 可以减少单独 BUS 布线，但会让 boot/debug/fault 依赖更复杂的运行态网络；保留独立 BUS 控制骨架可诊断性更好，但覆盖大量 tile 时面积和地址管理成本上升。

## 例子：启动一个 AI Kernel

| 阶段 | 事件 | BUS / NoC 分工 |
| --- | --- | --- |
| T0 | runtime 写 kernel descriptor | CPU memory path，可能经 BUS/AXI 到 memory |
| T1 | runtime 配置 tile/NI 寄存器 | BUS MMIO，要求顺序和 side effect 正确 |
| T2 | runtime 写 doorbell | BUS 控制写触发 NI/DMA |
| T3 | NI/DMA 读取 descriptor | BUS/AXI/SMMU path 读取任务 |
| T4 | NI 发起 NoC packet flow | NoC 承载 tile-to-tile 或 HBM 数据 |
| T5 | tiles 写 partial completion | NoC 或本地 fabric 聚合状态 |
| T6 | completion 对 CPU 可见 | BUS-visible status/completion memory |
| T7 | interrupt/assert event | interrupt controller 或 runtime polling |

这个例子里，性能瓶颈可能在 NoC 数据面；软件卡住却可能发生在 BUS-visible completion。调试时要分清“数据网络没完成”还是“完成状态没有回到软件语义边界”。

## 常见边界错误

| 错误 | 表现 | 正确建模 |
| --- | --- | --- |
| 把高吞吐 tensor traffic 放到低速 BUS | 带宽不足、控制路径被挤压 | tensor data 进入 NoC/HBM fabric |
| 把所有控制状态藏进 NoC | boot/debug 时无法访问 | 保留最小 BUS/debug 可达路径 |
| completion 聚合不可靠 | kernel 已完成但 runtime 等不到 | completion/event/status 要闭环 |
| BUS-NoC backpressure 未定义 | doorbell 被接收但任务不启动 | command queue 和 credit 状态要可见 |
| fault 只停在 NoC 内部 | 软件只看到 timeout | fault record 要映射回 BUS-visible status |

这类错误的共同点是边界语义不清。NoC 内部可以用 packet、credit、VC 和 routing 管理流量，但软件需要看到的是任务状态、错误、完成和可恢复入口。

## 观测点

| 层级 | 观测内容 |
| --- | --- |
| BUS control | MMIO config、doorbell、status read、clear/EOI |
| command queue | descriptor fetch、queue occupancy、command accept |
| NI/bridge | BUS command 到 NoC packet 的转换、credit wait |
| NoC | injection/ejection rate、VC occupancy、route wait、drop/error |
| completion | partial done、aggregate done、completion visible |
| debug/boot | minimal access path、snapshot、last progress |

观测点必须跨越 BUS-NoC 边界。只看 NoC bandwidth，无法说明软件为什么没看到 completion；只看 BUS MMIO，也无法说明 NoC 内部是否被 credit 或路由限制。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| AI 芯片有 NoC，就不需要 BUS | BUS 仍负责软件可见控制、boot、debug、status 和错误闭环 |
| BUS 也能搬数据，所以不需要 NoC | BUS 不适合承载大规模 tile/HBM 并发数据面 |
| BUS 和 NoC 是硬二选一 | 二者在 NI/DMA/bridge 边界协同 |
| NoC 完成就等于软件完成 | completion/status 还要回到 BUS-visible 或 runtime-visible 状态 |

## 一句话理解

AI 芯片里的 BUS 负责控制语义和可诊断边界，NoC 负责大规模数据交换；真正的设计重点是二者交界处的任务、完成和错误如何闭环。

## 建模启示

AI 芯片中的 BUS vs NoC 要按边界建模。Resource 侧要区分寄存器/status/debug 资源与 tile/router/link/HBM 资源；Topology 侧要区分控制 bus、NoC、local SRAM/HBM path 和 bridge/NI；Interaction 侧要区分 MMIO/doorbell/completion 与 packet/credit/routing；Capability 侧要区分软件可见性、error mapping、debug reachability 与 bandwidth、QoS、deadlock avoidance。

事件模型建议显式表达 `mmio_config_write`、`doorbell_accept`、`ni_command_accept`、`noc_packet_inject`、`noc_credit_wait`、`tile_compute_done`、`completion_aggregate`、`completion_visible_to_runtime`、`fault_map_to_status`。这些事件能把 AI 芯片里的控制闭环和数据网络进展放进同一个模型。
