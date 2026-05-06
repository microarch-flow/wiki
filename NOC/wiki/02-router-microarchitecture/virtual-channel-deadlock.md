# VC / Deadlock

上级：[Router 微架构](./README.md)

相关：[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)、[检查清单](../06-reference/checklists.md)

## 为什么 VC 不是“可有可无的高级功能”

没有 VC 时，多个 packet 共用一个物理队列。  
只要队头 packet 卡住，后面的 packet 即使目的地完全不同，也可能被一并堵住，这就是典型的 `head-of-line blocking`。

## VC 的四个核心作用

### 1. 降低 HOL blocking

通过把不同 packet 放进不同逻辑队列，减少错误耦合。

### 2. 隔离 message class

例如：

- request
- response
- control
- stream / bulk data

如果这些流量共池，系统很容易出现“小消息被大流量淹没”的问题。

### 3. 为 QoS 提供抓手

控制面、同步消息、低延迟请求，往往需要和 bulk data 分离。

### 4. 降低 deadlock 风险

VC 不是自动防死锁，但它给你提供了协议分层和资源依赖切断的工具。

## Deadlock 的本质

deadlock 不是“堵了一会儿”，而是资源依赖形成了环：

- 每个 packet 都持有一部分资源
- 同时等待别的 packet 释放资源
- 整个系统进入无前进状态

## 两类你必须区分的 deadlock

### Routing deadlock

由路径资源依赖环导致。  
常见解决方式：

- dimension-order routing
- turn model
- escape VC

### Protocol deadlock

由 request / response / control 等不同事务类相互等待导致。  
常见解决方式：

- request / response 分离
- control plane 独立
- 避免“响应需要等待请求释放资源”的循环依赖

## AI NoC 中最常见的错误理解

- 认为 credit 能防死锁
- 认为 VC 数量越多越好
- 认为没有一致性协议就不会有 protocol deadlock

实际情况是：

- credit 只能防 overflow
- VC 太多会增加面积、状态和仲裁复杂度
- AI NoC 同样可能因 DMA response、control、reduce 或 ejection 阻塞而形成协议级依赖环

## 对 AI Dataflow NoC 的实用建议

第一版建模时，可以先采用简单但稳妥的分层：

- control plane
- memory request plane
- memory response / data plane
- stream plane

如果实现成本有限，至少先保证：

- control 不被 bulk data 长时间压住
- request 和 response 不共用一个容易相互堵塞的资源池

## 建模时需要显式记录的状态

- 每个 input VC 的 occupancy
- VC allocation 状态
- packet 当前占用的下游资源
- 各 message class 的通路关系
- 是否存在循环等待路径

## 本页结论

VC 的本质不是“把链路切成几份”，而是给 NoC 提供资源隔离与协议组织能力。  
做架构探索时，如果不显式处理 VC 和 deadlock，你得到的很多吞吐结论都不够可信。
