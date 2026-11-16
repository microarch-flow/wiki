# 流量模式与表征：网络实际收到什么？

<span id="traffic-patterns-and-characterization"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[05 System Integration](./README.md)

相关：[工作负载与 NoC 流量](../06-ai-noc-specifics/why-ai-noc-is-different.md)、[All-to-All 与通信矩阵](../06-ai-noc-specifics/all-to-all-and-traffic-matrix.md)、[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)

<span id="这页在回答什么问题"></span><span id="traffic-不是一个数字"></span>流量表征要回答：谁在什么时候向谁发送多少数据，以及发送和接收受什么条件约束。同样的平均速率，可以对应不同的目的分布、突发和等待。

## 描述空间、时间和完成条件

<span id="characterization-至少要记录什么"></span>先选择观察边界：统计源端生成、成功注入，还是目的端消费。然后记录：

| 维度 | 需要说明的内容 |
| --- | --- |
| 空间 | 源、目的集合和各端点位置；本地交付是否入网。 |
| 时间 | 释放时刻、到达间隔、观察窗口、阶段及突发。 |
| 大小与语义 | payload、分包、单播或多目的交付，是否有请求和响应。 |
| 依赖与服务 | 何时允许发送、接收端能否消费，以及前驱的完成事件。 |
| 类别 | 流量类别及其如何映射到实际队列和仲裁资源。 |

<span id="一个更有用的分类法"></span>单播流、相同数据的多目的分发、归约，以及请求／响应有不同语义。同一条流也可以同时属于某个通信形状和某个服务类别；不要把二者当作互斥分类。多目的操作的定义见[集体通信基础](../06-ai-noc-specifics/collective-communication-basics.md)。

## 平均速率相同时，突发也会改变等待

<span id="为什么-burstiness-比平均值更重要"></span>构造例：一个队列有足够空间，服务端每 cycle 恰好处理一个 packet。四个 packet 都在前 4 个 cycle 内释放，无其他流量；服务完成后才能处理下一个 packet。

| 释放方式 | 拍 0、1、2、3 释放量 | 四个 packet 的队列等待 |
| --- | --- | --- |
| 均匀释放 | 1、1、1、1 | 均为 0 cycle。 |
| 集中释放 | 4、0、0、0 | 分别为 0、1、2、3 cycle。 |

两组在这 4 个 cycle 的平均释放率都是 1 packet/cycle；集中释放的平均队列等待为 1.5 cycle。这是指定队列和服务规则下的例子。更长窗口的平均值、队列容量或服务规则变化时，要重新计算。

## 合成流量与实际负载

<span id="synthetic-traffic-仍然必要"></span>合成流量适合控制单个因素并测试模型，例如均匀随机、热点、邻近通信和置换流量。应说明目的分布、是否允许自身目的、packet 大小、生成规则和随机种子。它可以包含突发或依赖，但不能仅凭名称代表某个真实工作负载。

<span id="ai-like-traffic-的本质差异"></span>从工作负载推导的流量可以保留映射、阶段和任务依赖，但质量取决于这些输入是否准确；“AI”“CPU”或“prefill”本身不规定固定的热点或带宽需求。[Garnet 合成流量文档](https://www.gem5.org/documentation/general_docs/debugging_and_testing/directed_testers/garnet_synthetic_traffic/)给出了生成规则和以 packet/node/cycle 表示注入率的具体例子；其他工具的注入边界和 packet 大小可能不同。

## 系统也会改变流量

<span id="和系统集成的关系"></span>地址映射影响目的存储端口，DMA 和 outstanding 限制影响释放节奏，NI 决定如何分包；接收端服务和反压也可能影响后续注入。固定时间重放的 Trace 可以控制网络输入，但未必再现这些反馈。[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)讨论两种边界。

<span id="常见误区"></span><span id="一句话理解"></span><span id="建模启示"></span>比较流量时，保留源、目的、大小、时间与依赖，再检查它们对应哪些网络和端点资源。总字节数和平均注入率是起点，不足以单独确定拥塞或完成时间。
