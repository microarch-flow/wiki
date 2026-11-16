# BUS 设计检查清单

上级：[07 术语与检查清单](./README.md)

相关：[BUS 一页版总览](./bus-one-page.md)、[Master/Slave/Bridge 设计清单](./master-slave-bridge-checklists.md)、[DDR/IOMMU/Debug 集成清单](./ddr-iommu-debug-checklists.md)

## 使用方式

这份清单用于设计评审或方案比较。不要只检查协议字段是否完整，要检查事务能否闭环、错误能否释放资源、软件语义是否清楚、性能瓶颈是否可观测。

## 功能层

| 检查项 | 要回答的问题 |
| --- | --- |
| master/slave 列表 | 所有发起方和目标方是否列全，包括 CPU、DMA、debug、boot master |
| address map | 地址窗口是否完整、互斥、可解释，decode miss 是否有去处 |
| permission/security | master ID、secure/non-secure、privilege/firewall 是否定义 |
| transaction closure | 每类 read/write 是否一定返回 data、response、error 或 timeout |
| ordering | 哪些访问必须保序，哪些允许重排，软件是否知道边界 |
| error semantics | decode error、slave error、timeout、fault 如何区分和上报 |
| resource release | error/timeout 后 outstanding、FIFO、ID slot 是否释放 |

## 性能层

| 检查项 | 要回答的问题 |
| --- | --- |
| traffic matrix | 哪些 master 访问哪些 slave，流量大小和突发形态是什么 |
| hotspot | 热点是否在 DDR、SRAM、bridge、APB、return path 或 SMMU |
| burst | burst 长度、对齐、边界拆分是否会拖慢小请求 |
| outstanding | master、interconnect、slave、SMMU、DDR 的 slot 是否匹配 |
| arbitration/QoS | 关键流是否有优先级或保底，低优先级是否有 starvation bound |
| backpressure | 下游慢时回压会传播到哪里，是否影响无关流量 |
| tail latency | 是否分析 p99/max，而不是只看平均 latency |
| completion latency | 软件可见完成是否单独测量，不被 data bandwidth 掩盖 |

## 集成层

| 检查项 | 要回答的问题 |
| --- | --- |
| protocol bridge | AXI/AHB/APB/TileLink 转换后，ordering、error、attribute 是否保留 |
| CDC | 时钟域 crossing 的 FIFO/handshake、reset、满空状态是否定义 |
| width adaptation | byte lane、WSTRB、partial access、MMIO side effect 是否正确 |
| low power/reset | target 未上电、clock gated、reset asserted 时访问行为是什么 |
| boot path | reset 默认 map、ROM/SRAM/DDR bring-up、remap 是否有阶段定义 |
| debug path | CPU hang、low power、secure lock 下是否还能取证 |
| DMA/IOMMU | descriptor/data/writeback 地址、权限、cache 属性是否一致 |

## 软件语义层

| 检查项 | 要回答的问题 |
| --- | --- |
| MMIO attribute | 寄存器区域是否 device/non-cacheable，禁止错误缓存和预取 |
| side effect | read-clear、write-one-to-clear、FIFO pop、command write 是否标出 |
| barrier contract | descriptor -> doorbell、completion -> interrupt、clear/EOI 顺序是否定义 |
| cache/coherence | DMA buffer、descriptor、completion 是否有 coherent 或 maintenance 规则 |
| interrupt path | enable、pending、status、clear、EOI 与 BUS 访问顺序是否清楚 |
| polling | polling 频率是否会压垮低速 APB/bridge |

## 可观测性层

| 检查项 | 要回答的问题 |
| --- | --- |
| counters | 是否有 request accept、grant wait、stall、service、response latency |
| queue visibility | FIFO occupancy、high watermark、outstanding age 是否可见 |
| error/fault | decode/slave/timeout/translation/permission fault 是否能区分 |
| trace | 是否能记录 request、grant、response、timeout/fault、completion 关键事件 |
| last progress | hang 后是否能知道最后一个 forward progress 事件 |
| classification | 观测是否能按 master、slave、ID、QoS、read/write 分类 |

## 验证层

| 检查项 | 要回答的问题 |
| --- | --- |
| protocol closure | VALID/READY、burst、ID、response 是否覆盖边界场景 |
| error injection | decode miss、slave error、timeout、fault 是否都可注入 |
| stress traffic | CPU/DMA/display/debug 混合流是否覆盖 |
| reset/power | reset 中访问、power off 访问、CDC reset mismatch 是否覆盖 |
| bridge corner | burst split、narrow transfer、WSTRB、attribute map 是否覆盖 |
| software sequences | descriptor/doorbell/completion/interrupt/clear 是否覆盖 |

## 一句话理解

BUS 设计检查的重点不是字段齐不齐，而是每条软件可见事务路径是否能完成、报错、恢复、观测和复盘。

## 建模启示

这份清单可以直接转成模型项：Resource 包括 master、slave、queue、slot、bridge、controller；Topology 包括 decode route、crossbar、bridge、CDC、return path；Interaction 包括 transaction、ordering、backpressure、completion、interrupt；Capability 包括 QoS、error/timeout、coherence、IOMMU、observability。

事件模型建议覆盖 `request_accept`、`decode_miss`、`arbiter_grant`、`backpressure_assert`、`bridge_convert`、`timeout_fire`、`fault_recorded`、`response_return`、`completion_visible`、`interrupt_clear_done`。设计评审时，每个事件都应能回答“谁产生、谁消费、失败怎么闭环”。
