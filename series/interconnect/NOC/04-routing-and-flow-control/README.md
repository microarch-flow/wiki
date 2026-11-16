# 04 路由、仲裁与服务保证

> 本页保留原章节入口。[查看现行分类与完整阅读顺序](../SUMMARY.md#04-routing-and-flow-control)。

<span id="04-routing-and-flow-control"></span><span id="这页在回答什么问题"></span>本章讨论包可以走哪里、共享资源先服务谁，以及在什么条件下能证明前进或服务。路由、逐跳流控、仲裁和 QoS 共同影响网络行为，但各自回答不同的问题。

<span id="这一章的主线"></span>路由定义合法路径或候选出口；Credit 等流控管理发送条件；仲裁选择共享资源的使用者；QoS 将需求映射到资源和服务。死锁安全、最终到达及有限延迟是不同性质，需要分别说明条件。

<span id="和前后章节的关系"></span><span id="为什么这一章对-ai-noc-很关键"></span>阅读前可回看[第二章的虚通道、Credit 和分配](../SUMMARY.md#02-router-microarchitecture)及[第三章拓扑](../SUMMARY.md#03-topology)。端点事务和地址映射属于第五章；编译器计划和调度属于第六章；性能测量与归因属于第八章。

## 本章入口

<span id="本章其余正文"></span>

1. [路由算法分类](./routing-algorithm-classes.md)：区分决策位置、路径范围和选择依据。
2. [维序路由](./dimension-order-routing.md)：用 XY/YX 建立固定路径和通道依赖的例子。
3. [死锁、活锁与饥饿](./deadlock-livelock-starvation.md)：区分不前进现象、等待状态和证明条件。
4. [Turn Model 与逃逸资源](./deadlock-avoidance-turn-model.md)：理解转向限制和逃逸资源的安全边界。
5. [自适应路由](./adaptive-routing-tradeoffs.md)：分析候选路径、观测信息和动态选择。
6. [Source Routing](./source-routing-for-deterministic-systems.md)：说明路径表达、执行和更新契约。
7. [仲裁策略](./arbitration-policies.md)：比较共享资源上的服务次序和公平性。
8. [QoS 与优先级](./qos-and-priority-classes.md)：从流量目标选择服务和隔离手段。
9. [端到端服务保证](./service-guarantees-and-latency-bounds.md)：给出带宽和延迟界的输入与服务条件。

<span id="读完这章后应该得到什么"></span><span id="建模启示"></span>分析一个网络时，分别记录合法路径、资源与等待、候选和实际授权、流量约束以及端点服务。路径确定、无路由死锁和有限完成时间不能相互替代。

<span id="一句话理解"></span>先定义路径和资源，再分析依赖、竞争与服务条件，才能判断网络如何前进。
