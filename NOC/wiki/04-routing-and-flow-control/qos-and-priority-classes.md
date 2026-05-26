# QoS And Priority Classes

上级：[04 Routing And Flow Control](./README.md)

相关：[Arbitration Policies](./arbitration-policies.md)、[Virtual Channel Fundamentals](../02-router-microarchitecture/virtual-channel-fundamentals.md)、[Multiple Physical Networks](../05-system-integration/multiple-physical-networks.md)、[BUS: 争用、QoS 与可观测性](/mnt/e/wiki/BUS/wiki/05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

这页回答：为什么 NoC 不能把所有 packet 当成同一类流量处理，以及 `QoS` 在片上网络里到底应该通过哪些抓手落地。

## QoS 不是“让所有流量都更快”

QoS 的本质是资源分配优先级。

它要解决的问题是：系统里不同流量的业务语义不同。

典型差异包括：

- control / sync：包很小，但极度怕延迟
- request / response：会直接影响上游 pipeline 是否停住
- bulk tensor data：更关注总吞吐
- background copy / prefetch：通常可以容忍更大等待

如果这些流量全部放在同一个 class、同一个 VC、同一套仲裁规则里，系统会表现得“平均上没问题，关键流量偶尔死得很难看”。

## QoS 最常见的实现抓手

### 1. Priority Class

最直观的做法是给不同 traffic class 不同优先级。

适合：

- barrier
- descriptor
- completion
- 小包控制消息

风险：

- 低优先级可能被持续压制

### 2. VC Separation

把不同 class 放到不同 VC。

价值：

- 减少 HOL blocking
- 避免 request/response/control 互相堵死
- 给后续仲裁和统计留出独立抓手

这往往是 QoS 的第一层基础，而不是附加优化。

### 3. Multiple Physical Networks / Planes

当 class 隔离要求很强时，单靠 VC 可能不够，系统会直接用多物理网络或多平面分离。

适合：

- control network 与 data network 分离
- read / write / reduction 分离
- latency-sensitive fabric 与 bulk fabric 分离

代价是面积和布线成本更高，但隔离效果最直观。

### 4. Reserved Share / Weighted Arbitration

对于不能完全优先级化的系统，可以按 class 保底份额。

它的好处是：

- 不会让低优完全饿死
- 能在实时流和吞吐流之间建立更稳的配比

## NoC 里的 QoS 比 BUS 更难

BUS 上很多 QoS 问题集中在少数共享点。NoC 则是一路上每个热点 router 都可能重新放大 class 差异。

这意味着：

- QoS 不是单点配置
- 同一 class 的保障要跨多跳保持一致
- 某个局部 router 的策略不合理，就可能毁掉整条路径的端到端体验

因此 NoC 的 QoS 设计一定要和 topology、routing、VC 组织一起看。

## 一个 deterministic NPU 的常见 class 划分

很常见的分层方式是：

- `control/sync`：最高优先级，小流量，要求低延迟
- `response/completion`：高优先级，避免上游等待链拉长
- `bulk stream`：中优先级，追求稳定吞吐
- `background/prefetch`：低优先级，可在压力下让路

重点不在名字，而在依赖链长度：

- 谁的延迟会直接卡 compute
- 谁的延迟只是影响总完工时间

这比单纯按 payload 大小分类更实用。

## QoS 的代价

QoS 并不免费。

你引入它之后，就要承担：

- 更多 class 状态
- 更复杂的仲裁和统计
- 更多 corner case
- 更难解释的性能分布

特别是 fixed-priority 风格的 QoS，很容易出现一个表面现象：

- 关键流量确实更快了
- 但低优流量尾延迟严重恶化
- 最后反过来影响系统级吞吐或 completion 时间

所以 QoS 设计不是“谁重要就一直压别人”，而是“哪些流必须被保护，保护到什么程度为止”。

## 什么时候 VC 不够、必须上多网络

当下面几种情况出现时，通常说明仅靠 VC 隔离已接近极限：

- 某类流量必须获得非常强的 latency bound
- 大流量持续占用物理链路，VC 只能排队，无法真正隔离带宽
- 不同 class 的 burst 结构和方向性差异极大
- debug 与验证需要非常清楚的因果边界

这时把 control/data 或 read/write 物理分离，往往比继续堆 QoS 规则更干净。

## 常见误区

- 认为 QoS 就是 fixed priority
- 认为有了 VC 就自动有 QoS
- 认为优先级只影响性能，不影响 forward progress

更准确的说法是：

- QoS 是一组资源分配与隔离机制，不是单一策略
- VC 是 QoS 的重要抓手，但不等于完整 QoS
- 如果某类流量长期拿不到服务，系统级依赖链会把问题放大成 hang 或超时

## 一句话理解

QoS 的任务不是让网络“整体更快”，而是让不同语义的流量在同一网络里按系统目标获得不同程度的保护和让步。

## 建模启示

建模 QoS 时，最重要的是先定义 traffic class，而不是先挑仲裁器名字。模型至少要有：

- class 标签
- class 对应 VC 或物理网络映射
- class-specific arbitration rule
- class-specific latency / throughput objective

输出结果不能只看总平均值，还要按 class 看：

- latency distribution
- starvation risk
- bandwidth share
- completion criticality

否则“总吞吐没问题”会掩盖“control path 已经不稳定”的事实。
