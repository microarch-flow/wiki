# 从 Flow 到完成：一条依赖怎样跨过网络？

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)

相关：[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)、[工作负载与端点执行](./workload-endpoint-execution.md)、[最小逐拍仿真实作](./minimal-cycle-simulator.md)、[验证场景](./verification-and-calibration.md)

本例把一个 flow 映射成一个 packet，再连接后继 compute 的依赖。网络时序来自现有教学程序；flow 完成和 compute 时序按本文契约**手工推导**。程序不读取 Trace，不执行 compute，也不验证本文的分包规则。

## 输入与分包假设

构造一个 `noc-workload-v1` 事件图：F0 从节点 0 向节点 3 单播 32 B payload；C0 在节点 3 计算 2 cycle，依赖 F0。两者的释放时间均为 0，C0 仍须等待 F0 完成。

```json
{
  "schema": "noc-workload-v1",
  "events": [
    {"id": "F0", "kind": "flow", "release_time": 0, "depends_on": [],
     "src_node": 0, "dst_set": [3], "traffic_class": "STREAM", "payload_bytes": 32},
    {"id": "C0", "kind": "compute", "release_time": 0, "depends_on": ["F0"],
     "node": 3, "duration_cycles": 2}
  ]
}
```

为本例另行指定 packet header 为 16 B，flit 为 16 B；header 与 payload 连续装填，没有其他开销。32 + 16 = 48 B，恰好为 **3 flit、1 个 packet**。v1 事件本身不规定这里的 header 或分包方式。目的集合只有节点 3，因此 F0 的 all-consumer 完成条件只需这个目的的 consumer 接收全部数据。

假设节点 0 到节点 3 对应教学程序的 R0—R1—R2—R3 固定路径，只有这一个 packet，使用默认队列、链路延迟和持续可接收的 consumer。程序只接收 flit 数量；它不检查上面的节点映射、字节和包头。

## 先运行网络模型

将[最小逐拍实作](./minimal-cycle-simulator.md)的代码保存为 `line_noc.py`，运行 `python3 line_noc.py --size 3`。末行报告：

```text
injection, network arrival, consumer complete, quiescent: 0 9 10 10
```

这些数值是程序的拍号：首 flit 在拍 0 注入；tail 在拍 9 末进入目的 ejection FIFO；consumer 在拍 10 消费 tail；程序检查的网络状态也在拍 10 末首次静止。时间和队列快照见[三跳无阻塞场景](./verification-and-calibration.md#场景-1三跳三-flit无阻塞)。

## 再按工作负载契约推导

约定 F0 的唯一 packet 被 consumer 完整接收时，F0 在同一拍末完成；完成结果从下一拍快照可见。C0 所需计算资源在节点 3 空闲、可立即启动，无其他竞争；2-cycle 计算运行于半开区间 `[开始拍, 开始拍 + 2)`。

| 时间 | 事件 | 证据来源 |
| --- | --- | --- |
| 拍 0 末 | 首 flit 注入。 | 程序输出。 |
| 拍 9 末 | tail 进入 ejection；完整 packet 尚未被 consumer 接收。 | 程序输出。 |
| 拍 10 末 | consumer 接收 tail；按本例契约 F0 完成。 | 前半项为程序输出，后半项为手工推导。 |
| S(11) | C0 首次看到 F0 完成，且资源可用，开始计算。 | 手工推导。 |
| 拍 12 末 | C0 完成两个计算周期；后继最早在 S(13) 看见完成。 | 手工推导。 |

本例在拍 10 末网络已经静止，工作负载却要到拍 12 末才完成。网络静止和 workload 完成不能互相替代；其他配置下，consumer 完成后 credit 也可能仍在返回途中。

## 扩展前要增加什么

要让程序直接处理上面的 JSON，需要解析并验证事件、实现分包和节点映射、执行 consumer／compute 资源及依赖释放，并验证其与网络的时间契约。多 packet、多目的、竞争或本地交付还要补相应状态。本文手工映射不证明这些能力已经实现，也不证明模型与真实硬件一致。
