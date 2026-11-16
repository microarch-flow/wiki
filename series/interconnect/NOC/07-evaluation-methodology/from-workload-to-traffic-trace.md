# 从工作负载到流量 Trace：事件和依赖怎样生成？

<span id="from-workload-to-traffic-trace"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[07 Evaluation Methodology](./README.md)

相关：[流量模式与表征](../05-system-integration/traffic-patterns-and-characterization.md)、[Trace 生成与核算实作](./trace-generation-worked-example.md)、[流量注入与 Trace](../08-simulator-construction/traffic-injection-and-tracing.md)

工作负载描述要完成的任务；Trace 描述模型需要处理的事件。要从前者得到后者，必须先给出任务切分、数据位置、通信语义和依赖。仅凭算子名称不能确定流量。

## 从任务到事件

1. 划分计算任务，写出生产者、消费者和依赖。
2. 将任务与数据映射到端点，标明本地存储及外部存储位置。
3. 为跨位置的数据需求生成 flow；区分本地交付、单播和多目的交付。
4. 定义释放与完成事件，再按具体包格式分包。
5. 检查事件依赖、每个目的端和资源口径，最后交给相应模型。

## 输入、输出与完成边界

本章示例使用 `noc-workload-v1`。每个事件有唯一字符串 `id`、非负整数 `release_time` 和前驱 ID 数组 `depends_on`。前驱按 all-of 解释：所有指定前驱完成，且释放时间已到，事件才可执行。

| 事件 | 额外字段 | 此示例的完成条件 |
| --- | --- | --- |
| `flow` | `src_node`、`dst_set`、`traffic_class`、`payload_bytes` | 所有目的 consumer 接收所需数据；本地目的也要交付。 |
| `compute` | `node`、`duration_cycles` | 模型规定的计算时长结束。 |
| `barrier` | 无端点字段 | 所有前驱完成。 |

`dst_set` 始终是数组，单播也只有一个元素。`phase` 可选。加载器应拒绝重复 ID、非法节点、未知 class、无效时间、缺失前驱和依赖环。合法性检查与性能仿真是不同工作。

多目的 flow 的 all-consumer 完成是**这个 schema 的规则**。若每个消费者拿到自己的数据后就能独立计算，需要表示逐目的完成事件；不能只把现有整组完成事件当作逐目的事件。改变 schema 及其模拟器接口需要同时更新消费者，不能悄悄改变 v1 含义。

第九章的基线网络内核只支持单播。多目的 flow 若展开为多份单播，应按各份路径重新统计注入和 byte-hop；共享树需要额外实现复制和完成状态。[注入与分包](../08-simulator-construction/traffic-injection-and-tracing.md)说明接口边界。

## 固定时间与依赖驱动

固定时间 Trace 给每个事件预定释放时刻，适合对候选网络施加相同输入。但实际工作负载可能等待前一条响应，网络变慢会影响后续释放。依赖驱动 Trace 显式保存这些依赖，模型可按前驱完成推进；它仍只覆盖 Trace 中记录的依赖和端点行为，不自动等同完整系统。

[Netrace 原论文](https://www.research.ed.ac.uk/en/publications/netrace-dependency-driven-trace-based-network-on-chip-simulation/)展示了在 NoC Trace 中保留消息依赖的方法。选择哪种输入，要看实验目标并记录未表示的反馈。

## 可执行的 GEMM 生成器

4×4 tile 的示例生成 32 个输入 flow、64 个 compute、3 个阶段 barrier 和 16 个写回 flow。输入块按行或列交付，所有 K 步之间使用全局 barrier；每个 compute 的 `duration_cycles=1` 只是示例值，不是 GEMM 性能测量。

完整代码、字段检查和共享树／单播的独立计数见[Trace 生成与核算实作](./trace-generation-worked-example.md)。本页保留该入口；复制代码或运行检查应使用实作篇的完整版本。

## 可手算的 prefill 小 trace

batch=1、4 token、1 head、head dimension=4，Q/K/V 使用 FP16。两个相邻 tile 各持 2 token 的 Q/K/V；本例假设双方交换本地 K/V，每方向合并为一个 32 B payload packet。每 packet header 为 16 B，flit 为 16 B，因此每方向是 3 flit，双方共发送 64 B payload 和 96 B wire 数据。

采用[第九章快照契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)：两个方向独立，每方向每拍最多发 1 flit；源 input FIFO 在 S(0) 已装下完整 packet，credit 和目的端容量充足，forward latency 为 1，无其他流量。各方向在 t=0、1、2 发送；tail 在 t=3 拍末进入下游 FIFO，t=4 弹出，t=5 被 consumer 消费。完成时间戳为 t=5；若把 t=0 到 t=5 两端都计作离散周期，则为 6 cycle。

这是双方都需要对方 K/V 的例子。因果掩码下可能只需要一个方向，见[Prefill 案例](../06-ai-noc-specifics/workload-attention-prefill.md#同一个分块两种掩码)。

## AllReduce 的量纲检查

若 8 个端点各有 100 MiB，采用无竞争单向逻辑 Ring，均匀分片、每阶段顺序执行、端点可同时收发，每个端点发送 1.75×100 MiB，所有端点共注入 **1,468,006,400 B payload**。若每阶段固定项为 10 cycle、有效带宽为 64 B/cycle，且忽略归约计算、包头和竞争，估算为 **2,867,340 cycle**。完整前提和其他算法的比较见[AllReduce 理想模型](../06-ai-noc-specifics/reduction-and-collective-networks.md#带明确前提的-allreduce-模型)。

## 复核方法

分别核对事件和前驱、每个目的的交付、payload 与 packet 格式，再沿实际路径累计各条链路。byte-hop 使用 B·hop，不能当作注入字节或完成时间。保留输入版本、简化项和未完成任务；只有再定义资源、仲裁与时间，才能通过模型研究完成时间。
