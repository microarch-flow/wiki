# 流量注入、分包与完成：Trace 怎样进入网络？

<span id="traffic-injection-and-tracing"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)、[工作负载与端点执行](./workload-endpoint-execution.md)、[核心数据结构](./core-data-structures.md)

<span id="这页在回答什么问题"></span><span id="trace-engine-和-noc-core-应解耦"></span>Trace 描述事件何时允许执行；endpoint 根据容量和资源决定何时注入；网络决定何时能够前进。把 packet 直接塞进 router 会掩盖源端等待，也可能绕过 credit 契约。

## 从就绪事件到 packet

<span id="推荐注入流程"></span><span id="trace-最少字段"></span>加载器先检查唯一 ID、非负释放时间、合法节点与 class、前驱存在及依赖无环。v1 的 flow 带 `src_node`、`dst_set`、`traffic_class`、`payload_bytes`；compute 带 `node`、`duration_cycles`；barrier 没有网络端点。各事件都使用 `release_time` 和按 all-of 解释的 `depends_on`，可选 `phase`。字段及语义以[第八章 v1 契约](../07-evaluation-methodology/from-workload-to-traffic-trace.md#输入输出与完成边界)为准。

依赖在快照中已满足且释放时间已到后，flow 才可进入 ready 队列。packetizer 将远端交付分成 packet；注入控制器再按许可和 credit 逐 flit 发送。若 ready 队列在本拍末新增 packet，按本章快照规则最早下一拍才能从该队列注入。统计要分别记录释放、首次注入、网络到达和 consumer 完成。

## packetization 不应被省略成隐式常数

对一个 packet，若 payload、header 和 tail 字节可以连续填入固定宽度的 flit，所需数量为：

> flit 数 = ⌈(payload bytes + header bytes + tail bytes) / flit bytes⌉。

余下空间是 padding；tail 信息若已包含在 header 或 payload 中，不得重复计数。若协议要求独立 header flit、每 flit 保留元数据或其他对齐，必须按该格式计算。单 flit 包使用 `HEAD_TAIL`。

## 多目的 flow 的完成

假设源节点 0 向 `{0,1,3}` 交付同一份 40 B 数据；每个 packet 的 payload 上限为 16 B，header 为 8 B，flit 为 16 B，尾部信息包含在 header 中，忽略其他开销。基线不实现共享树，将两个远端目的展开成单播。本地节点 0 直接交付 40 B，不计网络注入或 router 间 hop。

| 每个远端目的 | 三个 packet 的 payload | flit 数 | wire 字节 |
| --- | --- | --- | ---: |
| 节点 1 或 3 | 16、16、8 B | 2、2、1 | 32 + 32 + 16 = 80 B |

两个远端合计注入 6 个 packet、80 B payload、160 B wire。实际 byte-hop 还要按各自路径逐边计算。packetizer 需保存父 flow ID、目的和 packet ID；每个目的的所有 packet 被 consumer 接收后，该目的才完成；所有目的包括本地目的完成后，父 flow 才完成并释放后继。重复完成事件不能重复计数，远端 packet 即使乱序完成也要按 ID 汇总。

[Trace 生成与核算实作](../07-evaluation-methodology/trace-generation-worked-example.md)比较了共享树与单播展开。共享树需要额外实现复制及各分支完成状态，不能直接套用单播的网络计数。

## 输入与网络的边界

<span id="synthetic-和-workload-trace-最好共用接口"></span>合成流量和 workload Trace 可以共用 packetizer 与注入接口，但仍应记录各自释放规则。固定时间回放与依赖驱动事件可能产生不同反馈，不能仅凭接口相同断言工作负载等价。

<span id="class-和-dependency-应在注入前就固定"></span>class、目的和依赖由输入或上层映射确定；路由器按其网络契约处理资源。class 标签不自动建立 VC 隔离或优先级。

<span id="一句话理解"></span><span id="建模启示"></span>在每个层级保留父子 ID 和完成边界，才能同时统计网络传输与工作负载前进。[Netrace 原论文](https://www.research.ed.ac.uk/en/publications/netrace-dependency-driven-trace-based-network-on-chip-simulation/)展示了在 Trace 中保留消息依赖的一种方法。
