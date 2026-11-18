# 算法与模型 · 第二轮重构记录（2026-11-18）

本轮以 Git 提交 `9b35860` 发布的 86 页为基线。复核后保留 12 个专题，修改其中 42 篇正文与导读。改动分为四批，依次处理机制和分类、12 个基础算例、跨模型执行过程、阅读路线与历史兼容。上一轮的范围和当时的检查结果见[第一次重构记录](workload-reconstruction-report.md)。

## 12 个基础缺口与复算结果

下表中的数值均来自正文构造例。复算使用 Python 标准库。每行对应一项独立测试，其中梯度用有限差分复核，规划和路由用逐项枚举复核。[算例测试源码](../website/tests/test_workload_examples.py)

| 主文 | 读完可以自己完成的计算 |
| --- | --- |
| [任务、训练与推理](../series/workload/00-overview/tasks-training-inference.md) | 对同一样本求损失、梯度，做一步参数更新。权重从 1 变为 1.2，训练损失从 0.5 降到 0.18，再用更新后的权重推理。 |
| [张量形状与计算量](../series/workload/00-overview/tensor-shapes-and-cost.md) | 对两行特征广播同一偏置，沿特征轴求和得到 66、75。用一个线性层分别算出 384 FLOP、208 B 和 1.85 FLOP/B。用步长 2 的卷积从输入高 7 推到输出高 4。 |
| [MoE 路由](../series/workload/01-foundation-model-components/mixture-of-experts.md) | 选择前两个专家并重新归一化，合并值为 6。换成 top-1 并限制每个专家接收两个 token，可以找出溢出的分配和保留的残差通路。 |
| [掩码重建与自蒸馏](../series/workload/learning-objectives/masked-reconstruction-and-distillation.md) | MAE 的 16 块中有 4 块进入编码器，按 12 块遮挡区算出损失 1/3。用 BYOL 算出归一化向量误差 0.8 和教师权重 1.04，再与 DINO 的教师分布、中心化及温度对照。 |
| [自回归生成](../series/workload/generative-models/autoregressive-generation.md) | 排齐输入“BOS、红、杯、在”和标签“红、杯、在、桌上”。逐行检查可见前缀，再用模型自己选的 token 续写一步。 |
| [Flow Matching](../series/workload/generative-models/flow-matching.md) | 两条构造路径在同一时刻经过同一点，目标速度为 2 和 4。等概率与平方误差下，最优预测为 3。一步欧拉积分将 1 更新到 1.3。 |
| [语言模型](../series/workload/language-and-multimodal/language-models.md) | 从 token ID 走到形状为 `[2,4,30]` 的词表分数。比较对所有位置训练的 240 个分数与每条序列仅取末位置的 60 个分数。 |
| [视觉语言模型](../series/workload/language-and-multimodal/vision-language-models.md) | 以早期 LLaVA 的投影接口为例，将 196 个视觉位置接到 3 个问题 token 之前。对齐回答“红、杯、EOS”的预测位置，区分输入掩码、损失掩码和冻结参数。 |
| [预测、规划与控制](../series/workload/decision-and-policy/prediction-planning-control.md) | 对两组动作展开状态，得到代价 0.125、1.025。只下发所选序列的首步，下一周期按实测位置重算，再由控制器给出受限命令。 |
| [模仿学习与强化学习](../series/workload/decision-and-policy/imitation-and-reinforcement-learning.md) | 用两个时间步的延迟奖励求回报和优势，更新采样动作的概率（0.500 → 0.525）与价值估计（1 → 1.1）。对照示范学习需要的动作标签。 |
| [SSM 工作负载](../series/workload/06-chip-workload-analysis/ssm-workload.md) | 手算一个对角递推及读出，再比较逐步更新与仿射前缀扫描。指定维度、精度与存储边界后，一步为 20,224 FLOP，持久状态 8 KiB，读写各一次合计 16 KiB。 |
| [MoE 工作负载](../series/workload/06-chip-workload-analysis/moe-workload.md) | 四个 token 经 top-2 产生八次分配。专家执行 4,096 FLOP，加权合并另需 96 FLOP。给定两个设备的放置后，128 B 的单向逻辑载荷中有 32 B 跨设备。 |

## 其他正文的职责

| 阅读问题 | 对应修改 |
| --- | --- |
| 图像和序列经过哪些网络组件 | [Attention](../series/workload/01-foundation-model-components/attention-and-transformer.md) 衔接视觉、语言两条路线。[ViT/Swin](../series/workload/01-foundation-model-components/vision-transformer-backbone.md) 区分可逆切块、投影秩和后续合并。[注意力变体](../series/workload/01-foundation-model-components/attention-variants-and-efficiency.md) 解释 GQA 共享关系。[Mamba](../series/workload/01-foundation-model-components/mamba-and-ssm.md) 区分选择性递推与整个模块的运算。 |
| 怎样重建空间或生成样本 | [BEV 感知](../series/workload/02-vision-and-3d-perception/bev-perception.md) 让两个像素的四个深度假设投到三个网格，并与 BEVFormer 从网格取样对照。[扩散模型](../series/workload/generative-models/diffusion-models.md) 从网络的噪声估计走完 DDPM 最后两步。[动作表示与生成](../series/workload/04-robotics-and-vla/action-tokenizer.md) 说明每轮求值更新哪个动作块。 |
| 如何描述和使用世界模型 | [概念关系图](../series/workload/00-overview/unified-relationship-map.md) 说明模型属性可以兼有。[世界模型基础](../series/workload/05-world-model-and-generative/world-model-fundamentals.md) 用内部表示、预测机制、条件、输出、用途说明一个模型。[BEVWorld](../series/workload/05-world-model-and-generative/bev-world-model.md) 展开历史编码、动作条件预测和观测解码。[Latent 世界模型](../series/workload/05-world-model-and-generative/latent-world-model.md) 对照 DreamerV3 的真实观测更新、想象训练和 V-JEPA 2-AC 的在线候选规划。[原扩散世界模型页](../series/workload/05-world-model-and-generative/diffusion-for-world-model.md) 将旧章节定位到对应主文。 |
| 驾驶与机器人各自要求什么反馈 | [驾驶世界模型](../series/workload/03-autonomous-driving-algorithms/world-model-for-ad.md) 说明其他交通主体能否响应自车动作。[数据闭环与仿真](../series/workload/03-autonomous-driving-algorithms/data-closed-loop-and-simulation.md) 用提前刹车分开观测生成与主体反应。[机器人世界模型](../series/workload/04-robotics-and-vla/robot-world-model.md) 处理接触、感知反馈和控制时限。 |
| 怎样从模型推到资源 | [工作负载方法](../series/workload/06-chip-workload-analysis/workload-analysis-methodology.md) 区分时间下界及接近下界的条件。[Transformer 工作负载](../series/workload/06-chip-workload-analysis/transformer-workload.md) 用同一层算四词元 prefill 和下一次 decode。[世界模型工作负载](../series/workload/06-chip-workload-analysis/world-model-workload.md) 按实际调用图计算候选数、时间位置和网络求值次数。 |
| 怎样回查原始证据 | [代表论文](../series/workload/07-reference/representative-papers.md) 按要回答的问题给出论文入口。[来源记录](../series/workload/07-reference/source-tracking.md) 保留模型版本、作者报告的测量条件和待测结论。 |

## 阅读顺序与旧链接

[系列总导读](../series/workload/README.md) 提供视觉、语言与动作、策略与世界模型、工作负载四条路线。下列导读与网站侧栏使用同一顺序。

- [共同基础](../series/workload/00-overview/README.md) 把原索引放入历史入口。[网络组件](../series/workload/01-foundation-model-components/README.md) 在 ViT/Swin 前先讲 Attention。
- [生成机制](../series/workload/generative-models/README.md) 连接训练目标与采样过程。[语言与多模态](../series/workload/language-and-multimodal/README.md) 从错位标签接到语言模型、图文模型。
- [世界模型](../series/workload/05-world-model-and-generative/README.md) 放在决策之后、系统案例之前。[自动驾驶](../series/workload/03-autonomous-driving-algorithms/README.md) 与 [机器人](../series/workload/04-robotics-and-vla/README.md) 分别接到交通反馈与操作闭环。
- [工作负载](../series/workload/06-chip-workload-analysis/README.md) 保留资源分析主线。[查阅资料](../series/workload/07-reference/README.md) 收纳索引。两个专题都将兼容入口移出顺读列表。

源码持续位于 `series/workload/`。7 篇已迁移源码的正文继续使用历史公开路径。搜索收录 79 页，另有 7 页经各专题的“历史入口”可达。源码位置映射和兼容页清单分别查[构建映射](../website/workload.py)和[兼容性测试](../website/tests/test_workload_refinement.py)。两组清单按页保护第一次重构前的 610 个正文 ID，以及本轮开始前另外发布的 451 个正文 ID。

## 验证范围

全站使用 Python 3.12 准备页面，MkDocs 严格构建通过，`website/tests` 中 113 项测试通过。其中 12 项复算上表，另有 5 项复算 DDPM、BEV、真实状态估计、CEM 和 Transformer 阶段计数。站点自带的 KaTeX 严格解析了本系列 430 处公式。

本地 Chromium 在 1440 × 960 和 390 × 844 两种视口分别打开 86 页，检查公式、表格、面包屑、当前导航及 5 幅 Mermaid 图。手机上可从扩散世界模型旧锚点打开历史目录，返回世界模型基础。BEV 表格在容器内可滚动 144 像素，页面保持 390 像素宽。两种视口搜索“CEM”“SSM”“强化学习”都能找到对应主文。发布提交、Actions 运行和公开站点验收结果随本次交付提供。

技术事实与原论文对照。算例验证给定前提下的计算关系。论文中的时延、训练结果和闭环成功率沿用各自实验条件，本轮未在目标硬件、车辆或机器人上独立测量。
