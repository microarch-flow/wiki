# 04 Routing And Flow Control

上级：[NOC Wiki](../README.md)

相关：[Router Microarchitecture](../02-router-microarchitecture/README.md)、[Topology](../03-topology/README.md)、[System Integration](../05-system-integration/README.md)、[BUS: 仲裁、顺序性与 Backpressure](/mnt/e/wiki/BUS/wiki/02-fundamentals/arbitration-ordering-backpressure.md)

## 这页在回答什么问题

这一章回答三个经常被混在一起的问题：

- packet 该走哪条路径
- 多个竞争者同时要同一资源时谁先过
- 系统怎样保证不会因为资源依赖环而永久卡死

前一章的 `topology` 讨论的是“网络长什么样”，这一章讨论的是“同一张网络如何运行”。在 mesh 上跑 XY、West-First、source routing、fully adaptive，看起来都还是同一个 mesh，但延迟分布、热点位置、验证难度和死锁处理空间都完全不同。

## 这一章的主线

这里把几个概念拆开：

- `routing`：决定下一跳候选集合
- `flow control`：决定在下游没空位时能不能继续发送
- `arbitration`：决定多个候选里谁拿到端口、VC 或注入口
- `deadlock avoidance`：限制资源获取顺序，保证 forward progress
- `QoS`：按 traffic class 改变服务顺序或隔离方式

这几个机制会同时作用在同一个 packet 身上，但它们不是同一件事。比如：

- XY routing 解决的是路径选择，不自动解决 request/response 协议依赖
- credit-based flow control 防止 buffer overflow，不自动防 deadlock
- fixed-priority arbitration 可以让 control traffic 更快，不自动减少总拥塞

## 为什么这一章对 AI NoC 很关键

AI/NPU 设计通常不是在追求“任意流量下都很灵活”，而是在追求：

- 主数据流可预测
- 编译器可控
- tail latency 有上界
- 系统容易验证

这会直接影响 routing 选择。很多 deterministic NPU 的主路径不会优先上 fully adaptive routing，而是更偏向：

- dimension-order routing
- source routing
- 受限 turn model
- traffic class 隔离
- 多平面或多物理网络分离

原因不是“老旧”，而是可验证性和性能稳定性比理论 path diversity 更重要。

## 和前后章节的关系

- 如果你还没统一 `VC`、`credit`、`allocator` 的概念，先回看 [virtual-channel-fundamentals](../02-router-microarchitecture/virtual-channel-fundamentals.md)、[allocator-design-vc-switch](../02-router-microarchitecture/allocator-design-vc-switch.md)、[credit-based-flow-control](../02-router-microarchitecture/credit-based-flow-control.md)。
- 如果你还没统一 mesh、ring、fat-tree、concentrated mesh 的结构差异，先回看 [03 Topology](../03-topology/README.md)。
- 如果你关心的是主机接口、DMA、memory system、multiple networks，那么这一章只是底层规则，系统级组织放在 [05 System Integration](../05-system-integration/README.md)。

## 读完这章后应该得到什么

读完后，你应该能独立回答这些问题：

- 为什么 XY routing 能防某类 deadlock
- 为什么 source routing 不等于不需要 VC
- 为什么 adaptive routing 的收益取决于 path diversity 和 traffic unpredictability
- 为什么 fixed-priority 能解决一部分 latency 问题，但也可能制造 starvation
- 为什么 request/response/control/bulk data 需要分 message class
- 为什么 credit stall、switch stall、protocol wait 不是同一种 stall

## 一句话理解

`topology` 决定“路网长什么样”，`routing + flow control + arbitration + QoS` 决定“同一张路网里的车到底怎么跑、为什么会堵、怎样保证最终能到”。

## 建模启示

这一章对应的模型，至少要显式保留四层状态：

- 路径层：每个 packet 当前可选的 next hop 集合
- 资源层：每个 input VC、output port、credit、injection slot 的占用状态
- 策略层：仲裁规则、QoS class、priority/aging 规则
- 安全层：deadlock avoidance 约束、escape VC、message class 依赖约束

如果模型里只有“hop 数”和“链路带宽”，你会看不到：

- 为什么某些流量一直走同一热点链路
- 为什么平均负载不高但 tail latency 很差
- 为什么系统不是拥塞，而是不前进
