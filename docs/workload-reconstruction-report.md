# Workload Wiki 重构记录（2026-11-17）

本次按已确认的方案 B 重构“算法与模型”系列，并补齐全部 12 个基础缺口。源码、网站导航和阅读顺序统一为 12 个专题。原有 70 页均完成调整，新增 12 篇基础正文和 4 篇专题导读，共 86 页。其中 6 页作为兼容入口保留，80 页进入搜索。

本记录说明提交前的内容范围和验证结果。部署提交、GitHub Actions 运行及公开站点验收结果见本任务最终交付回复；不要把本地构建结果当作线上发布证明。

## 组织与去重

- 将骨干结构、训练目标、生成机制、系统任务和执行实例分开。CNN、对比学习、VLA 和世界模型不再作为同一层的互斥算法。
- 机制文章解释输入、输出、状态、过程和边界。完整成本记录集中到工作负载专题，减少各篇重复的背景、通用模板和无来源的趋势预测。
- 驾驶、机器人和世界模型保留为系统案例。推理服务的缓存调度、硬件存储机制和互连实现通过链接进入既有系列。
- 总导读维护阅读路线；查阅资料维护问题索引、论文及版本。旧研究问题、路线与重复辨析页保留为兼容入口，并从搜索排除。
- 历史来源台账原文保存在 [历史档案](archive/workload/source-tracking-20260607.md)。文章旧文继续可从 Git 历史读取。

## 主要技术修正

| 问题 | 本次口径 |
| --- | --- |
| Attention 与访存 | 内容权重变化不等于随机地址；稠密连接、KV 头共享、FlashAttention 的 IO 优化分别解释。数学等价不声称位级完全一致。 |
| 计算量和流量 | 明确 1 MAC 按 2 FLOP 计数，写出维度和存储边界；逻辑张量大小不直接当作 HBM 实测流量。 |
| BEV 与占用 | BEV 是空间表示；未知不等于空闲；LSS 的中间展开不是所有 BEV 实现的必需步骤。 |
| 驾驶方法 | BC 是训练方式，规划是职责；端到端和共享 BEV 是不同组织维度。非反应式离线评测不直接证明闭环表现。 |
| 机器人模型 | 固定论文版本与设备。修正 RT-1 预训练和输出依赖、RT-2 配置、OpenVLA 七维动作的含义、GR00T N1 模型与节拍口径。 |
| 动作编码和频率 | FAST 的 DCT/量化与 BPE 分层解释；动作执行频率、动作块长度和模型调用频率分别计数。π0 的计时仅用于原实验配置。 |
| 世界模型 | 表示、机制、条件和用途正交。DreamerV3 的想象训练不同于部署候选搜索；V-JEPA 2 与 2-AC 分开；latent 不意味着无解码器或无采样。 |
| 调用量与延迟 | 候选数、时间位置和采样求值数按实际调用图计数。一次序列求值已覆盖的时间轴不得重复相乘；工作量不等于墙钟时延。 |
| 架构结论 | Roofline 只给指定条件下的上界；p99 不代替 WCET；架构需求和待测假设不描述为已有 Archax 能力。 |

关键证据以原始论文、官方项目和厂商文档为主。具体版本与核查说明见 [来源记录](../series/workload/07-reference/source-tracking.md)。正文明确区分论文报告、构造算例和待测性能结论。

## 提交前验证

- 执行 `python website/prepare.py`、`mkdocs build --strict` 和完整网站测试；89 项测试通过。
- 自动检查 86 页的正文内部链接、目标锚点、canonical、导航覆盖和源码映射；页面在主导航中恰好出现一次。
- 以重构前站点为基线，验证 70 个旧公开路径及 610 个正文锚点均保留且只出现一次。
- 搜索索引收录 80 页，保留完整文章标题；6 个兼容入口不收录。浏览器搜索能检出新增 MoE 机制及工作负载文章。
- 使用仓内 KaTeX 严格解析全部 249 个数学表达式，无解析错误。公式数含重复出现的表达式，不等同于独立公式数。
- 在 1280 像素桌面与 390 像素手机视口检查标题、面包屑、当前项高亮、抽屉导航、搜索、公式、表格和全部 5 张 Mermaid。概念与世界模型图使用简短的分行节点；语言模型和规划反馈图采用纵向布局，避免窄屏压缩文字。
- 使用隔离 worktree 处理本任务，先整合并验证主分支同期的微架构修改；未将其他未提交或未跟踪文件纳入提交。

## 路径兼容

源码移动只改变维护位置。下表的公开路径保持不变，导航按当前专题归属。新旧源码相对引用由构建阶段统一映射。

| 当前源码（相对 `series/workload/`） | 保留的公开路径（相对 `/wiki/external/workload-wiki/`） |
| --- | --- |
| `learning-objectives/contrastive-learning.md` | `01-foundation-model-components/contrastive-learning/` |
| `learning-objectives/jepa-and-self-supervised.md` | `01-foundation-model-components/jepa-and-self-supervised/` |
| `generative-models/diffusion-models.md` | `01-foundation-model-components/diffusion-models/` |
| `decision-and-policy/robotics-vs-autonomous-driving.md` | `04-robotics-and-vla/robotics-vs-autonomous-driving/` |
| `06-chip-workload-analysis/edge-cloud-collaborative-world-model.md` | `05-world-model-and-generative/edge-cloud-collaborative-world-model/` |
| `06-chip-workload-analysis/workload-lens.md` | `00-overview/workload-lens/` |
| `06-chip-workload-analysis/workload-comparison-table.md` | `07-reference/workload-comparison-table/` |

旧锚点以 `workload-legacy-anchor` 保留在对应正文位置。兼容基线在 `website/tests/fixtures/workload-legacy.json`；导航和映射在 `website/workload.py`，行为测试在 `website/tests/test_workload_refinement.py`。

## 逐篇内容边界

“新增”只标记本轮补齐的 12 篇基础正文。四篇新专题导读另外列入对应专题；其他导读和入口均已同步调整。

| 页面 | 内容边界 |
| --- | --- |
| [系列总导读](../series/workload/README.md) | 系列地图、四条阅读路线和与整个 Wiki 的分工。 |

### 导读与共同基础

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/00-overview/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [从任务到模型：训练、推理与评估各解决什么问题](../series/workload/00-overview/tasks-training-inference.md)（新增） | 任务输入输出、训练与推理、离线指标与部署评估。 |
| [张量形状与计算量：从一个线性层建立计数口径](../series/workload/00-overview/tensor-shapes-and-cost.md)（新增） | 形状语义、MAC/FLOP、字节与一次读写的线性层算例。 |
| [概念关系图：任务、结构、目标与执行不是同一层](../series/workload/00-overview/unified-relationship-map.md) | 分清任务、结构、训练目标、生成机制和执行阶段。 |
| [术语与单位：本系列的统一口径](../series/workload/00-overview/glossary.md) | 统一术语、阶段、单位及计数口径；机制解释链接到主文。 |
| [研究问题：原入口](../series/workload/00-overview/research-questions.md) | 兼容旧研究问题入口；主问题与分类转到总导读。 |
| [系列建设与阅读路线：原入口](../series/workload/00-overview/wiki-roadmap.md) | 兼容旧建设路线；当前边界由总导读维护。 |
| [代表工作索引：原入口](../series/workload/00-overview/representative-works-index.md) | 兼容旧索引；论文清单集中到查阅资料。 |

### 骨干网络与序列建模

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/01-foundation-model-components/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [CNN 骨干：局部卷积如何形成多尺度特征](../series/workload/01-foundation-model-components/cnn-backbone.md) | 卷积、感受野与分层特征；任务头另述。 |
| [ViT 与 Swin：图像如何变成 token 序列](../series/workload/01-foundation-model-components/vision-transformer-backbone.md) | patch、ViT、窗口注意力、Swin 层级与 token 数。 |
| [多尺度特征融合：FPN 为什么连接不同分辨率](../series/workload/01-foundation-model-components/neck-feature-fusion.md) | FPN 的自顶向下路径、横向连接和尺度对齐。 |
| [Attention 与 Transformer：从加权读取到一个完整 block](../series/workload/01-foundation-model-components/attention-and-transformer.md) | 从 Q/K/V 加权读取到完整 block；解释矩阵形状与计算量。 |
| [Attention 效率：哪些方法改变计算，哪些改变实现](../series/workload/01-foundation-model-components/attention-variants-and-efficiency.md) | 区分连接稀疏、KV 头共享、IO 优化与缓存管理。 |
| [Mamba 与状态空间模型：用递推状态处理序列](../series/workload/01-foundation-model-components/mamba-and-ssm.md) | 递推状态、选择性参数与扫描；区分结构和执行方式。 |
| [MoE：如何为每个 token 选择一部分专家](../series/workload/01-foundation-model-components/mixture-of-experts.md)（新增） | 路由、专家、加权合并、负载均衡与容量限制。 |

### 表示学习与训练目标

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/learning-objectives/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [对比学习：用样本关系定义表示空间](../series/workload/learning-objectives/contrastive-learning.md) | 样本关系、InfoNCE、负样本条件与部署输出。 |
| [掩码重建与自蒸馏：监督目标来自哪里](../series/workload/learning-objectives/masked-reconstruction-and-distillation.md)（新增） | 比较 MAE、BYOL、DINO 的目标来源与防坍塌机制。 |
| [JEPA：预测目标表示，而非重建每个像素](../series/workload/learning-objectives/jepa-and-self-supervised.md) | 表征预测、目标编码器与坍塌约束；不等同于所有自监督。 |

### 自回归与扩散生成

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/generative-models/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [自回归生成：从条件概率到下一个 token](../series/workload/generative-models/autoregressive-generation.md)（新增） | 条件概率分解、teacher forcing、逐 token 生成与缓存。 |
| [扩散模型：学习去噪，再逐步生成样本](../series/workload/generative-models/diffusion-models.md) | 前向加噪、训练目标、反向采样和求值次数。 |
| [Flow Matching：学习把噪声变成样本的速度场](../series/workload/generative-models/flow-matching.md)（新增） | 条件路径、速度场目标与 ODE 采样；步数不等同于求值次数。 |

### 语言与多模态模型

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/language-and-multimodal/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [语言模型：从 token ID 到下一词元分布](../series/workload/language-and-multimodal/language-models.md)（新增） | token、嵌入、语言骨干和词表输出；不同结构的边界。 |
| [视觉语言模型：图像表示怎样进入语言计算](../series/workload/language-and-multimodal/vision-language-models.md)（新增） | 视觉和语言的表示接口；对比、投影接入与交叉注意力。 |

### 视觉感知与三维场景表示

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/02-vision-and-3d-perception/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [目标检测：从图像到目标集合](../series/workload/02-vision-and-3d-perception/object-detection.md) | 框与集合输出、标签匹配、NMS 和 DETR 的适用边界。 |
| [语义分割：为每个位置分配类别](../series/workload/02-vision-and-3d-perception/semantic-segmentation.md) | 逐位置类别、编码解码和分辨率；不提供个体身份。 |
| [实例分割：把同类目标分成不同个体](../series/workload/02-vision-and-3d-perception/instance-segmentation.md) | 实例身份和掩码输出；比较 proposal 和 query 路线。 |
| [视频理解：时间采样如何改变模型看到的问题](../series/workload/02-vision-and-3d-perception/video-understanding.md) | 已有视频的时空采样与理解；区分因果和双向输入。 |
| [LiDAR 点云：从不规则采样到可计算的空间表示](../series/workload/02-vision-and-3d-perception/lidar-point-cloud-processing.md) | 点、体素、pillar 与稀疏表示；采样密度及索引成本。 |
| [BEV 感知：把多视角观测对齐到地面坐标](../series/workload/02-vision-and-3d-perception/bev-perception.md) | 坐标对齐与视角变换；比较 LSS、BEVFormer、PETR。 |
| [多传感器融合：先对齐证据，再组合表示](../series/workload/02-vision-and-3d-perception/multi-sensor-fusion.md) | 时空标定、融合层次与缺失或冲突证据。 |
| [Occupancy 感知：已占用、空闲与未知空间](../series/workload/02-vision-and-3d-perception/occupancy-prediction.md) | 当前空间的占用、空闲、未知及可见性掩码。 |

### 决策与策略学习

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/decision-and-policy/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [预测、规划、策略与控制：从观测到执行的边界](../series/workload/decision-and-policy/prediction-planning-control.md)（新增） | 预测、规划、策略与控制的输入输出和闭环职责。 |
| [模仿学习与强化学习：动作监督和回报分别怎样使用](../series/workload/decision-and-policy/imitation-and-reinforcement-learning.md)（新增） | BC、分布偏移、DAgger、回报与强化学习的训练接口。 |
| [机器人与自动驾驶：相同决策闭环，不同动作接口](../series/workload/decision-and-policy/robotics-vs-autonomous-driving.md) | 比较动作空间、动力学、观测与执行约束。 |

### 自动驾驶感知、预测与规划

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/03-autonomous-driving-algorithms/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [从模块化到共享 BEV：驾驶系统改变了哪些接口](../series/workload/03-autonomous-driving-algorithms/modular-to-bev-evolution.md) | 比较模块接口与共享表示；不作单线替代叙事。 |
| [驾驶行为克隆：模仿轨迹为何不等于闭环成功](../series/workload/03-autonomous-driving-algorithms/behavior-cloning-e2e.md) | 驾驶示范监督、误差累积和闭环验证；BC 与规划可共存。 |
| [规划导向端到端：让中间任务服务自车决策](../series/workload/03-autonomous-driving-algorithms/planning-oriented-e2e.md) | 以 UniAD 等系统说明中间任务如何服务自车规划。 |
| [驾驶中的 VLM 与 VLA：语义推理怎样连接车辆动作](../series/workload/03-autonomous-driving-algorithms/vlm-vla-for-ad.md) | 驾驶语义输出到动作接口；解释能力与控制能力分别验证。 |
| [驾驶世界模型：预测未来、比较动作与生成测试场景](../series/workload/03-autonomous-driving-algorithms/world-model-for-ad.md) | 预测、动作比较和测试生成三种用途及其条件。 |
| [数据闭环与仿真：每种测试能证明什么](../series/workload/03-autonomous-driving-algorithms/data-closed-loop-and-simulation.md) | 失败收集、数据切分、仿真及非反应式评测的证据边界。 |

### 机器人策略与视觉语言动作模型

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/04-robotics-and-vla/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [VLA 基础：把视觉与语言条件转成可执行动作](../series/workload/04-robotics-and-vla/vla-fundamentals.md) | 观测和语言如何连接可执行动作；动作块和控制器分工。 |
| [动作表示与生成：分箱、FAST、扩散和 flow matching](../series/workload/04-robotics-and-vla/action-tokenizer.md) | 分箱、FAST、连续动作头；区分表示损失与生成过程。 |
| [RT-1 与 RT-2：机器人数据和视觉语言预训练如何衔接](../series/workload/04-robotics-and-vla/rt-series.md) | 固定 RT-1/RT-2 原论文的预训练、动作输出和执行频率。 |
| [OpenVLA 原模型：视觉语言骨干如何输出七维动作](../series/workload/04-robotics-and-vla/openvla.md) | 固定原论文 v3 的视觉输入、7B 骨干、分箱和七维动作。 |
| [GR00T N1：视觉语言条件与连续动作头](../series/workload/04-robotics-and-vla/groot.md) | 固定 GR00T N1 v2 的双模块、动作块和测量配置。 |
| [机器人世界模型：预测怎样进入策略学习或规划](../series/workload/04-robotics-and-vla/robot-world-model.md) | 比较想象策略学习与部署时预测搜索。 |

### 世界模型与环境预测

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/05-world-model-and-generative/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [世界模型基础：预测对象、条件与用途](../series/workload/05-world-model-and-generative/world-model-fundamentals.md) | 表示、预测机制、条件与用途；世界模型与视频生成的关系。 |
| [Latent 世界模型：压缩状态怎样服务学习与规划](../series/workload/05-world-model-and-generative/latent-world-model.md) | 比较 DreamerV3、V-JEPA 2 与 2-AC 的训练和部署路径。 |
| [视频世界模型：从未来画面到可用环境预测](../series/workload/05-world-model-and-generative/video-world-model.md) | 视频输出的时空一致性、条件控制及其验证范围。 |
| [BEV 世界模型：在统一空间中预测场景演化](../series/workload/05-world-model-and-generative/bev-world-model.md) | BEV 状态的预测和解码；BEVWorld 跨越多个分类轴。 |
| [占用世界模型：预测未来三维空间如何变化](../series/workload/05-world-model-and-generative/occupancy-world-model.md) | 未来占用、动态变化和 OccWorld 输入条件。 |
| [扩散世界模型：时间长度与采样次数怎样计量](../series/workload/05-world-model-and-generative/diffusion-for-world-model.md) | 环境条件、预测时间长度、采样轮次与网络求值计数。 |
| [世界模型与视频生成：关系速查](../series/workload/05-world-model-and-generative/world-model-is-not-video-generation.md) | 兼容旧辨析入口；完整解释合并到世界模型基础。 |

### 算法工作负载分析

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/06-chip-workload-analysis/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [工作负载分析方法：从执行路径推导资源需求](../series/workload/06-chip-workload-analysis/workload-analysis-methodology.md) | 固定执行实例，计工作量、边界流量、容量和依赖，再测量。 |
| [工作负载记录字段：让不同案例可以比较](../series/workload/06-chip-workload-analysis/workload-characterization-axes.md) | 统一分析记录的字段、单位、配置与证据级别。 |
| [CNN 工作负载：复用、分块与中间特征](../series/workload/06-chip-workload-analysis/cnn-workload.md) | 卷积形状、复用、分块与物化中间特征。 |
| [Transformer 工作负载：prefill、decode 与 KV 容量](../series/workload/06-chip-workload-analysis/transformer-workload.md) | 条件化计算 prefill、decode、GQA KV 容量和流量。 |
| [SSM 工作负载：区分并行扫描与流式状态更新](../series/workload/06-chip-workload-analysis/ssm-workload.md)（新增） | 简化递推的扫描与逐步更新；状态容量和完整模型成本。 |
| [MoE 工作负载：从专家分配计数到数据交付](../series/workload/06-chip-workload-analysis/moe-workload.md)（新增） | 专家分配计数、逻辑载荷、设备放置和实际通信边界。 |
| [BEV 工作负载：视角变换、采样与历史特征](../series/workload/06-chip-workload-analysis/bev-workload.md) | 相机编码、视角变换、采样和历史融合的分段资源分析。 |
| [Occupancy 工作负载：三维分辨率、稀疏性与输出解码](../series/workload/06-chip-workload-analysis/occupancy-workload.md) | 空间分辨率的三次方增长、稀疏索引和输出解码成本。 |
| [端到端驾驶工作负载：共享计算与关键路径](../series/workload/06-chip-workload-analysis/e2e-workload.md) | 驾驶共享计算、模块频率和传感器到动作的关键路径。 |
| [VLA 工作负载：编码、动作生成与执行节拍](../series/workload/06-chip-workload-analysis/vla-workload.md) | 编码、离散或连续动作生成、预测块与执行节拍。 |
| [世界模型工作负载：调用图比模型类别更重要](../series/workload/06-chip-workload-analysis/world-model-workload.md) | 候选、时间长度与求值次数的调用图计数，避免重复乘法。 |
| [端侧推理约束：从截止时间推导芯片需求](../series/workload/06-chip-workload-analysis/edge-inference-chip-requirements.md) | 截止时间、尾延迟、容量与功耗预算；p99 不替代 WCET。 |
| [云端推理与仿真：吞吐、并发和通信的取舍](../series/workload/06-chip-workload-analysis/cloud-inference-and-simulation-chip.md) | 云端服务、离线生成和策略训练的吞吐与通信约束。 |
| [世界模型的端云协作：按调用时限划分职责](../series/workload/06-chip-workload-analysis/edge-cloud-collaborative-world-model.md) | 按调用时限、传输量和故障回退划分端云职责。 |
| [从驾驶与机器人负载到架构实验](../series/workload/06-chip-workload-analysis/ad-robotics-chip-architecture-summary.md) | 把算法需求转成可验证的架构假设和实验矩阵。 |
| [工作负载比较索引：先选阶段，再看资源](../series/workload/06-chip-workload-analysis/workload-comparison-table.md) | 按阶段定位对应案例；不对模型家族作固定性能排名。 |
| [从算法到工作负载：阅读入口](../series/workload/06-chip-workload-analysis/workload-lens.md) | 兼容原工作负载入口；分析方法集中到方法主文。 |

### 查阅资料

| 页面 | 内容边界 |
| --- | --- |
| [专题导读](../series/workload/07-reference/README.md) | 本专题职责、阅读顺序及与相邻专题的边界。 |
| [按问题查阅：从术语找到主文](../series/workload/07-reference/multi-dimensional-index.md) | 按问题链接主文；不另建重复的概念解释。 |
| [代表论文与阅读目的](../series/workload/07-reference/representative-papers.md) | 按学习目的列代表一手来源；不是完整文献或性能排名。 |
| [来源、版本与核查边界](../series/workload/07-reference/source-tracking.md) | 记录核查版本、事实修正、教学假设及未复现的实验。 |
| [按目标阅读：原入口](../series/workload/07-reference/reading-roadmap-by-goal.md) | 兼容旧阅读路线；四条路线合并到总导读。 |

## 验证边界与后续工作

本次核查的是机制、公式条件、论文原配置及网站发布行为。没有重新训练模型，没有复现论文任务分数，也没有在目标硬件上测量端到端性能。具体吞吐、尾延迟、能耗、专家通信和闭环质量仍需固定模型版本、输入、实现与设备后测试。

原始案例有意固定 RT、OpenVLA、GR00T N1、DreamerV3、V-JEPA 2/2-AC 等论文版本。本次不是对其后续变体或截至核查日期所有模型的完整综述。新增变体应单独记录版本与差异，不能回填为旧模型的事实。
