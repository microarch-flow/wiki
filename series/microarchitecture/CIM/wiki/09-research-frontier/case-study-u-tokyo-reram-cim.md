# 案例：东大 ReRAM CIM

上级：[09 研究前沿](README.md)
相关：[ReRAM 作为计算元件](../02-memory-technologies/reram-as-compute-element.md), [非理想性与误差源](../04-circuit-and-macro/non-idealities-and-error-sources.md), [Edge AI](../07-workloads/edge-ai-and-cim.md)

## 这页在回答什么问题

这页回答：ReRAM CIM 研究为什么必须同时讨论多值存储、长期保持和推理精度，而不是只讨论 crossbar MAC。

基本信息：

| 字段 | 内容 |
| --- | --- |
| 论文 | Adaptive Oxygen Vacancy Diffusion Compensation in MLC Intermediate States for over 10-year Data-retention of TaOx ReRAM Analog CiM Array |
| 会议/年份 | IEEE ESSERC 2025 |
| 机构/作者 | University of Tokyo；Yusuke Hirata、Kenshin Yamauchi、Naoko Misawa、Chihiro Matsui、Ken Takeuchi |
| 技术路线 | TaOx ReRAM analog CiM array，MLC intermediate states，retention compensation |
| 层级 | device/array/research result，不是产品 |
| 来源 | [University of Tokyo press release, 2025-09-11](https://www.t.u-tokyo.ac.jp/en/press/pr2025-09-11-002) |

ReRAM CIM 的核心吸引力是非易失、高密度和 conductance-based MAC。权重可以以电导状态留在 array 中，读电流的加和天然适合 analog MVM；但多值状态越多，电导间隔越小，retention、noise、temperature 和 oxygen vacancy diffusion 带来的漂移越容易破坏 MAC 精度。

东大这个案例有研究价值，是因为它把“大容量化”和“长期保持”放在一起处理。官方发布说明该工作用 MLC 技术提高容量，同时提出补偿 ReRAM reliability degradation 导致的 MAC 变化，目标是在 10 年以上保持期内维持高 AI 推理精度。这个问题比单次阵列读写更接近产品化前必须面对的可靠性闭环。

[原论文](https://doi.org/10.1109/ESSERC66193.2025.11214081)使用 40nm、4 Mbit TaOx 芯片，研究 S0–S3 四个电阻态（2 bit/cell）。在 150°C 与 190°C 测量 cell 电流分布；190°C 的 12.9 小时按 Arrhenius 模型、氧空位扩散激活能 1.2 eV 换算为 85°C 下 10 年等效时间。S1/S2 中间态电流漂移较 S3 明显。此为加速测量与模型换算，不是系统在 85°C 实际运行十年的证明。

作者用 S3 replica cell 的平均实测电流预测补偿因子 α，缩放 MAC 值；模型侧还使用 ELU 和 retention-aware training。文中根据实测保持数据估计 ResNet32 推理精度，而不是完整系统连续运行十年的实测。准确率、外设能耗和其他 workload 的外推须保留各自实验条件；[东大发布及原图](https://www.t.u-tokyo.ac.jp/hubfs/press-release/2025/0911/002/text.pdf)说明等效保持背景。

对 taxonomy，它是典型 CIM：存储介质和计算物理同混，ReRAM cell 的电导状态直接参与 MAC。它和 PIM/NMC 的差异很清楚：PIM/NMC 主要研究数据搬移和 host/memory 协同，ReRAM CIM 研究首先要解决器件状态是否能长期、可重复地代表权重。

## 一句话理解

东大 ReRAM case 的价值是把 ReRAM CIM 从“能做 analog MAC”推进到“多值权重能否长期可靠地支撑推理”。

## 研究启示

新器件 CIM 的关键 open problem 是误差随时间、温度、写入次数和阵列位置传播到模型精度的完整链路。没有 retention/endurance/compensation 的证据，ReRAM CIM 的高密度和高能效只能停留在短期实验结果。
