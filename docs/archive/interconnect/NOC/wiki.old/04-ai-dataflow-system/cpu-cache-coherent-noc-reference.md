# CPU/Cache Coherent NoC 对照专题

上级：[AI Dataflow 系统视角](./README.md)

相关：[AI Dataflow NoC vs CPU Coherent NoC](./ai-vs-cpu-noc.md)、[VC / Deadlock](../02-router-microarchitecture/virtual-channel-deadlock.md)

## 为什么这页值得单独存在

你的主线是 AI tile（计算单元）dataflow NoC，但 CPU/cache coherent NoC（缓存一致性片上网络）仍然很有参考价值。  
它最大的价值不在于让你照搬 CPU 设计，而在于让你看到：

- 为什么 request / response / snoop（窥探）必须隔离
- 为什么 VN（虚网络）/ VC（虚通道）在协议正确性里这么关键
- 为什么“能跑通”不等于“协议安全”

## CPU coherent NoC 在解决什么

它的核心目标通常是：

- 支撑共享地址空间
- 处理 cache miss（缓存未命中）
- 支撑 coherence transaction（一致性事务）
- 保证 ordering（排序）、atomicity（原子性）和 forward progress（前进保证）

典型事务不只是“拿数据”，而是整套状态变化链条。

## 一次 cache miss 可能触发什么

一个简化链条可能包括：

1. core 发出 read miss request
2. request 到达 home agent / LLC
3. home 发起 snoop（窥探请求）或目录查询
4. owner cache 或 memory 返回 data response
5. invalidate / ack 或状态更新完成

所以 coherent NoC 天然就是多类消息并存。

## 典型 message class

至少要区分：

- request
- response
- snoop
- invalidate（无效化）/ ack（确认）
- writeback（回写）

这些类之间往往存在强协议依赖。

## 为什么 VN / VC 在 coherent NoC 里更“硬约束”

AI NoC 里，VC 很多时候是为了：

- 避免 HOL blocking（队头阻塞）
- 分 traffic class（流量类别）
- 做 QoS（服务质量）

而 coherent NoC 里，VN / VC 往往还承担：

- 避免 request / response 资源环
- 支撑协议级 forward progress
- 保证某些 ordering 语义

也就是说，在 coherent NoC 里，VC 不是“优化项”，往往是协议安全的一部分。

## Ordering 是什么问题

CPU coherent NoC 不是只要“最终到达”就行，还要关心：

- 同一 core 发出的请求是否要保序
- response 是否可能乱序到达
- invalidate / ack 是否会改变可见顺序
- memory consistency model 如何被实现支持

这使它比 AI dataflow NoC 更偏事务语义网络，而不是纯数据搬运网络。

## Protocol deadlock（协议死锁）为什么在这里更典型

一个常见风险是：

- request 占用资源等 response
- response 又被 request 或 snoop 阻塞
- 整套事务链条形成协议级循环等待

这也是 coherent NoC 常常强调：

- message class 分离
- request / response plane 分离
- escape path（逃逸路径）

## 对 AI NoC 的真正启发

你不需要把完整 coherence 搬进 AI NoC，但应吸取几条经验：

- 不同语义的消息不要轻易共池
- response path 往往比 request path 更敏感
- forward progress 要显式设计，不能靠“应该能跑”
- VC / plane 的划分应服务协议依赖图，而不只是吞吐

## 什么内容你现在不必深挖

如果你当前目标是 AI NoC 建模，可以暂时不深入：

- MOESI / MESIF（缓存一致性协议状态机）具体状态机
- memory consistency（内存一致性）模型细节
- cache hierarchy 所有 corner case

你需要掌握的是 NoC 视角下的抽象，不是完整 CPU 协议验证。

## 一个对照式学习方法

把下面两组问题并排看最有价值：

- AI NoC：为什么要分 control / response / bulk stream
- CPU NoC：为什么要分 request / response / snoop

前者让你看到系统吞吐问题，后者让你看到协议安全问题。

## 本页结论

CPU/cache coherent NoC 最值得你借鉴的，不是具体 cache 协议，而是“消息语义分层、资源依赖控制和 forward progress 设计”这套思维方式。  
这会帮助你把 AI NoC 做得更稳，而不是更像 CPU NoC。
