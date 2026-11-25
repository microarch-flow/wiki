# 从驾驶与机器人负载到架构实验

上级：[专题导读](README.md)

<span id="ad-and-robotics-chip-architecture-summary" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="核心结论真实系统是-workload-的组合不是单一-workload" class="workload-legacy-anchor"></span>
<span id="workload-到架构的映射表" class="workload-legacy-anchor"></span>
<span id="对七份硬件-wiki-的要求" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>


算法分析的结果应是一组可验证的资源与执行假设，而不是直接宣布某种芯片结构最好。比较架构前，先固定任务质量与运行约束，再选择能区分候选设计的实验。

## 用代表性变化覆盖工作点

| 工作点 | 建议改变的变量 | 观察对象 |
| --- | --- | --- |
| 视觉骨干 | 分辨率、通道、batch | 利用率、权重与特征复用 |
| BEV / occupancy | 网格、深度、历史、活跃率 | 采样流量、容量、索引开销 |
| 自回归生成 | 上下文、并发、KV 精度 | 权重/KV 流量、状态容量 |
| VLA / 世界模型 | 执行块、候选、NFE、预测时域 | 串行链、条件复用、反馈延迟 |
| SSM / MoE | 状态宽度、路由分布、专家布局 | scan、负载均衡与通信 |

这些变化比为每类模型指定一个“固定瓶颈”更能暴露设计边界。

## 三类架构取舍

增加计算吞吐只有在算子能利用它、且数据供应充分时才有效。增加片上容量可能减少重复搬运，但收益取决于存活集合和映射。增加互连带宽可缓解通信，却不能消除串行依赖或错误的任务划分。

构造例：两种设计峰值算力相同，一种容纳整个常用状态，另一种每步都要从片外载入。对状态更新负载，两者可能明显不同；对大批量无状态 GEMM，差异可能缩小。需要通过对应实验确认。

<span id="archax-总结探索空间不该只扫-tops" class="workload-legacy-anchor"></span>

## 向 Archax 等工具提交什么

准备模型版本与形状、算子依赖图、各存储边界的流量假设、资源容量和连接方式，以及质量/时延目标。将未知项列成敏感性范围。

Resource、Topology、Interaction、Capability 可作为组织实验说明的维度，但是否能表达动态路由、循环、稀疏执行或特定精度，应查当前工具契约。本文不把需求列表当成已实现能力。

## 怎样报告结论

区分解析估算、模拟结果、软件内核测量和真实系统测量。模拟结果只能在建模假设成立时解释系统；单次成功也不证明全局最优或所有场景满足截止时间。

本页收束实验设计。具体硬件机制留给[计算微架构](../../microarchitecture/README.md)、[存储系统](../../storage/README.md)和[芯片与系统互连](../../interconnect/README.md)系列，避免在算法文章中重复讲解。
