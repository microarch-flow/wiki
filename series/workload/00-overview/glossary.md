# 术语与单位：本系列的统一口径

上级：[专题导读](README.md)

<span id="glossary" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="算法与系统范式" class="workload-legacy-anchor"></span>
<span id="workload-刻画维度" class="workload-legacy-anchor"></span>
<span id="硬件与-archax-术语" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


本表提供简明定义。机制、条件和反例由链接到的主文解释。

## 任务与模型

| 术语 | 本系列用法 |
| --- | --- |
| Backbone / 骨干 | 提取可复用特征的网络部分；不等于完整任务模型 |
| Neck | 组织或融合骨干特征，常用于多尺度输出 |
| Token | 模型处理的序列单元；可以是离散 ID，也可以是连续向量 |
| Latent | 学习到的内部表示，不保证低维、无损或无 decoder |
| BEV | 鸟瞰坐标中的空间组织方式 |
| Occupancy | 空间占用估计；空闲与未知不能混同 |
| VLM / VLA | 视觉语言模型 / 视觉语言动作模型 |
| World model | 环境演化模型；预测对象与用途须另行说明 |

## 学习与执行

| 术语 | 本系列用法 |
| --- | --- |
| 自监督 | 监督信号主要从数据自身构造，不等于不使用损失或训练目标 |
| 行为克隆 BC | 以专家动作或轨迹监督策略 |
| Policy / 策略 | 根据观测或状态选择动作的规则或模型 |
| Planning / 规划 | 根据目标、预测与约束选择未来行为 |
| Rollout | 沿时间展开状态或交互；注明真实环境还是模型内部 |
| Horizon / 时域 | 预测或优化覆盖的时间范围；不能与执行长度混用 |
| Action chunk | 一次预测的一段动作，实际执行可只取前缀 |
| NFE | 网络函数求值次数；可能不同于求解器步数 |
| Prefill / decode | 自回归模型的提示处理 / 追加生成阶段 |
| KV cache | 保存历史 key/value 的状态；不是权重缓存 |

## 数量与评价

| 术语 | 本系列口径 |
| --- | --- |
| MAC | 一次乘加；默认计为 2 FLOP |
| FLOP / FLOP/s | 浮点工作量 / 每秒处理速率 |
| 算术强度 | 工作量除以指定存储边界的字节流量 |
| 容量 / 流量 | 同时驻留的数据量 / 测量区间内跨边界传输总量 |
| MB、GB | 十进制字节单位，$10^6$ B、$10^9$ B |
| MiB、GiB | 二进制字节单位，$2^{20}$ B、$2^{30}$ B |
| 延迟 / 吞吐 | 单次完成所需时间 / 单位时间完成数量 |
| p99 | 延迟分布的第 99 百分位；不是最坏执行时间上界 |
| 开放环 / 闭环 | 预测不改变后续环境 / 动作反馈影响后续状态；还需说明环境反应能力 |

形状和算术量见[计数基础](tensor-shapes-and-cost.md)，执行字段见[工作负载记录](../06-chip-workload-analysis/workload-characterization-axes.md)。
