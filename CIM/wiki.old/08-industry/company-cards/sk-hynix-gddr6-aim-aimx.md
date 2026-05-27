# SK hynix GDDR6-AiM / AiMX

## 基本信息

- 公司：SK hynix
- 对象：`GDDR6-AiM` 与 `AiMX`
- 路线归类：`GDDR / PIM / Accelerator-in-Memory`
- 公司角色：`memory vendor`

## 时间点

- `2022-02-16`：SK hynix 新闻稿表示已开发出采用 PIM 的 `GDDR6-AiM` 样品
- `2023-09-18`：SK hynix 展示首个基于 `GDDR6-AiM` 的 `AiMX` generative AI accelerator card 原型
- `2025-10-01`：SK hynix 继续在 AI Infra Summit 展示更新后的 AiM 方案

## 官方口径里最值得记的内容

SK hynix 对 `AiM` 的定义很明确：它是其 `PIM` 产品名，包含 `GDDR6-AiM`。

这说明这条路线的重点不是把存储阵列直接做成通用计算核心，而是：

- 在高带宽图形内存体系中加入计算能力
- 面向 AI、HPC、big data 等数据密集任务
- 进一步把产品形态扩成 card 级 `AiMX`

## 为什么它值得单独建卡

Samsung HBM-PIM 更像内存本体的路线展示，而 SK hynix 的 `GDDR6-AiM -> AiMX` 更清楚地展示了一条从 memory component 往 accelerator card 过渡的商业路径。

它回答的是另一个问题：

> memory vendor 能不能不只卖 memory，而是进一步卖面向 AI inference 的 memory-centric solution？

## 怎么看这条路线

### 它的核心价值

- 利用 GDDR6 的带宽属性承接 AI memory-bound 工作负载
- 进一步通过 AiMX 把产品形态从 chip 扩到可展示、可集成的 accelerator card
- 在官方表述中，已经直接对齐 `LLM`、`attention`、`KV-cache` 等场景

### 它的核心边界

- 这是典型 `PIM / AiM` 路线，不是纯阵列级 CIM
- 许多性能说法依赖特定 demo、ASIC control hub 或系统配置
- 评价时必须区分 `chip`、`card`、`demo system` 三个层级

## 在产业图谱中的位置

更适合放在：

- `memory vendor 主导路线`
- `GDDR / PIM / AiM`
- `LLM inference / attention / KV-cache / AI infra`

## 我的判断

如果 Samsung HBM-PIM 更像“方向信号”，那么 SK hynix 的 `GDDR6-AiM + AiMX` 更像“产品化姿态”。它让这条路线从内存器件概念，往可部署的 AI 加速系统更近了一步。

## 官方来源

- SK hynix 新闻稿，`2022-02-16`：<https://news.skhynix.com/sk-hynix-develops-pim-next-generation-ai-accelerator/>
- SK hynix 新闻稿，`2023-09-18`：<https://news.skhynix.com/sk-hynix-debuts-first-gddr6-aim-accelerator-card-aimx-for-generative-ai/>
- SK hynix 新闻稿，`2025-10-01`：<https://news.skhynix.com/ai-infra-summit-2025/>
