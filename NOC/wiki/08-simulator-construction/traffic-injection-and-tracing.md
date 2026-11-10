# Traffic Injection And Tracing

上级：[08 Simulator Construction](./README.md)

相关：[From Workload To Traffic Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)、[Core Data Structures](./core-data-structures.md)

## 这页在回答什么问题

这页回答：trace 进入 simulator 时应该如何组织注入逻辑，哪些字段必须保留，怎样避免 trace engine 和 NoC core 写成一团。

## trace engine 和 NoC core 应解耦

最好的做法通常是：

- trace engine 负责在正确时间释放 flow / packet
- NoC core 负责判断它们能不能真的进网

不要让 trace engine 直接绕过 injection queue 把 flit 塞进 router。否则很多 `INJECTION_BLOCKED`、source-side stall、class 竞争都会被抹平。

## 推荐注入流程

一个实用流程是：

1. 读取 trace 中到时的 event / flow
2. packetize 成 packet 列表
3. packet 入 endpoint `pending_packets`
4. endpoint 再按注入规则把 packet 切成 flit 放入 router local input

这样可以自然表达：

- release time
- dependency
- packetization 开销
- 注入阻塞

## trace 最少字段

v1 事件按类型保留字段：

- 共用：`kind`、唯一字符串 `id`、非负整数 `release_time`、`depends_on`；依赖为前驱 ID 数组，按 all-of 等待约定完成事件。
- `flow`：`src_node`、数组 `dst_set`、`traffic_class`、`payload_bytes`。
- `compute`：`node`、`duration_cycles`；完成时释放后继。
- `barrier`：没有网络端点，所有前驱完成后释放后继。
- 可选的阶段标记统一使用 `phase`，与 GEMM 生成器一致。

与 [v1 workload schema](../07-evaluation-methodology/from-workload-to-traffic-trace.md#输入输出与完成边界) 一致。flow 默认等所有目的 consumer 完成；network arrival 不足以释放依赖。compute/barrier 也有 ID 和完成事件。加载时检查重复 ID、未知 class、无效 node、死引用和 DAG 环，拒绝非法输入；在依赖满足且 release_time 已到后才进入 ready 队列。

如需更进一步，可以再加：

- `route_hint`
- `memory_context`
- `phase`

## packetization 不应被省略成隐式常数

同一个 flow，采用不同 packet / flit 粒度时，影响会包括：

- header 开销
- serialization latency
- wormhole path 占用时间
- ejection burst 形状

每 packet 的 `num_flits=ceil((payload_bytes+header_bytes+tail_bytes)/flit_bytes)`，并记录 padding；具体格式可将 tail 信息包含在 header 或 payload，不得重复计数。单 flit 包用 `HEAD_TAIL`。单播基线若将 multicast 展开为多个单播，要按展开结果重新统计；只有实现 fork 状态的扩展才可使用共享树。计时分别记录 release、首 flit 注入、tail 网络到达和 consumer 完成。

## synthetic 和 workload trace 最好共用接口

无论是：

- hotspot synthetic
- GEMM-like trace
- decode trace

都尽量走同一条注入接口。

这样你的 simulator 才不会出现：

- synthetic 一套逻辑
- workload 一套逻辑
- 结果不可比

## class 和 dependency 应在注入前就固定

流量类别和依赖关系不应等到进入 router 才临时猜。最好在 trace / packet 生成阶段就固定好：

- `traffic_class`（flow 字段）
- release condition
- route hint

这样 router core 才能专注于网络推进，而不是背上 workload 语义判断。

## 一句话理解

好的注入体系，是让 trace 负责“何时该发什么”，让 NoC core 负责“此刻能不能发进去”。

## 建模启示

实现上建议至少拆成三个模块：

- `trace_reader`
- `packetizer`
- `injection_controller`

这样后续要换 trace schema、换 packet size、换 synthetic generator 时，不会波及整个 NoC 内核。
