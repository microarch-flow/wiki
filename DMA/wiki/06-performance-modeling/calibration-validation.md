# 校准与验证

上级：[06 性能建模与调优](./README.md)

相关：[从抽象模型到系统诊断](./modeling-method.md)、[参数与公式速查](./parameter-reference.md)、[模型数据结构与事件规范](./model-schema.md)、[观测、计数器与调试路径](./debug-observability.md)

## 这页在回答什么问题

[modeling-method](./modeling-method.md) 讲了模型分几层，[debug-observability](./debug-observability.md) 讲了硬件该有哪些 counter，但两者中间缺一座桥：**怎么用真实 counter 把模型参数标定出来？标到什么误差才算可信？什么时候该从 L2 升到 L3？** 没有这一步，模型只是"能跑"，不是"可信"。对架构探索工具尤其关键——你拿模型做选型决策，前提是它在已知点上对得上实测。

## 校准的基本回路

```text
真实运行 / RTL 仿真
   └─ 采集 counter & 事件时间戳（按 model-schema 的规范事件）
        └─ 反推模型参数（下表）
             └─ 用同一 workload 跑模型
                  └─ 比对 Metrics，算误差
                       └─ 误差超预算 → 升层 / 补状态，回到上一步
```

关键纪律：**先校准、再外推**。模型只有在至少一个已知工作点上对齐过，才有资格去预测没跑过的设计点。

## counter → 参数 反推表

这张表是本页核心：把 [debug-observability](./debug-observability.md) 里的可观测量，映射回 [parameter-reference](./parameter-reference.md) 里的模型参数。

| 想标定的参数 | 用什么 counter / 观测 | 反推方式 |
| --- | --- | --- |
| `interconnect_RTT` / `dram_return_latency` | response latency histogram | 取分布，不是均值；P50 做主延迟，P95/P99 做尾部建模 |
| `max_outstanding`(有效值) | outstanding occupancy 高水位 | 实际高水位常低于配置值，用实测水位 |
| `efficiency`(公式 3) | read/write bytes 与 burst 分布 | useful/(useful+overhead)，按 burst 长度分布加权 |
| `row_hit_prob`(公式 4) | DRAM row hit/miss counter（若 MC 暴露） | 直接读；无 counter 时由 stride+地址映射推 |
| `completion_visibility_latency` | completion visible delay / backlog | `completion_visible - data_commit` 事件差 |
| `submit_latency` | descriptor submitted vs accepted | 两个 counter 时间差 |
| `boundary_split_penalty` | subreq_count / descriptor 数 | 实际子事务数 ÷ 理论事务数 - 1 |
| `sram_port` 冲突率 | queue full / port busy cycles | busy cycle 占比 |

无对应 counter 时的兜底：用 [parameter-reference](./parameter-reference.md) 的量级范围做先验，再用端到端带宽/延迟做整体拟合——但要在模型里标注该参数是"拟合得到"而非"实测得到"，因为它会成为外推时的主要不确定性来源。

## 各层的误差预算与代价

模型不是越精细越对，每一层有它**该达到的精度**和**该付的代价**。低于精度说明状态缺失，远高于精度说明白做了细节。

| 层次 | 典型用途 | 合理误差预算 | 主要代价 | 校准需要的最少 counter |
| --- | --- | --- | --- | --- |
| L1 上界 | 量级筛选、sanity check | 端到端带宽 ±30~50% | 几乎为零 | bytes、端点峰值带宽 |
| L2 队列-事务 | 解释 stall、定 outstanding/queue | 带宽 ±15%，P95 ±30% | 中等 | response latency 分布、outstanding 水位、completion delay |
| L3 系统耦合 | 多流冲突、尾延迟、供数断流 | 带宽 ±10%，P99 ±20% | 高（需地址映射/端口/路径） | 上述 + bank/port 冲突、row hit、ejection stall |

误差预算是**判据，不是承诺**：达到即停，别为了把 L2 误差从 12% 压到 8% 而盲目加 L3 细节——那通常意味着你该换工作点验证，而不是加状态。

## 什么时候该从 L2 升到 L3

不要凭"感觉模型不够细"升层，用量化触发器：

- **L2 误差超预算且偏差有结构**：误差不是随机噪声，而是随某个变量单调漂移（如随并发数增大系统性低估延迟）→ 缺的多半是冲突/热点，升 L3。
- **single-stream 准、multi-stream 崩**：L2 在单流对得上、多流误差骤增 → 必须显式建 NoC 注入/ejection 或 bank/port 冲突（[dma-and-noc](../05-system-integration/dma-and-noc.md)、[dma-and-memory-system](../05-system-integration/dma-and-memory-system.md)）。
- **平均对、尾部错**：均值 ±10% 但 P99 偏差 >50% → 缺 row-hit 分布或 return path 长尾，升 L3 并保留延迟分布而非均值。
- **改一个旋钮，模型方向都不对**：扫 outstanding/burst 时模型给出的趋势和实测相反 → 缺关键耦合状态，见 [sensitivity-coupling](./sensitivity-coupling.md)。

反向也成立：如果 L2 已在多个工作点稳定落在预算内，**就不该升 L3**——多出来的细节只会拖慢探索且更难解释。

## 验证（不止校准）

校准是"在已知点对齐"，验证是"在没校准过的点仍然对"。两者必须用不同数据：

1. **留出验证集**：校准用一组 workload/配置，验证用另一组，不能重叠。
2. **趋势验证优先于点值验证**：架构探索更看重"扫 burst/outstanding 时拐点位置和单调性对不对"，而不是某个单点带宽精确到 1%。
3. **外推标注不确定性**：预测远离校准点的设计时，明确哪些参数是拟合来的、外推区间多大。

## 常见误解

常见误解：`模型对了一个点就可信`。实际上那只是校准；可信要靠未校准点的验证。

常见误解：`误差越小越好，所以一律上 L3`。实际上每层有合理误差预算，达到即停，超细节是浪费且更难解释。

常见误解：`用均值校准延迟就够`。实际上尾延迟问题必须用分布校准，均值会把长尾问题藏掉。

## 一句话理解

校准是用 counter 把模型参数标到实测、并在留出点上验证趋势；模型的可信度来自"未校准点仍对"，而升层与否由误差预算和偏差结构决定，不由直觉。
