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
| [世界模型与环境预测](05-world-model-and-generative/README.md) | 用什么表示预测未来，怎样服务训练或规划 |
| [自动驾驶感知、预测与规划](03-autonomous-driving-algorithms/README.md) | 驾驶任务怎样连接感知与自车决策 |
| [机器人策略与视觉语言动作模型](04-robotics-and-vla/README.md) | 视觉语言条件怎样变成机器人动作 |
| [算法工作负载分析](06-chip-workload-analysis/README.md) | 怎样从执行图推导资源并验证瓶颈 |
| [查阅资料](07-reference/README.md) | 怎样找到概念入口、原始论文和版本 |

## 按目标选择路线

初读从[任务、训练与推理](00-overview/tasks-training-inference.md)和[张量形状](00-overview/tensor-shapes-and-cost.md)开始。用[概念关系图](00-overview/unified-relationship-map.md)定位问题，再按目标选择一条路线。

**理解视觉感知。** 沿[网络组件导读](01-foundation-model-components/README.md)从 CNN 读到多尺度融合，再读 Attention 和 ViT/Swin。带着同一张图进入[感知专题](02-vision-and-3d-perception/README.md)，分别看模型怎样输出框、像素标签或鸟瞰网格。需要理解多相机驾驶时，先走通 [BEV 的投影与汇聚](02-vision-and-3d-perception/bev-perception.md)，再读[驾驶系统](03-autonomous-driving-algorithms/README.md)。

**理解语言和动作生成。** 从 [Attention](01-foundation-model-components/attention-and-transformer.md) 转到[自回归的错位预测](generative-models/autoregressive-generation.md)，再走通[语言模型](language-and-multimodal/language-models.md)、[图文模型](language-and-multimodal/vision-language-models.md)和 [VLA 的动作接口](04-robotics-and-vla/vla-fundamentals.md)。若要读连续动作头，先核对[扩散的一步更新](generative-models/diffusion-models.md)和 [Flow Matching 的积分](generative-models/flow-matching.md)，再比较[动作表示与生成](04-robotics-and-vla/action-tokenizer.md)。

**理解策略和世界模型。** 先分清[预测、规划与控制](decision-and-policy/prediction-planning-control.md)，再看[示范动作和回报怎样更新策略](decision-and-policy/imitation-and-reinforcement-learning.md)。进入[世界模型基础](05-world-model-and-generative/world-model-fundamentals.md)后，沿 [Dreamer 或 CEM](05-world-model-and-generative/latent-world-model.md) 追到一次真实动作。若关心规划用的状态如何学得，可先读[自蒸馏](learning-objectives/masked-reconstruction-and-distillation.md)和 [JEPA 表征预测](learning-objectives/jepa-and-self-supervised.md)。最后选择[机器人接触](04-robotics-and-vla/robot-world-model.md)或[驾驶交互](03-autonomous-driving-algorithms/world-model-for-ad.md)核对反馈条件。

**分析资源需求。** 先用[张量算例](00-overview/tensor-shapes-and-cost.md)区分容量和流量，再读[工作负载分析方法](06-chip-workload-analysis/workload-analysis-methodology.md)。从[对照索引](06-chip-workload-analysis/workload-comparison-table.md)选择刚学过的一种机制，固定阶段、形状和精度，计算其工作量与读写量。可以从四个提示 token 的 [Transformer 算例](06-chip-workload-analysis/transformer-workload.md#同一层的两次前向)开始。

## 与整个 Wiki 的边界

硬件执行结构归于[计算微架构](../microarchitecture/README.md)，容量与存储路径归于[存储系统](../storage/README.md)，通信机制归于[芯片与系统互连](../interconnect/README.md)，缓存与服务调度归于[推理运行时](../inference-runtime/README.md)。本系列通过工作负载连接这些主题，不重复编写硬件百科。

正文中的论文测量附带版本与条件；构造例标明假设；性能推论需要测量支持。新增内容以补足理解链条为准，不预设空的音频、推荐或图学习栏目。历史公开路径继续保留，当前职责以本文地图与侧栏为准。
