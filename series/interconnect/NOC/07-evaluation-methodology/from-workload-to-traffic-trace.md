# From Workload To Traffic Trace

上级：[07 Evaluation Methodology](./README.md)

相关：[Compiler NOC Co Design](../06-ai-noc-specifics/compiler-noc-co-design.md)、[Reduction And Collective Networks](../06-ai-noc-specifics/reduction-and-collective-networks.md)、[Core Data Structures](../08-simulator-construction/core-data-structures.md)

## 输入、输出与完成边界

生成器输入是计算 DAG、placement、数据类型、memory map、算法和分组策略；输出是带依赖的 flow、compute 和 barrier 事件。packetizer 再按 payload 上限、header、padding 和 flit width 切包。不能从算子名直接推导网络负载。

v1 使用一致的字段和类型。所有 `id` 都是唯一字符串，`release_time` 为非负整数 cycle，`depends_on` 为字符串数组且按 all-of 解释：每个前驱的指定完成事件发生后才可执行。flow 的依赖完成默认为目的集合中所有 consumer 完成，不是网络到达；compute 在 `duration_cycles` 后完成，barrier 在所有前驱完成后完成。明确局部目的地的本地交付，不隐式计算网络 hop。无效 node、缺失依赖、重复 ID、环和未知 class 必须报错。

```json
{"kind":"flow","id":"A0_0","release_time":0,"depends_on":[],
 "src_node":0,"dst_set":[0,1,2,3],"traffic_class":"STREAM",
 "payload_bytes":2097152,"phase":"k0"}
```

`dst_set` 始终是数组；单播长度为 1。第 08 章基线内核只支持单播：必须显式扩展 fork 状态才能运行共享树；若展开为多份单播，则应按各单播路径重算注入和 byte-hop，不能仍使用下文共享树统计。`compute` 有 `node,duration_cycles`，`barrier` 无网络端点。flow 的多包要等所有目的所需 packet 被 consumer 接收后才完成。`Packet` 内部可映射成 `id/src/dst/class/num_flits/ready_cycle`；单 flit 使用 `HEAD_TAIL`。见 [注入和 tracing](../08-simulator-construction/traffic-injection-and-tracing.md)。

## 可执行的 GEMM 生成器

假设 `M=N=K=4096`，输入/输出 2 B，`Tm=Tn=Tk=1024`，16 个 tile 映射到 4×4 mesh，节点 `id=4×row+col`。每个 `(i,j)` tile 负责一个输出块，顺序累加 4 个 K 块。A 在行内广播，B 在列内广播；每个 A/B 块为 `1024²×2=2,097,152 B = 2 MiB`。示例使用全局阶段 barrier 以简化依赖，不表示唯一或最快的调度。每个 k 有 4 行 A + 4 列 B = 8 flow，共 32；16 个最终 writeback，共 48 flow。16 个输出块各计算 4 次，共 64 compute，而不是 64 个输出块各做 4 步。

将以下代码保存为 `gemm_trace.py`，`python3 gemm_trace.py > trace.json` 输出完整 JSON；`python3 gemm_trace.py --check` 检查 ID、依赖、无环和算例计数。它是有限 workload 生成器，不是模拟器；路径、仲裁和时间由后续模型负责。

```python
#!/usr/bin/env python3
"""Generate a finite GEMM trace, or verify its DAG and link accounting."""
import argparse
import json
import sys
from collections import Counter

bytes_per_block = 1024 * 1024 * 2
rows = 4
columns = 4
steps = 4
events = []


def node_id(row, column):
    return row * columns + column


def add_event(kind, event_id, depends_on, **attributes):
    event = {
        "kind": kind,
        "id": event_id,
        "release_time": 0,
        "depends_on": list(depends_on),
    }
    event.update(attributes)
    events.append(event)


for step in range(steps):
    dependencies = [] if step == 0 else [f"barrier{step - 1}"]
    for row in range(rows):
        add_event(
            "flow", f"A{step}_{row}", dependencies,
            src_node=node_id(row, 0),
            dst_set=[node_id(row, column) for column in range(columns)],
            traffic_class="STREAM", payload_bytes=bytes_per_block,
            phase=f"k{step}",
        )
    for column in range(columns):
        add_event(
            "flow", f"B{step}_{column}", dependencies,
            src_node=node_id(0, column),
            dst_set=[node_id(row, column) for row in range(rows)],
            traffic_class="STREAM", payload_bytes=bytes_per_block,
            phase=f"k{step}",
        )
    for row in range(rows):
        for column in range(columns):
            add_event(
                "compute", f"C{step}_{row}_{column}",
                [f"A{step}_{row}", f"B{step}_{column}"],
                node=node_id(row, column), duration_cycles=1,
                phase=f"k{step}",
            )
    if step < steps - 1:
        completed_blocks = [
            f"C{step}_{row}_{column}"
            for row in range(rows)
            for column in range(columns)
        ]
        add_event("barrier", f"barrier{step}", completed_blocks,
                  phase=f"k{step}")

for row in range(rows):
    for column in range(columns):
        add_event(
            "flow", f"W{row}_{column}", [f"C{steps - 1}_{row}_{column}"],
            src_node=node_id(row, column), dst_set=[node_id(row, 0)],
            traffic_class="BULK_DMA", payload_bytes=bytes_per_block,
            phase="writeback",
        )


def xy_path(source, destination):
    """Directed links in a row-then-column mesh route."""
    row, column = divmod(source, columns)
    dst_row, dst_column = divmod(destination, columns)
    links = []
    while column != dst_column:
        next_column = column + (1 if dst_column > column else -1)
        links.append((node_id(row, column), node_id(row, next_column)))
        column = next_column
    while row != dst_row:
        next_row = row + (1 if dst_row > row else -1)
        links.append((node_id(row, column), node_id(next_row, column)))
        row = next_row
    return links


def verify_trace():
    events_by_id = {event["id"]: event for event in events}
    assert len(events_by_id) == len(events), "duplicate event id"
    assert all(
        dependency in events_by_id
        for event in events for dependency in event["depends_on"]
    ), "missing dependency"
    completed = set()
    while len(completed) < len(events):
        ready = {
            event["id"] for event in events
            if event["id"] not in completed
            and set(event["depends_on"]) <= completed
        }
        assert ready, "dependency graph contains a cycle"
        completed.update(ready)

    counts = Counter(event["kind"] for event in events)
    assert counts == {"flow": 48, "compute": 64, "barrier": 3}
    totals = Counter()
    header_bytes = 16
    flit_bytes = 16
    for event in events:
        if event["kind"] != "flow":
            continue
        payload = event["payload_bytes"]
        totals["logical_payload"] += payload
        tree_links = set()
        for destination in event["dst_set"]:
            tree_links.update(xy_path(event["src_node"], destination))
        if not tree_links:
            continue
        wire_bytes = ((payload + header_bytes + flit_bytes - 1)
                      // flit_bytes * flit_bytes)
        totals["network_injection_payload"] += payload
        totals["network_injection_wire"] += wire_bytes
        totals["payload_byte_hops"] += payload * len(tree_links)
        totals["wire_byte_hops"] += wire_bytes * len(tree_links)

    expected = {
        "logical_payload": 100663296,
        "network_injection_payload": 92274688,
        "network_injection_wire": 92275392,
        "payload_byte_hops": 251658240,
        "wire_byte_hops": 251660160,
    }
    assert dict(totals) == expected, (totals, expected)
    print("counts", dict(counts), "totals", dict(totals))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.check:
        verify_trace()
    else:
        json.dump({"schema": "noc-workload-v1", "events": events},
                  sys.stdout, ensure_ascii=False, indent=2)
```

固定行/列树沿网格相邻边传播，每个广播有 3 条边；每行 writeback 的路径长度依列为 0、1、2、3。假设每个 2 MiB flow 是一个 packet、header 16 B、flit 16 B、无其他 padding，且本地写回不入网：

| 计量口径 | 值 | 计算 |
| --- | ---: | --- |
| 逻辑 flow payload | 96 MiB | `(32+16)×2 MiB`，含本地交付 |
| 网络注入 payload | 88 MiB | `(32+12)×2 MiB` |
| 网络注入 wire | 92,275,392 B | 44 个网络 packet 各加 16 B header |
| payload byte-hop | 251,658,240 B | `(32×3+24)×2 MiB` |
| wire byte-hop | 251,660,160 B | 120 次 packet-hop 各加 16 B header |

这些值不是 makespan：同一链路、NI 和 consumer 会竞争。可将该 trace 放入具体仿真器并记录网络到达和 consumer 完成，按指定时序验证；不应以任意误差百分比将差异直接判错。

## 可手算的 prefill 小 trace

batch=1、4 token、1 head、head_dim=4、FP16。两个相邻 tile 各持 2 token 的 Q/K/V，双方交换本地 K 与 V：每方向合并一个 32 B payload packet，两个方向独立。假设每 packet header=16 B、flit=16 B、每方向链路 1 flit/cycle、单 hop `forward_latency=1`、充足 credit 和 ejection/consumer 容量。源 router 的输入 FIFO 在 `S(0)` 已有完整 packet；没有其他流量。按 [快照契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)，各方向在 t=0、1、2 发 3 flit，最后 flit 在 t=3 拍末到达下游 FIFO、t=4 弹出、t=5 被 consumer 消费。两个方向同时完成：payload 64 B，网络注入 wire 和单跳 wire byte-hop 均为 96 B，完成时间戳为 t=5；若按包含 t=0 到 t=5 的离散周期数报告则为 6 cycle。Q 的计算依赖接收完成。真实 prefill 的 masking、FlashAttention 分块与共享路径会改变通信。

## AllReduce 的量纲检查

假设 8 个端点组成无竞争的单向逻辑 ring，每端点向量 100 MiB。reduce-scatter 和 all-gather 各 7 步，每步每端点发送 `12.5 MiB = 13,107,200 B`，共 `8×14=112` 个 flow。每端点发送 `1.75×100 MiB=175 MiB`；8 个端点合计 1,468,006,400 B 注入 payload。若 B=64 B/cycle、每阶段 `α=10 cycle`，忽略算术/拥塞时，带宽项为 `1.75×104,857,600/64 = 2,867,200 cycle`，加固定项 140，合计 2,867,340 cycle。实际逻辑邻居若经多 hop，须另算 byte-hop 和对应路径延迟。

## 复核方法

分别检查逻辑 payload、网络注入 payload、header/padding 后 wire bytes 和每条边的 byte-hop。核对 DAG 引用、每个消费者完成条件及资源共享，再在明确时序和服务假设下核对 makespan。保留输入、路由、随机 seed、warmup/measurement/drain、未完成任务和简化项；对有拥塞的 workload，应将手算界、逐拍样例和模型结果分别报告。
