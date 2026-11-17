# 工作负载记录字段：让不同案例可以比较

上级：[专题导读](README.md)

<span id="workload-characterization-axes" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="统一模板" class="workload-legacy-anchor"></span>
<span id="计算密度" class="workload-legacy-anchor"></span>
<span id="访存模式" class="workload-legacy-anchor"></span>
<span id="并行性" class="workload-legacy-anchor"></span>
<span id="数据复用" class="workload-legacy-anchor"></span>
<span id="量化敏感度" class="workload-legacy-anchor"></span>
<span id="瓶颈类型" class="workload-legacy-anchor"></span>
<span id="硬件核心需求" class="workload-legacy-anchor"></span>
<span id="archax-建模口径" class="workload-legacy-anchor"></span>
<span id="算法文档的简版填写格式" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>


本页定义分析记录的字段和边界，不要求每篇机制文章复制同一张模板。机制正文只保留理解算法所需的成本说明；完整记录集中在本专题的案例中。

## 最小可复现信息

| 字段 | 应记录的内容 | 为什么需要 |
| --- | --- | --- |
| 任务与版本 | 模型、权重、实现版本、质量指标 | 避免混合不同模型或优化结果 |
| 执行阶段 | 训练、prefill、decode、采样、规划或后处理 | 同一模型各阶段的图不同 |
| 输入与动态量 | 形状、batch、长度分布、相机/点/候选数 | 规模和尾部场景决定资源 |
| 数值格式 | 权重、激活、累加器、状态及索引 | “INT8 模型”不能说明全部路径 |
| 观察边界 | 内核、设备、端到端系统 | 容量、流量与时延必须在同一范围解释 |
| 质量与时限 | 可接受误差、吞吐、分位延迟或截止时间 | 没有约束就没有可比较的优化 |

## 资源与执行字段

工作量记录 MAC/FLOP 约定；流量分别列各层级读取和写入；容量按存活区间计算。并行性要写出具体轴，依赖则写出哪些结果必须先完成。

复用应说明对象、次数与驻留位置。比如“相邻请求共享前缀”与“矩阵 tile 内复用权重”是不同机制。只写“复用高”无法支持硬件判断。

逻辑访问可以描述为连续、strided、gather/scatter 或状态更新；物理访问还需要数据布局、映射和缓存条件。规则 GEMM 不自动保证 DRAM 行命中，稀疏访问也不自动等于随机。

## 如何写瓶颈结论

建议采用“配置—证据—结论”的句式。例如：在 batch=1 且权重不驻留的配置下，权重读取下界高于计算下界；测量显示带宽接近有效上限，因此权重带宽是该阶段的主要限制。

若没有测量，只能写“带宽限制的候选原因”或“理想模型的预测”。计算、带宽、容量、串行依赖和控制开销可以同时存在，不必强行只贴一个标签。

## 架构建模不是实现证明

| 建模维度 | 可提出的问题 |
| --- | --- |
| Resource | 容量、吞吐和端口能否容纳这一配置 |
| Topology | 数据必须跨哪些节点和存储边界 |
| Interaction | 计算、搬运、状态更新与同步如何依赖 |
| Capability | 实验需要哪些算子、数据类型和执行模式 |

这些字段帮助准备实验。是否支持动态路由、稀疏算子、状态循环或某种量化，应核对目标工具版本，不能从本表推导已经实现。

分析过程与手算例见[工作负载分析方法](workload-analysis-methodology.md)；本页负责记录一致性。
