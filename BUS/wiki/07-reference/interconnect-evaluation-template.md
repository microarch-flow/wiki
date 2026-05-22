# 互连方案评估模板

上级：[07 术语与检查清单](./README.md)

相关：[BUS 设计检查清单](./bus-design-checklist.md)、[MCU / SoC / AI 芯片中的 BUS 对照](../06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)、[Shared Bus、Bus Matrix 与 Crossbar](../04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)

## 使用方式

这个模板用于评估 shared bus、bus matrix、crossbar、NoC 边界、AXI/AHB/APB/TileLink 组合或厂内 fabric 方案。重点不是写出“方案 A 更快”，而是把场景、Resource、Topology、Interaction、Capability、性能风险和集成风险放在同一张表里比较。

## 推荐模板

```md
# 方案名称

## 1. 场景定位

- 面向系统：MCU / 通用 SoC / AI 芯片 / 子系统 / 控制岛
- 主要 workload：
- 控制面 / 数据面 / completion path / debug path：
- 关键软件流程：
- 关键失败模式：timeout / fault / hang / missing completion / tail latency

## 2. Resource

| Resource | 数量 / 类型 | 是否共享 | 风险 |
| --- | --- | --- | --- |
| master / initiator |  |  |  |
| slave / target |  |  |  |
| queue / FIFO / buffer |  |  |  |
| ID / source / slot |  |  |  |
| bridge / adapter |  |  |  |
| controller / SMMU / debug |  |  |  |

## 3. Topology

- 拓扑类型：shared bus / bus matrix / crossbar / NoC / hybrid
- 是否分层：
- 是否全连接：
- 哪些路径被裁剪：
- 哪些路径经过 bridge / CDC / width adapter：
- request path：
- response path：
- completion / interrupt path：

## 4. Interaction

- transaction 类型：read / write / burst / MMIO / DMA / debug
- read/write 是否分离：
- outstanding 上限：
- ordering 规则：
- backpressure 传播路径：
- error / timeout / fault 如何返回：
- software-visible completion 如何形成：

## 5. Capability

| 能力 | 是否需要 | 方案支持方式 | 风险 |
| --- | --- | --- | --- |
| QoS / priority |  |  |  |
| burst / narrow transfer |  |  |  |
| cacheability / attributes |  |  |  |
| IOMMU / SMMU |  |  |  |
| debug / boot / low power |  |  |  |
| observability |  |  |  |
| error recovery |  |  |  |

## 6. 性能判断

- 理论带宽上限：
- 关键 master 的 latency 预算：
- 热点 slave / controller：
- read/write 混合风险：
- response path 风险：
- completion latency 风险：
- tail latency 风险：
- 需要的 counter / trace：

## 7. 集成判断

- software model：
- MMIO side effect：
- DMA descriptor/data/writeback：
- DDR controller 接入：
- IOMMU/SMMU fault 路径：
- boot/debug/low-power 状态：
- 安全和权限边界：

## 8. 验证计划

- protocol compliance：
- stress traffic：
- error injection：
- timeout/fault/hang：
- reset/power/CDC：
- software sequence：

## 9. 最适合的场景

-

## 10. 最大风险

-

## 11. 决策结论

- 推荐 / 不推荐 / 有条件推荐：
- 前置条件：
- 必须补的观测点或保护机制：
```

## 评估原则

| 原则 | 解释 |
| --- | --- |
| 先场景后协议 | 同一协议在不同系统中可能承担完全不同角色 |
| 先闭环后性能 | transaction、error、timeout、completion 必须先能闭环 |
| request 和 response 分开评估 | response path 更容易被低估 |
| data done 和 software done 分开评估 | completion/writeback/interrupt 是独立路径 |
| 平均值和尾延迟分开评估 | p99/max 才能暴露短时拥塞 |
| 性能和观测点一起评估 | 没有观测点，性能结论无法复盘 |

## 一句话理解

互连方案评估不是协议选型表，而是把场景需求映射到 Resource、Topology、Interaction、Capability，再判断性能、正确性和可调试性是否闭环。

## 建模启示

这个模板可以直接变成模型 schema。Resource 是节点和容量，Topology 是路径和共享点，Interaction 是事务和顺序，Capability 是系统语义和保护能力。每个候选方案都应能生成同一组事件：`request_accept`、`route_select`、`arbiter_grant`、`bridge_convert`、`response_return`、`completion_visible`、`timeout_fire`、`fault_recorded`、`debug_snapshot`。

若某个方案无法回答这些事件在哪里发生、如何观测、失败后如何释放资源，就说明它还没有达到可集成方案的最低描述质量。
