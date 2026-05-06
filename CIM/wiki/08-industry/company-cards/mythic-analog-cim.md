# Mythic Analog Compute-in-Memory

## 基本信息

- 公司：Mythic
- 对象：`Analog Compute-in-Memory` / `Analog Matrix Processor`
- 路线归类：`analog CIM`
- 公司角色：`startup`

## 时间点

- `2020-11-19`：Mythic 发布首款 Analog Matrix Processor 新闻稿
- `2024-06-27`：Mythic 更换 CEO，继续扩展 AI inference 市场
- `2026-02-06`：Honda 与 Mythic 宣布联合开发面向下一代车辆的模拟 AI 芯片

## 官方口径里最值得记的内容

Mythic 官网对自身路线的表述很清楚：

- 它把 AI 参数直接存进处理器 / memory array
- 用模拟方式在阵列内完成核心矩阵运算
- 目标是消除传统数字架构中的 memory bottleneck

其产品页对 `M1076 AMP` 的描述则强调：

- 单芯片最高可达 `25 TOPS`
- 使用 `76` 个 AMP tiles
- 最多可存 `80M` 权重参数
- 运行复杂模型时典型功耗约 `3~4W`

## 为什么它值得单独建卡

Mythic 很适合作为“startup 主导的 analog CIM 路线”样板，因为它不是停留在论文概念，而是：

- 有明确产品命名
- 有软件工作流叙述
- 有面向 edge 与更大市场的商业故事

## 怎么看这条路线

### 它的核心价值

- 代表了最典型的 analog compute-in-memory 商业化尝试
- 强调把权重留在阵列内，减少外部 DRAM 依赖
- 目标场景从 edge 推理延伸到 automotive、robotics、defense

### 它的核心边界

- 官网大量表述是公司口径，评估时要区分 marketing claim 与可验证指标
- analog CIM 的老问题依然在：精度、校准、可重复性、规模化制造
- 当它向 data center 和 automotive 走时，验证门槛会大幅抬升

## 在产业图谱中的位置

更适合放在：

- `analog CIM startup`
- `edge inference -> automotive / enterprise expansion`
- `startup 试图把阵列原生计算做成产品`

## 我的判断

Mythic 是看 analog CIM 商业化时绕不开的对象，因为它把这条路线最吸引人的叙事和最难的工程现实放在了同一个公司身上。

## 官方来源

- Mythic 技术页：<https://mythic.ai/technology/compute-in-memory/>
- Mythic 技术页：<https://mythic.ai/technology/analog-computing/>
- Mythic 产品页：<https://mythic.ai/product/analog-matrix-processor/>
- Mythic 新闻稿，`2020-11-19`：<https://mythic.ai/whats-new/mythic-launches-industry-first-ai-analog-matrix-processor/>
- Mythic 与 Honda 新闻稿，`2026-02-06`：<https://mythic.ai/whats-new/honda-and-mythic-announce-joint-development-of-100x-energy-efficient-analog-ai-chip-for-next-generation-vehicles/>
