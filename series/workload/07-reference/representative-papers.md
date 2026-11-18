# 代表论文与阅读目的

上级：[专题导读](README.md)

<span id="representative-papers" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="foundation-components" class="workload-legacy-anchor"></span>
<span id="vision-and-3d-perception" class="workload-legacy-anchor"></span>
<span id="autonomous-driving" class="workload-legacy-anchor"></span>
<span id="robotics-and-vla" class="workload-legacy-anchor"></span>
<span id="world-model-and-generative" class="workload-legacy-anchor"></span>


下面只列本系列用于解释核心机制的代表来源。每篇正文提供更具体的引用。选择论文是为了回答问题，不表示完整文献覆盖或当前模型排名。

## 结构、目标与生成

| 来源 | 建议关注的问题 |
| --- | --- |
| [ResNet](https://arxiv.org/abs/1512.03385)、[ViT](https://arxiv.org/abs/2010.11929)、[Swin](https://arxiv.org/abs/2103.14030) | 局部连接、全局交互和多尺度组织 |
| [Transformer](https://arxiv.org/abs/1706.03762)、[GQA](https://aclanthology.org/2023.emnlp-main.298/)、[FlashAttention](https://arxiv.org/abs/2205.14135) | 模型结构、KV 共享与实现优化的区别 |
| [Mamba](https://arxiv.org/abs/2312.00752)、[Switch Transformer](https://jmlr.org/papers/v23/21-0998.html) | 递推状态与条件专家计算 |
| [SimCLR](https://arxiv.org/abs/2002.05709)、[CLIP](https://arxiv.org/abs/2103.00020) | 样本关系如何定义表示 |
| [MAE](https://arxiv.org/abs/2111.06377)、[BYOL](https://arxiv.org/abs/2006.07733)、[I-JEPA](https://arxiv.org/abs/2301.08243) | 重建、蒸馏与目标表示预测 |
| [DDPM](https://arxiv.org/abs/2006.11239)、[Flow Matching](https://arxiv.org/abs/2210.02747) | 训练目标与采样求值 |
| [LLaVA](https://arxiv.org/abs/2304.08485)、[Flamingo](https://arxiv.org/abs/2204.14198) | 视觉特征与语言模型的连接 |

## 感知、驾驶与机器人

| 来源 | 建议关注的问题 |
| --- | --- |
| [DETR](https://arxiv.org/abs/2005.12872)、[Mask R-CNN](https://arxiv.org/abs/1703.06870) | 集合检测与实例掩码的接口 |
| [LSS](https://arxiv.org/abs/2008.05711)、[BEVFormer](https://arxiv.org/abs/2203.17270)、[BEVPoolv2](https://arxiv.org/abs/2211.17111) | 几何提升、查询采样与中间物化 |
| [Occ3D](https://arxiv.org/abs/2304.14365)、[UniAD](https://arxiv.org/abs/2212.10156) | 空间监督与规划导向任务连接 |
| [DAgger](https://arxiv.org/abs/1011.0686)、[NAVSIM](https://arxiv.org/abs/2406.15349) | 分布偏移与评估反馈边界 |
| [RT-1 v1](https://arxiv.org/html/2212.06817v1)、[RT-2 v1](https://arxiv.org/html/2307.15818v1) | 机器人训练与视觉语言预训练 |
| [OpenVLA v3](https://arxiv.org/html/2406.09246v3)、[FAST v1](https://arxiv.org/html/2501.09747v1) | 原始动作分箱与时间压缩 |
| [π0 v1](https://arxiv.org/html/2410.24164v1)、[GR00T N1 v2](https://arxiv.org/html/2503.14734v2) | 连续动作块与执行频率 |

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 世界模型与成本

| 来源 | 建议关注的问题 |
| --- | --- |
| [DreamerV3 v2](https://arxiv.org/html/2301.04104v2) | 对照想象训练与真实交互中的观测编码、状态更新和 actor |
| [V-JEPA 2 v1](https://arxiv.org/html/2506.09985v1) | 无动作预训练与动作条件规划 |
| [BEVWorld v3](https://arxiv.org/html/2407.05679v3)、[OccWorld](https://arxiv.org/abs/2311.16038) | 表示、生成机制与输出交叉组合 |
| [GAIA-1](https://arxiv.org/abs/2309.17080)、[Genie](https://arxiv.org/abs/2402.15391)、[ReSim](https://arxiv.org/abs/2506.09981) | 生成环境的条件与评估用途 |
| [NVIDIA GEMM 指南](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html) | 计算量、流量与硬件上界 |
| [Efficiently Scaling Transformer Inference](https://arxiv.org/abs/2211.05102) | 长度、batch、并行方案和设备条件 |

涉及具体测量时使用已标注的版本。最新版本可能包含改动，不能将新结果回填到旧实验配置；见[来源与版本记录](source-tracking.md)。
