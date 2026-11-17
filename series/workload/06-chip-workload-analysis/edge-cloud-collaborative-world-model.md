# 世界模型的端云协作：按调用时限划分职责

上级：[专题导读](README.md)

<span id="edge-cloud-collaborative-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="职责拆分与背后的-workload-性格" class="workload-legacy-anchor"></span>
<span id="连接的瓶颈协同不是免费的" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


端云分工应由时限、数据量、质量目标和连接条件决定。端侧可能运行状态估计、策略或候选预测；云端可能训练、生成数据和批量评测。没有一种表示天然固定属于某一侧。

## 三种可比较的方案

| 方案 | 适用条件 | 收益 | 代价 |
| --- | --- | --- | --- |
| 本地策略，云端训练与评测 | 在线链路要求稳定响应 | 控制不依赖每次网络往返 | 本地容量受限，更新要管理版本 |
| 本地编码，远端生成或规划 | 时限允许且连接可用 | 可使用远端大模型 | 网络尾延迟、传输量与状态陈旧 |
| 本地预测，云端提供离线先验或数据 | 需低延迟但训练资源大 | 复用离线学习成果 | 模型偏差与数据迁移仍需验证 |

这是设计选项比较，不是现有产业形态的统计结论。

## 远端调用的预算

远端响应时间至少包括上行、排队、推理、下行和本地处理。构造上行 15 ms、排队 10 ms、推理 40 ms、下行 15 ms，总计 80 ms，尚未计本地编码与执行。若控制预算为 50 ms，该配置即使远端算力充足也不满足。

平均网络延迟不足以决定可用性。需要测试尾延迟、丢包和过期结果，并定义未及时收到结果时系统如何继续。具体降级机制属于系统设计，不应由模型论文暗示已有。

## 日志与模型更新

离线闭环需要记录输入、动作、结果和版本，才能复现失败。新模型上线前应通过独立回归；模型、归一化统计量和动作接口必须成套更新。

生成数据的价值要在目标任务验证，不能只按生成数量计算。数据闭环方法见[驾驶数据与仿真](../03-autonomous-driving-algorithms/data-closed-loop-and-simulation.md)。

## 为什么表示名称不能决定位置

Latent 模型也可能包含昂贵候选搜索；视频模型也可能通过压缩、短时域或设备优化满足某类任务。部署位置必须用完整配置和测量支持。

本页只比较职责与接口。模型机制归于[世界模型专题](../05-world-model-and-generative/README.md)，调用次数归于[世界模型工作负载](world-model-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [V-JEPA 2-AC：规划实验的实际调用成本](https://arxiv.org/html/2506.09985v1)
- [RT-2：特定云端机器人实验](https://arxiv.org/html/2307.15818v1)
