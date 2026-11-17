# 驾驶中的 VLM 与 VLA：语义推理怎样连接车辆动作

上级：[专题导读](README.md)

<span id="vlm-and-vla-for-autonomous-driving" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么要把大模型塞进车里直觉与类比" class="workload-legacy-anchor"></span>
<span id="部署的现实形态慢-快双系统" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


视觉语言模型可以描述交通场景、回答问题或解释决策；视觉语言动作模型进一步输出动作相关表示。是否改善驾驶，应以输入依赖、动作接口与闭环结果判断，不能由自然语言解释的流畅程度判断。

## 三种接入位置

离线数据工具可帮助检索场景、生成标签或分析失败，输出不直接进入在线控制。在线辅助模块可提供语义约束或候选解释，再由规划器处理。直接策略则把多模态输入映射为轨迹或控制量。

三者的延迟、错误传播和验证要求不同。离线标注质量提高，不等于同一个大模型可以直接进入实时链路。

## 语言与几何之间缺少什么

“前方有人，应减速”没有给出行人坐标、速度、可用制动距离或车辆约束。连接车辆动作至少需要坐标化状态、时间对齐和动作参数化。

构造例：一条文字判断正确，却基于 300 ms 前的图像。若相对速度为 15 m/s，期间相对位置已变化 4.5 m。语义正确与及时可用是不同要求。

DriveLM 用图结构组织感知、预测和规划相关问答，是理解语言接口的代表。它的问答任务与真实闭环控制能力应分别评价。

## 可解释文本不是因果证据

模型可能生成合理解释，却使用了错误视觉线索或仅复述先验。应测试遮挡、反事实输入、导航变化和置信度校准，并检查文字与实际动作是否一致。

模型是否使用自回归文本、离散轨迹 token 或连续动作头，将改变串行依赖与采样成本。VLM 的共同结构见[视觉语言模型](../language-and-multimodal/vision-language-models.md)，动作生成机制见[动作表示](../04-robotics-and-vla/action-tokenizer.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 本文保留的边界

VLM/VLA 是有明确接口的技术选项，不是对所有驾驶模块的统一替代。评价时应报告实际在线路径、输入时间戳、任务指标和端到端延迟；没有这些条件时，不给出“必然改善长尾”或“必然实时”的结论。

## 来源与延伸

- [DriveLM](https://arxiv.org/abs/2312.14150)
- [RT-2：视觉语言动作迁移案例](https://arxiv.org/abs/2307.15818)
