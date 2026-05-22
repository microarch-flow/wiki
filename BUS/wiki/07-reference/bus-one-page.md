# BUS 一页版总览

上级：[07 术语与检查清单](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[事务、地址、数据与响应](../02-fundamentals/transaction-address-data-response.md)、[CPU、DMA、外设与内存之间的总线路径](../04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)

## BUS 是什么

BUS 是片上事务互连层。它把 CPU、DMA、memory、peripheral、accelerator、debug master 放进同一套访问规则：地址如何 decode，请求如何仲裁，数据如何传输，response 如何返回，错误如何闭环，下游变慢时回压如何传播。

BUS 不等于一根共享线。shared bus、bus matrix、crossbar、分层互连、bridge 组合都可以是 BUS 的具体组织方式。

## BUS 要回答的设计问题

| 问题 | 对应机制 |
| --- | --- |
| 谁可以访问谁 | address map、decoder、firewall、permission |
| 谁先走 | arbitration、QoS、priority、fairness |
| 事务如何完成 | response、completion、error、timeout |
| 下游慢时怎么办 | backpressure、FIFO、buffer、retry、timeout |
| 软件何时能相信结果 | cacheability、barrier、coherence、interrupt/status |
| 不同协议/时钟/位宽如何相连 | bridge、CDC、width adapter |

## 核心对象

| 对象 | 要点 |
| --- | --- |
| transaction | 一次访问从 request 到 response/error 的闭环 |
| address | 决定目标、权限、属性和错误路径 |
| data | 可能按 beat、byte lane、WSTRB、burst 组织 |
| response | 释放 outstanding/slot 的关键 |
| arbitration | 把并发请求压成可执行顺序 |
| ordering | 决定哪些访问不能交换可见顺序 |
| backpressure | 下游容量不足向上游传播的机制 |
| bridge | 改变协议、时钟、位宽、burst、错误语义 |

## 协议定位

| 协议 | 更适合的角色 |
| --- | --- |
| APB | 低速寄存器、外设、简单 MMIO |
| AHB/AHB-Lite | 中等复杂度主干或子系统互连 |
| AXI | 高性能、多 channel、outstanding、burst、异构 IP 接口 |
| TileLink | 参数化 SoC 生态中的事务与一致性框架 |

协议名不是行为结论。AXI 路径也可能被 bridge、slave slot、return path 限制；APB 路径也可能因为 clear/status 顺序影响软件正确性。

## 系统分工

| 系统对象 | BUS 视角 |
| --- | --- |
| CPU | 发起 memory/MMIO，受 cache、barrier、exception 影响 |
| DMA | 把 descriptor/data/writeback 组织成 BUS 事务 |
| DDR controller | 把 AXI request 重新调度成受 row/bank/timing 约束的命令 |
| IOMMU/SMMU | 在 DMA path 上加入身份、翻译、权限和 fault |
| Interrupt | 依赖 MMIO status、completion、clear/EOI 闭环 |
| NoC | 承担大规模数据网络时，BUS 仍保留控制语义和管理边界 |

## 性能问题优先看什么

| 现象 | 优先检查 |
| --- | --- |
| 带宽低 | payload、burst、outstanding、target service time |
| tail latency 高 | arbitration wait、write drain、return path、QoS |
| master 发不出 | upstream slot、READY、input FIFO、outstanding 上限 |
| response 不回来 | slave、bridge、return FIFO、ID matching |
| completion 慢 | writeback path、cache visibility、interrupt latency |

不要只看总带宽。要同时看 latency histogram、queue occupancy、arbiter wait、response wait、completion latency。

## 正确性问题优先看什么

| 现象 | 优先检查 |
| --- | --- |
| MMIO 读卡住 | decode、clock/reset/power、PREADY、timeout/error |
| DMA 读旧 descriptor | cache clean、barrier、IOMMU mapping |
| completion 丢失 | writeback、coherence/invalidate、interrupt ordering |
| IOMMU fault | stream/context、IOVA、permission、子事务阶段 |
| fault/hang 混淆 | 是否有 response、fault record、timeout wrapper、resource release |

## 调试路径

1. 先分清是 timeout、fault 还是 hang。
2. 再分清 request 没发出、target 没接收、response 没返回，还是 completion 没对软件可见。
3. 看 counter/trace：request accept、queue high watermark、arbiter grant、response return、timeout/fault、completion visible。
4. 打开 AXI 波形时，先分读写，再标 `VALID && READY`，最后用 ID/outstanding ledger 闭环 transaction。

## 一句话结论

BUS 不是线网细节，而是把协议语义、系统集成、性能瓶颈、错误闭环和软件可见性串在一起的片上基础设施。

## 建模启示

建模 BUS 时至少要有这些状态变量：master/slave、address window、transaction ID、outstanding、queue depth、arbiter wait、backpressure、bridge conversion、response path、error/timeout、cacheability/barrier、completion/interrupt。

事件模型建议显式表达 `request_accept`、`decode_done`、`arbiter_grant`、`fifo_push/pop`、`bridge_convert`、`response_return`、`fault_recorded`、`timeout_fire`、`completion_visible`、`interrupt_clear_done`。这些事件是整套 BUS wiki 的最小公共语言。
