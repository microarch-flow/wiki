# 来源、版本与核查边界

上级：[专题导读](README.md)

<span id="source-tracking" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="查证口径" class="workload-legacy-anchor"></span>
<span id="本轮重点查证项" class="workload-legacy-anchor"></span>
<span id="逐项来源记录" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


案例版本核查于 **2026-11-17**，基础机制复核于 **2026-11-18**。表中测量值取自列出的论文版本。正文用“构造例”标出用于手算的参数。

## 关键修正的证据

| 对象与版本 | 本轮确认的口径 | 不据此推导 |
| --- | --- | --- |
| [DETR v3](https://arxiv.org/html/2005.12872v3) | Hungarian 匹配用于训练目标分配 | 推理必须执行匹配 |
| [Swin](https://arxiv.org/abs/2103.14030) | 2×2 合并使 token 数变为 1/4、通道翻倍 | token 数仅减半 |
| [RT-1 v1](https://arxiv.org/html/2212.06817v1) | 使用视觉/语言预训练，移除动作间自回归条件 | 所有知识只来自机器人数据 |
| [RT-2 v1](https://arxiv.org/html/2307.15818v1) | 约 5 Hz 对应 PaLI-X 5B 的论文配置 | PaLM-E 12B 的测量或永久云端限制 |
| [OpenVLA v3](https://arxiv.org/html/2406.09246v3) | 原始实验为第三人称相机；7 维动作分箱 | 原模型已使用腕部多相机 |
| [π0 v1](https://arxiv.org/html/2410.24164v1) | RTX 4090 总推理 73 ms；动作前向部分 27 ms | 73 ms 全是动作专家，50 Hz 等于 50 次完整推理 |
| [GR00T N1 v2](https://arxiv.org/html/2503.14734v2) | 10/120 Hz 系统描述与 16-action/63.9 ms 分别记录 | 120 次完整 chunk 采样或固定复用 12 次 |
| [DreamerV3 v2，式 1 和式 4](https://arxiv.org/html/2301.04104v2) | 真实交互由观测与上一动作更新模型状态，再由 actor 选动作 | 只计 actor 网络，或把训练想象时域乘进每次交互 |
| [V-JEPA 2 v1，表 3](https://arxiv.org/html/2506.09985v1) | 机器人规划属于 2-AC，设备和测量条件见[规划案例](../05-world-model-and-generative/latent-world-model.md) | 所有 latent 模型已满足高频控制 |
| [BEVWorld v3](https://arxiv.org/html/2407.05679v3) | BEV latent、序列 diffusion 与观测 decoder 同时存在 | BEV、latent、视频是互斥类别 |
| [OccWorld](https://arxiv.org/abs/2311.16038) | 2 s 历史预测 3 s 未来；输入监督配置应区分 | 真值 occupancy 输入结果等于 camera 端到端结果 |
| [NAVSIM v1 基准，原论文第二版](https://arxiv.org/abs/2406.15349v2) | 自车按规划更新，背景交通主体沿记录轨迹运动 | 完整反应式交通世界或真实道路安全证明 |

## 数字与结论怎样使用

正文的手算形状、容量、FLOP 与频率例标为构造例；它们验证计数关系，不是设备测量。Roofline 与工作量估算建立条件性上界或下界，不能替代内核和系统测试。

论文或开源代码证明有对应研究实现，不自动证明生产部署成熟度。本轮去掉了无一致证据的“已落地”“唯一端侧路线”和跨年份必然趋势判断。

## 未作为已核实事实保留的内容

OccWorld 的“2 Hz、4 帧历史”未在本轮统一确认，正文只使用已核实时间范围。不同模型的长期预测误差、量化质量、目标硬件延迟和 Archax 支持能力，均需对应配置的后续实验。

本轮没有复现实验训练或真实机器人/驾驶测试，也不根据网站构建成功证明算法效果。未展开的后续模型版本不作为当前案例的隐含配置。

<span id="后续维护规则" class="workload-legacy-anchor"></span>

## 历史与维护

原 2026-05-29 与 2026-06-07 来源表保存在[历史快照](https://github.com/microarch-flow/wiki/blob/main/docs/archive/workload/source-tracking-20260607.md)。它保留当时记录，不延续其成熟度和趋势结论。

新增具体结果时记录论文版本、表格或章节、输入条件、设备、精度、范围和日期。先修改拥有该机制的主文，再更新[代表论文索引](representative-papers.md)；无需在多个索引复制一份模型介绍。
