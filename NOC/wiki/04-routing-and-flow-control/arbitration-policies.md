# Arbitration Policies

上级：[04 Routing And Flow Control](./README.md)

相关：[Allocator Design VC Switch](../02-router-microarchitecture/allocator-design-vc-switch.md)、[QoS And Priority Classes](./qos-and-priority-classes.md)、[BUS: 争用、QoS 与可观测性](/mnt/e/wiki/BUS/wiki/05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

这页回答：即使路径已经确定，为什么 packet 还是会卡住，以及不同仲裁策略到底在交换什么。

## 仲裁发生在哪里

在 NoC 里，仲裁不是只发生在一个“总线入口”，而是分散在多个资源点：

- input VC 争抢 output VC
- 多个 input 争抢同一 output port
- 多个源端争抢 injection slot
- 多个 packet 争抢 ejection 或 endpoint receive buffer

所以仲裁是 NoC 每一跳都可能发生的局部调度问题，而不是一次性全局决定。

## 仲裁解决的不是路径问题

要先把两件事分开：

- routing：决定有哪些合法出口候选
- arbitration：在多个候选者同时看上同一个出口时，谁这拍先拿到

很多 stall 并不是“路选错了”，而只是“大家都要同一个口，你这次没赢”。

## 常见策略

### Round-Robin

轮询是最常见默认值。

优点：

- 简单
- 公平性较好
- 不容易长期饿死某一路

缺点：

- 对 latency-sensitive control traffic 不够激进
- 在高负载下 tail latency 不一定最优

### Fixed Priority

固定优先级适合把 control、sync、response 这类小而关键的流量放在前面。

优点：

- 关键流量延迟低
- 行为直观

缺点：

- 低优先级可能被长期压制
- 如果 bulk data 持续注入，低优 starvation 风险会很真实

### Age-Based

谁等得久，谁优先。

优点：

- 可以显著改善 tail latency
- 对避免饥饿有效

缺点：

- 需要额外 age 状态
- 实现与验证成本更高

### Weighted / QoS-Aware

不同 class 拿不同份额或不同优先级。

优点：

- 能表达服务等级
- 更适合多类混合流量系统

缺点：

- 参数配置复杂
- 不容易直观看出最终等待分布

## 为什么仲裁策略在 AI 芯片里很敏感

因为 AI NoC 往往同时存在两类完全不同的流量：

- 大量、连续、占带宽的 bulk data
- 很小、但延迟极敏感的 control/sync/response

如果全都用一种完全公平的策略，control 可能被大流淹没。
如果全都用高优先级压制，bulk data 又可能失去吞吐稳定性。

所以这里真正要设计的不是“公平不公平”，而是“哪些 class 需要更低延迟，哪些 class 只要不饿死就行”。

## 仲裁策略和 topology 会耦合

在 ring、tree、mesh 这类网络里，热点位置不同，仲裁策略的可见效果也不同。

例如：

- 在中心热点明显的 mesh 中，局部 output arbiter 的策略会强烈影响 tail latency
- 在树形汇聚点上，reduce 流量更容易形成上行集中争用
- 在多 memory port 结构里，某些靠近 memory 的 router 会天然承担更重的仲裁压力

因此仲裁策略不能脱离 traffic map 讨论。

## 它和 HOL blocking 的关系

仲裁不当会放大 HOL blocking，但两者不是一回事。

- HOL blocking 说的是：前面的 packet 卡住，后面的 packet 即使目标不同也跟着卡
- 仲裁说的是：当多个候选都可前进时，谁先拿资源

VC 能缓解前者，合适的 arbitration policy 影响后者。很多系统问题是这两者叠加出来的。

## 一个实用的混合原则

对 deterministic NPU，常见的保守做法是：

- class 间：用 priority 或 reserved share
- class 内：用 round-robin 或 age-based

这样可以同时得到：

- 关键流量的低延迟
- 同类流之间较稳定的公平性

比“全局固定优先级压到底”更可控。

## 常见误区

- 认为轮询就一定最好，因为最公平
- 认为 fixed priority 只影响性能，不影响正确性
- 认为 routing 选好了，仲裁就只是实现细节

更准确的看法是：

- 公平不等于满足系统目标
- 低优先级长期拿不到服务，可能让软件等待 completion，进而形成系统级 hang
- routing 决定你会在哪些点争用，arbitration 决定争用结果的时间分布

## 一句话理解

仲裁策略决定的不是“路怎么走”，而是“多个包都想走同一条路时，谁先动、谁等多久、谁有没有可能一直等下去”。

## 建模启示

建模 NoC arbitration 时，至少要显式表示：

- arbitration point 的位置：VC allocation、switch allocation、injection、ejection
- 候选队列的组织方式
- class / priority / age 等调度属性
- starvation bound 或 aging 机制

对性能分析，单看平均 grant rate 不够，还要看：

- per-class wait time
- 99th percentile wait
- starvation event
- 与 credit stall、route restriction 的叠加关系

否则你会把“没抢到资源”和“根本无路可走”混成同一种 stall。
