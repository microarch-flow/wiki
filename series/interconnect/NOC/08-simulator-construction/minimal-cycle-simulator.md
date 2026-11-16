# 最小逐拍仿真实作：三跳单播如何前进？

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)

相关：[路由器逐拍推进](./router-pipeline-pseudocode.md)、[核心数据结构](./core-data-structures.md)、[验证、校准与适用边界](./verification-and-calibration.md)

本例实现一条固定的 `R0—R1—R2—R3` 路径。它只处理**一个单播 packet**：每个 router 有一个输入 VC 和固定深度 FIFO；每拍每个输出最多发一个 flit。源、目的 FIFO 和正反向链路都使用同一个时钟。consumer 每拍最多消费一个 flit。

本例使用[时间与快照契约](./router-pipeline-pseudocode.md#时间与快照契约)：读取 S(t)，拍末提交。跨 router 的 flit 与 slot credit 分别在发送或释放后指定的延迟拍末到达；到期值本拍不可用于决策。源注入和 LOCAL 弹出也在拍末写入队列。

代码记录 tail 返回的 free 标记，以检查所有反馈是否返回；因为全程只有一个 packet，它**没有实现多个 packet 的 VC 分配、switch 仲裁或下一包复用**。它也不读取第八章 v1 Trace、不实现多播、compute、memory 或真实芯片协议。它是验证基础时间和守恒的教学程序。

## 运行示例

将代码保存为 `line_noc.py`。运行 `python3 line_noc.py`，输出默认三 flit 的拍末快照。运行 `python3 line_noc.py --size 30 --block-until 30`，让 consumer 在拍 30 前停止，再观察反压与恢复。`--max-cycles` 用于限制运行；超时只表示在该上限内未完成，不证明死锁。

```python
#!/usr/bin/env python3
"""One-packet, four-router teaching model; cycle labels are zero based."""
import argparse
from collections import deque


class LineNoC:
    def __init__(self, num_flits=3, depth=4, ejection_depth=4,
                 forward_latency=1, return_latency=1):
        values = (num_flits, depth, ejection_depth, forward_latency, return_latency)
        if any(type(value) is not int or value < 1 for value in values):
            raise ValueError("sizes and latencies must be positive integers")
        self.num_flits = num_flits
        self.depth = depth
        self.ejection_depth = ejection_depth
        self.forward_latency = forward_latency
        self.return_latency = return_latency
        self.cycle = 0
        self.source = deque(range(num_flits))
        self.inputs = [deque() for _ in range(4)]
        self.ejection = deque()
        # credit[i] authorizes the upstream to reserve a slot in inputs[i].
        self.credit = [depth] * 4
        self.forward = []    # (due_cycle, target_input, flit_sequence)
        self.returns = []    # (due_cycle, target_credit, is_tail_free)
        self.free_seen = [False] * 4
        self.consumed = []
        self.injection_cycle = None
        self.network_arrival_cycle = None
        self.consumer_complete_cycle = None
        self.quiescent_cycle = None

    def label(self, seq):
        if self.num_flits == 1:
            return "HT"
        if seq == 0:
            return "H"
        if seq == self.num_flits - 1:
            return "T"
        return "B"

    def tick(self, consumer_ready=True):
        """Read S(t), plan actions, and commit all changes at the end of t."""
        if type(consumer_ready) is not bool:
            raise ValueError("consumer_ready must be bool")
        t = self.cycle
        old_inputs = [tuple(queue) for queue in self.inputs]
        old_ejection = tuple(self.ejection)
        old_credit = tuple(self.credit)
        next_source = deque(self.source)
        next_consumed = list(self.consumed)
        next_free_seen = list(self.free_seen)
        next_injection = self.injection_cycle
        next_arrival = self.network_arrival_cycle
        next_completion = self.consumer_complete_cycle
        next_inputs = [deque(queue) for queue in old_inputs]
        next_ejection = deque(old_ejection)
        next_credit = list(old_credit)
        if any(event[0] < t for event in self.forward + self.returns):
            raise AssertionError("overdue link event")
        due_forward = [event for event in self.forward if event[0] == t]
        due_returns = [event for event in self.returns if event[0] == t]
        next_forward = [event for event in self.forward if event[0] > t]
        next_returns = [event for event in self.returns if event[0] > t]
        actions = []

        # An endpoint only consumes what was present at the start of the cycle.
        if consumer_ready and old_ejection:
            seq = next_ejection.popleft()
            next_consumed.append(seq)
            actions.append(f"consume {self.label(seq)}")
            if seq == self.num_flits - 1:
                next_completion = t

        for router in range(4):
            if not old_inputs[router]:
                continue
            seq = old_inputs[router][0]
            is_tail = seq == self.num_flits - 1
            if router < 3 and old_credit[router + 1] > 0:
                if next_inputs[router].popleft() != seq:
                    raise AssertionError("snapshot/input mismatch")
                next_credit[router + 1] -= 1
                next_forward.append((t + self.forward_latency, router + 1, seq))
                next_returns.append((t + self.return_latency, router, is_tail))
                actions.append(f"R{router}->R{router + 1} {self.label(seq)}")
            elif router == 3 and len(old_ejection) < self.ejection_depth:
                if next_inputs[router].popleft() != seq:
                    raise AssertionError("snapshot/input mismatch")
                next_ejection.append(seq)
                next_returns.append((t + self.return_latency, router, is_tail))
                actions.append(f"eject {self.label(seq)}")
                if is_tail:
                    next_arrival = t

        # The source also uses the start-of-cycle credit, never a due credit.
        if next_source and old_credit[0] > 0:
            seq = next_source.popleft()
            next_inputs[0].append(seq)
            next_credit[0] -= 1
            actions.append(f"inject {self.label(seq)}")
            if seq == 0:
                next_injection = t

        for _, target, seq in due_forward:
            next_inputs[target].append(seq)
        for _, target, is_tail_free in due_returns:
            next_credit[target] += 1
            if is_tail_free:
                next_free_seen[target] = True

        self.source = next_source
        self.consumed = next_consumed
        self.free_seen = next_free_seen
        self.injection_cycle = next_injection
        self.network_arrival_cycle = next_arrival
        self.consumer_complete_cycle = next_completion
        self.inputs = next_inputs
        self.ejection = next_ejection
        self.credit = next_credit
        self.forward = next_forward
        self.returns = next_returns
        self.check_invariants()
        if self.quiescent_cycle is None and self.is_quiescent():
            self.quiescent_cycle = t
        row = {"cycle": t, "inputs": [list(q) for q in self.inputs],
               "ejection": list(self.ejection), "credit": list(self.credit),
               "source_pending": len(self.source), "actions": actions}
        self.cycle += 1
        return row

    def check_invariants(self):
        for target in range(4):
            forward_count = sum(1 for _, dest, _ in self.forward if dest == target)
            return_count = sum(1 for _, dest, _ in self.returns if dest == target)
            total = self.credit[target] + forward_count + len(self.inputs[target]) + return_count
            if total != self.depth or not 0 <= self.credit[target] <= self.depth:
                raise AssertionError(f"credit conservation failed for input {target}")
            if len(self.inputs[target]) > self.depth:
                raise AssertionError(f"input {target} overflow")
        if len(self.ejection) > self.ejection_depth:
            raise AssertionError("ejection overflow")
        pending = (len(self.source) + sum(len(q) for q in self.inputs)
                   + len(self.forward) + len(self.ejection) + len(self.consumed))
        if pending != self.num_flits:
            raise AssertionError("flit conservation failed")
        flits = list(self.source) + [seq for q in self.inputs for seq in q]
        flits += [seq for _, _, seq in self.forward] + list(self.ejection) + self.consumed
        if sorted(flits) != list(range(self.num_flits)):
            raise AssertionError("flit identity duplicated or lost")
        if self.consumed != list(range(len(self.consumed))):
            raise AssertionError("flit order changed")

    def is_quiescent(self):
        return (not self.source and all(not q for q in self.inputs)
                and not self.ejection and not self.forward and not self.returns
                and self.credit == [self.depth] * 4 and all(self.free_seen)
                and len(self.consumed) == self.num_flits)

    def run(self, block_until=0, max_cycles=500):
        if type(block_until) is not int or block_until < 0:
            raise ValueError("block_until must be a nonnegative integer")
        if type(max_cycles) is not int or max_cycles < 1:
            raise ValueError("max_cycles must be a positive integer")
        rows = []
        while len(rows) < max_cycles and not self.is_quiescent():
            rows.append(self.tick(consumer_ready=self.cycle >= block_until))
        if not self.is_quiescent():
            raise TimeoutError("unfinished within max_cycles; not a deadlock proof")
        return rows


def format_queue(sim, values):
    return "".join(sim.label(value) for value in values) or "-"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=3)
    parser.add_argument("--block-until", type=int, default=0)
    parser.add_argument("--max-cycles", type=int, default=500)
    args = parser.parse_args()
    sim = LineNoC(num_flits=args.size, ejection_depth=2 if args.block_until else 4)
    rows = sim.run(block_until=args.block_until, max_cycles=args.max_cycles)
    print("cycle R0 R1 R2 R3 E credit(I,01,12,23) actions")
    for row in rows:
        queues = [format_queue(sim, q) for q in row["inputs"]]
        ejection = format_queue(sim, row["ejection"])
        print(row["cycle"], *queues, ejection, row["credit"], "; ".join(row["actions"]))
    print("injection, network arrival, consumer complete, quiescent:",
          sim.injection_cycle, sim.network_arrival_cycle,
          sim.consumer_complete_cycle, sim.quiescent_cycle)
```

## 读懂输出

默认条件为输入 VC 深度 4、ejection 深度 4，正向与返回延迟均为 1。首 flit 在拍 0 注入，tail 在拍 9 弹出到 ejection FIFO，在拍 10 被 consumer 消费；全部 credit 和 tail free 也在拍 10 末返回。完整拍末队列表见[场景 1](./verification-and-calibration.md#场景-1三跳三-flit无阻塞)。

在 `--size 30 --block-until 30` 的构造例中，ejection 深度为 2。拍 17 末四个输入 FIFO 都为 4 flit、ejection 为 2 flit，四个发送端 credit 均为 0，源端还剩 12 flit。consumer 在拍 30 恢复；按此代码的规则，tail 在拍 59 被消费。改变容量或时序就要重新计算。

每次提交后程序检查每个输入的 `深度 = 可用 credit + 正向在途 flit + 已占 slot + 返回在途 credit`，并检查 FIFO 容量、flit 的唯一性和消费顺序。源端到 R0 的注入没有额外正向管线；其 credit 同样在释放 slot 后返回。跨 router link 的 credit 和该源注入 credit 分开统计。

这些检查证明运行中满足所写的不变量，不足以证明任意路由无死锁或性能接近硬件。后续要实现多个 packet、VC 或不同端点行为，应先增加对应状态和独立预期，再扩展测试。
