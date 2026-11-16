# Trace 生成与核算实作：一个 4×4 GEMM 示例

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)

相关：[从工作负载到流量 Trace](./from-workload-to-traffic-trace.md)、[GEMM 通信案例](../06-ai-noc-specifics/workload-gemm-on-noc.md)、[流量注入与 Trace](../08-simulator-construction/traffic-injection-and-tracing.md)

本例生成一个有限的事件图，并在固定路径上核算流量。它不是 NoC 模拟器，也不计算排队、仲裁或任务完成时间。

## 固定映射和依赖

设 A、B、C 均为 4096×4096，输入和最终输出每元素 2 B。16 个 tile 排成 4×4 mesh，每个 tile 负责一个 1024×1024 的 C 块；K 分成 4 个长度为 1024 的步骤。一个 A、B 或输出块为 **2 MiB**。

每个步骤中，A 块从各行左端送到该行 4 个 tile，B 块从各列上端送到该列 4 个 tile。每个源也使用本地块；本例不计输入块预先加载到源的位置。每个 tile 在得到对应 A、B flow 后执行一次 compute；全局 barrier 等待该步骤的 16 个 compute，再释放下一步骤。最后，每个 tile 将结果写回本行左端，包括已经在该处的本地写回。

本例的 flow 在**所有目的 consumer** 完成后才结束。因此一个 tile 的 compute 也会等待对应行和列 flow 的全部目的，而不是只等待自己收到数据。`duration_cycles=1` 是占位值；不据此推断真实性能。

## 生成器与检查

将下面代码保存为 `gemm_trace.py`。`python3 gemm_trace.py > trace.json` 输出事件；`python3 gemm_trace.py --check` 核对示例数量、两种分发计数，并检查部分非法字段能否被拒绝。`validate_trace` 检查本例支持的字段、节点、类别和 DAG；这不证明任意其他 schema 或网络模型正确。

```python
#!/usr/bin/env python3
"""Generate and check the chapter's 4x4 GEMM workload example."""
import argparse
import copy
import json
import sys
from collections import Counter

ROWS = COLS = STEPS = 4
BLOCK_BYTES = 1024 * 1024 * 2
CLASSES = {"CONTROL", "MEMORY_REQUEST", "MEMORY_RESPONSE", "STREAM", "BULK_DMA"}


def node(row, column):
    return row * COLS + column


def make_trace():
    events = []

    def add(kind, event_id, dependencies, **fields):
        event = {"kind": kind, "id": event_id, "release_time": 0,
                 "depends_on": list(dependencies)}
        event.update(fields)
        events.append(event)

    for step in range(STEPS):
        dependencies = [] if step == 0 else [f"barrier{step - 1}"]
        for row in range(ROWS):
            add("flow", f"A{step}_{row}", dependencies,
                src_node=node(row, 0),
                dst_set=[node(row, column) for column in range(COLS)],
                traffic_class="STREAM", payload_bytes=BLOCK_BYTES, phase=f"k{step}")
        for column in range(COLS):
            add("flow", f"B{step}_{column}", dependencies,
                src_node=node(0, column),
                dst_set=[node(row, column) for row in range(ROWS)],
                traffic_class="STREAM", payload_bytes=BLOCK_BYTES, phase=f"k{step}")
        for row in range(ROWS):
            for column in range(COLS):
                add("compute", f"C{step}_{row}_{column}",
                    [f"A{step}_{row}", f"B{step}_{column}"],
                    node=node(row, column), duration_cycles=1, phase=f"k{step}")
        if step < STEPS - 1:
            add("barrier", f"barrier{step}",
                [f"C{step}_{row}_{column}"
                 for row in range(ROWS) for column in range(COLS)], phase=f"k{step}")

    for row in range(ROWS):
        for column in range(COLS):
            add("flow", f"W{row}_{column}", [f"C{STEPS - 1}_{row}_{column}"],
                src_node=node(row, column), dst_set=[node(row, 0)],
                traffic_class="BULK_DMA", payload_bytes=BLOCK_BYTES, phase="writeback")
    return {"schema": "noc-workload-v1", "events": events}


def validate_trace(trace):
    """Check the fields and dependency graph supported by this example."""
    def integer(value, minimum=0):
        return type(value) is int and value >= minimum

    def valid_node(value):
        return integer(value) and value < ROWS * COLS

    if not isinstance(trace, dict) or trace.get("schema") != "noc-workload-v1":
        raise ValueError("unknown trace schema")
    events = trace.get("events")
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    by_id = {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("event must be an object")
        event_id = event.get("id")
        if not isinstance(event_id, str) or not event_id or event_id in by_id:
            raise ValueError("missing or duplicate event id")
        if not integer(event.get("release_time")):
            raise ValueError(f"invalid release_time: {event_id}")
        deps = event.get("depends_on")
        if (not isinstance(deps, list)
                or not all(isinstance(d, str) and d for d in deps)
                or len(set(deps)) != len(deps)):
            raise ValueError(f"invalid depends_on: {event_id}")
        if "phase" in event and not isinstance(event["phase"], str):
            raise ValueError(f"invalid phase: {event_id}")
        kind = event.get("kind")
        if kind == "flow":
            destinations = event.get("dst_set")
            if (not valid_node(event.get("src_node"))
                    or not isinstance(destinations, list) or not destinations
                    or not all(valid_node(d) for d in destinations)
                    or len(set(destinations)) != len(destinations)
                    or not isinstance(event.get("traffic_class"), str)
                    or event["traffic_class"] not in CLASSES
                    or not integer(event.get("payload_bytes"), 1)):
                raise ValueError(f"invalid flow: {event_id}")
        elif kind == "compute":
            if not valid_node(event.get("node")) or not integer(event.get("duration_cycles")):
                raise ValueError(f"invalid compute: {event_id}")
        elif kind != "barrier":
            raise ValueError(f"unknown kind: {event_id}")
        by_id[event_id] = event

    for event in events:
        if any(dependency not in by_id for dependency in event["depends_on"]):
            raise ValueError(f"missing dependency: {event['id']}")
    completed = set()
    while len(completed) < len(events):
        ready = {event_id for event_id, event in by_id.items()
                 if event_id not in completed and set(event["depends_on"]) <= completed}
        if not ready:
            raise ValueError("dependency graph contains a cycle")
        completed.update(ready)


def xy_path(source, destination):
    """Directed mesh edges; traverse columns before rows."""
    row, column = divmod(source, COLS)
    dst_row, dst_column = divmod(destination, COLS)
    links = []
    while column != dst_column:
        next_column = column + (1 if dst_column > column else -1)
        links.append((node(row, column), node(row, next_column)))
        column = next_column
    while row != dst_row:
        next_row = row + (1 if dst_row > row else -1)
        links.append((node(row, column), node(next_row, column)))
        row = next_row
    return links


def count_traffic(trace, mode):
    """Count one-packet flows using the example's shared tree or unicasts."""
    if mode not in {"shared", "unicast"}:
        raise ValueError("unknown distribution mode")
    totals = Counter()
    for event in trace["events"]:
        if event["kind"] != "flow":
            continue
        payload = event["payload_bytes"]
        source = event["src_node"]
        destinations = event["dst_set"]
        totals["logical_flow_payload"] += payload
        totals["consumer_payload"] += payload * len(destinations)
        if source in destinations:
            totals["local_payload"] += payload
        paths = [xy_path(source, destination) for destination in destinations
                 if destination != source]
        if mode == "shared" and paths:
            transmissions = [set(link for path in paths for link in path)]
        else:
            transmissions = paths
        wire = ((payload + 16 + 15) // 16) * 16  # 16 B header, 16 B flit
        for edges in transmissions:
            totals["injection_payload"] += payload
            totals["injection_wire"] += wire
            totals["payload_byte_hop"] += payload * len(edges)
            totals["wire_byte_hop"] += wire * len(edges)
    return dict(totals)


def check_example(trace):
    validate_trace(trace)
    counts = Counter(event["kind"] for event in trace["events"])
    if counts != {"flow": 48, "compute": 64, "barrier": 3}:
        raise ValueError(f"unexpected event counts: {counts}")
    common = {"logical_flow_payload": 100663296, "consumer_payload": 301989888,
              "local_payload": 75497472}
    shared = {**common, "injection_payload": 92274688, "injection_wire": 92275392,
              "payload_byte_hop": 251658240, "wire_byte_hop": 251660160}
    unicast = {**common, "injection_payload": 226492416, "injection_wire": 226494144,
               "payload_byte_hop": 452984832, "wire_byte_hop": 452988288}
    if count_traffic(trace, "shared") != shared or count_traffic(trace, "unicast") != unicast:
        raise ValueError("unexpected traffic counts")
    for field, value in (("src_node", -1), ("traffic_class", "UNKNOWN"),
                         ("release_time", -1)):
        invalid = copy.deepcopy(trace)
        invalid["events"][0][field] = value
        try:
            validate_trace(invalid)
        except ValueError:
            continue
        raise ValueError(f"invalid {field} was accepted")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    trace = make_trace()
    if args.check:
        check_example(trace)
        print("example checks passed")
    else:
        json.dump(trace, sys.stdout, ensure_ascii=False, indent=2)
        print()
```

## 独立核对数据量

按示例规定，每个 2 MiB flow 是一个 packet，header 为 16 B、flit 为 16 B，没有其他填充或重传。本地交付不入网。共享树沿相邻行或列复制，写回按示例的先列后行路径单播；单播方案则给每个远端目的各发一份。单播展开是流量表示，不代表现有程序已能读取此 Trace。要执行它，还需要 v1 读取、分包、端点执行和依赖释放；共享树另需复制及完成状态。第九章[最小逐拍实作](../08-simulator-construction/minimal-cycle-simulator.md)只处理固定路径上的一个 packet，不读取本 Trace。

| 统计口径 | 共享树 | 展开为单播 |
| --- | ---: | ---: |
| flow 逻辑 payload，含本地 flow | 96 MiB | 96 MiB |
| 目的端逻辑交付，含本地 | 288 MiB | 288 MiB |
| 本地交付 | 72 MiB | 72 MiB |
| 网络注入 payload | 88 MiB | 216 MiB |
| 网络注入 wire | 92,275,392 B | 226,494,144 B |
| payload byte-hop | 251,658,240 B·hop | 452,984,832 B·hop |
| wire byte-hop | 251,660,160 B·hop | 452,988,288 B·hop |

复算时，32 个输入 flow 各有 4 个目的，16 个写回 flow 各有 1 个目的，故目的交付为 `(32×4+16)×2 MiB=288 MiB`。共享树的每个输入 flow 使用 3 条边；每行 4 次写回分别经过 0、1、2、3 条边，故共有 `32×3+4×(0+1+2+3)=120` 次 packet-hop。展开为单播后，每个输入 flow 的远端路径分别为 1、2、3 跳，共 `32×6+24=216` 次 packet-hop。

这里的网络注入按 packet 发出时的整个 payload 记账；byte-hop 按实际经过的每条有向边分别计。两种方案有相同的目的端逻辑交付量，但共享树是否可行、如何复制和受哪些资源限制，必须由具体实现说明。真实系统可能把 2 MiB 拆为多个 packet，届时每包 header、填充、排队和完成条件都要重新计算。
