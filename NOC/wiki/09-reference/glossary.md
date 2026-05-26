# Glossary

上级：[09 Reference](./README.md)

相关：[Taxonomy](../01-overview/taxonomy.md)、[Router Microarchitecture](../02-router-microarchitecture/README.md)

## 这页在回答什么问题

这页回答：整套 NoC wiki 里最常用的术语到底各自指什么，哪些词彼此容易混淆，边界应该怎样划。

## 核心术语

### `packet / flit / phit`

- `packet`：协议和事务层面的完整传输单元
- `flit`：网络内部被 flow control 管理的最小推进单元
- `phit`：物理链路一个传输拍真正承载的位宽单位

最容易错的是把三者都当成“包”。更准确地说：packet 被切成 flit，flit 再映射到 phit 过物理链路。

### `wormhole`

header 先开路，body/tail 跟随，占用沿途资源直到 tail 释放。

它的核心后果是：buffer 可以浅，但 backpressure 和 path coupling 会被放大。

### `credit`

下游告诉上游“我还有多少 buffer slot 可接收”的计数。

它防的是 overflow，不自动防 deadlock。

### `VC`

`virtual channel`，共享同一物理链路但在缓冲与资源上部分隔离的逻辑通道。

它常见作用包括：

- 减少 HOL blocking
- message class 隔离
- deadlock avoidance 工具
- QoS 抓手

### `routing`

决定 packet 合法走哪些路径，或者下一跳候选是什么。

它不是仲裁。routing 选的是路，arbitration 选的是谁先上路。

### `arbitration`

多个候选竞争同一资源时，决定本拍谁获得服务的机制。

典型资源包括：

- output port
- output VC
- injection slot
- ejection slot

### `QoS`

按 traffic class 改变资源分配顺序或隔离方式的机制。

它不是“让所有流量都更快”，而是让不同语义的流量按系统目标受不同保护。

### `deterministic routing`

给定 `src-dst`，路径规则固定，可预测。

### `source routing`

路径由源端、编译器或 runtime 预先指定，而不是每跳本地临场决定。

### `adaptive routing`

路径选择依赖实时状态，例如局部拥塞或 credit。

### `deadlock / livelock / starvation`

- `deadlock`：互相等待，系统永久不前进
- `livelock`：一直在动，但某些 packet 长期不收敛
- `starvation`：有路也有系统活动，但你长期抢不到服务

### `injection / ejection`

- `injection`：endpoint 把流量送入 NoC
- `ejection`：NoC 把流量交给目的端

`ejection` 慢时，常常会被误判成“网络堵了”，其实根因可能在 endpoint / local SRAM。

### `memory-centric`

系统主要受 memory request/response 路径支配，而不是纯 tile-to-tile forwarding。

### `collective`

不是普通 point-to-point，而是：

- one-to-many
- many-to-one
- many-to-many

典型包括 broadcast、reduce、all-reduce、all-to-all。

## 最容易混淆的几组词

### routing vs arbitration

- routing 决定允许走哪条路
- arbitration 决定多人争同一路时谁先过

### flow control vs deadlock avoidance

- flow control 解决“不发爆下游”
- deadlock avoidance 解决“别形成循环等待”

### throughput vs utilization

- throughput 是完成了多少有效传输
- utilization 是资源忙了多久

高 utilization 不一定高 throughput。

### network bottleneck vs endpoint bottleneck

- network bottleneck：链路 / router / arbitration 主导
- endpoint bottleneck：NI / ejection / local SRAM / memory port 主导

## 一句话理解

术语表的价值不在于定义本身，而在于防止不同章节里的同一个词被悄悄换了口径。

## 建模启示

如果你后面继续做 DSL、simulator 或 case card，优先复用这里的术语口径。尤其是：

- traffic class
- stall reason
- routing / arbitration / QoS
- endpoint / memory-centric

这些词一旦口径漂移，后面的结果会很难横向比较。
