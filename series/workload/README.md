# 算法与模型：从任务机制到工作负载

<span id="workload-wiki" class="workload-legacy-anchor"></span>
<span id="写作原则" class="workload-legacy-anchor"></span>
<span id="阅读路径" class="workload-legacy-anchor"></span>
<span id="目录" class="workload-legacy-anchor"></span>

本系列连接三件事：模型解决什么问题，内部怎样计算，以及在给定配置下需要什么资源。学习路径以概念职责为主，驾驶、机器人和世界模型提供系统案例。

## 先建立四个区别

任务规定输入、输出与成功标准。网络结构规定信息怎样表示和交换。训练目标规定数据提供什么监督。执行路径规定训练或部署时实际调用哪些模块。把它们组合起来需要检查接口。例如，离散词表头可以接下一 token 的分类损失，连续速度场则需要同形状的速度目标和相应的采样器。

例如，VLA 可以使用 Transformer 骨干、模仿学习目标和 flow matching 动作头。BEVWorld 可以同时是 BEV 表示、latent 预测、diffusion 生成与视频/点云输出。分类应让这些组合能被准确表达。

## 系列地图

| 专题 | 核心问题 |
| --- | --- |
| [导读与共同基础](00-overview/README.md) | 怎样区分任务、阶段、形状与计数口径 |
| [网络组件与序列建模](01-foundation-model-components/README.md) | 骨干、融合层、注意力与专家怎样处理特征 |
| [表示学习与训练目标](learning-objectives/README.md) | 监督信号来自哪里，表示学到了什么 |
| [生成机制](generative-models/README.md) | 自回归、扩散与 Flow Matching 各学习什么，怎样生成样本 |
| [语言与多模态模型](language-and-multimodal/README.md) | token、视觉特征与语言怎样连接 |
| [视觉感知与三维场景表示](02-vision-and-3d-perception/README.md) | 从观测恢复哪些语义和空间信息 |
| [决策与策略学习](decision-and-policy/README.md) | 怎样预测、选择并执行动作 |
| [自动驾驶感知、预测与规划](03-autonomous-driving-algorithms/README.md) | 驾驶任务怎样连接感知与自车决策 |
| [机器人策略与视觉语言动作模型](04-robotics-and-vla/README.md) | 视觉语言条件怎样变成机器人动作 |
| [世界模型与环境预测](05-world-model-and-generative/README.md) | 预测哪种未来，服务训练还是规划 |
| [算法工作负载分析](06-chip-workload-analysis/README.md) | 怎样从执行图推导资源并验证瓶颈 |
| [查阅资料](07-reference/README.md) | 怎样找到概念入口、原始论文和版本 |

## 按目标选择路线

初次建立概念：先读[任务、训练与推理](00-overview/tasks-training-inference.md)，再读[张量形状](00-overview/tensor-shapes-and-cost.md)和[概念关系图](00-overview/unified-relationship-map.md)，随后按专题导读进入机制文章。

分析加速器负载：读[分析方法](06-chip-workload-analysis/workload-analysis-methodology.md)，选择一个[CNN/Transformer/SSM/MoE 或系统案例](06-chip-workload-analysis/workload-comparison-table.md)，固定形状和质量后再比较资源。

理解驾驶系统：先读[感知](02-vision-and-3d-perception/README.md)与[预测、规划、控制](decision-and-policy/prediction-planning-control.md)，再读[驾驶专题](03-autonomous-driving-algorithms/README.md)与其评估边界。

理解机器人与世界模型：先读[VLM](language-and-multimodal/vision-language-models.md)和[动作表示](04-robotics-and-vla/action-tokenizer.md)，再比较[VLA](04-robotics-and-vla/vla-fundamentals.md)与[环境预测](05-world-model-and-generative/world-model-fundamentals.md)的不同职责。

## 与整个 Wiki 的边界

硬件执行结构归于[微架构](../microarchitecture/README.md)，容量与存储路径归于[存储系统](../storage/README.md)，通信机制归于[芯片与系统互连](../interconnect/README.md)，缓存与服务调度归于[推理与运行时](../inference-runtime/README.md)。本系列通过工作负载连接这些主题，不重复编写硬件百科。

正文中的论文测量附带版本与条件；构造例标明假设；性能推论需要测量支持。新增内容以补足理解链条为准，不预设空的音频、推荐或图学习栏目。历史公开路径继续保留，当前职责以本文地图与侧栏为准。
