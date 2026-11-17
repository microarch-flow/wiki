# GR00T N1：视觉语言条件与连续动作头

上级：[专题导读](README.md)

<span id="gr00t" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="真实结构与数字锚点" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


本文只讨论 GR00T N1 原论文 v2，不把后续 N1.x 模型参数与结果回填到这个版本。它用视觉语言模型提供条件，再由连续动作生成头输出动作块。

## 两部分如何连接

论文中的 System 2 使用 Eagle-2 VLM 处理图像和语言，System 1 使用 diffusion transformer（DiT）结构的动作头，通过 flow matching 学习连续动作生成。动作头编码带噪动作与机器人状态，并对图文特征做交叉注意力。

这里 DiT 描述网络结构，flow matching 描述训练和生成路径；两者可以同时成立。System 1/2 是论文的结构命名，不应据此推断人类认知机制或通用智能能力。

## 参数与频率的原始口径

| 项目 | 原论文 v2 的配置或测量 |
| --- | --- |
| 总参数 | 约 2.2B；公开模型名使用 2B |
| 其中 VLM | 约 1.34B |
| 第 2.1 节系统描述 | L40 上 System 2 为 10 Hz，System 1 输出 120 Hz motor actions |
| 第 3.1 节 chunk 测量 | BF16、L40、16 个动作的块，63.9 ms |

两处频率和时延描述使用不同口径，应分别保留。不能把 120 Hz 当成每秒执行 120 次完整动作块采样，也不能由 120/10 推导 VLM 特征固定复用 12 次。

## 动作块执行需要另一层接口

动作头输出的块要经过本体对应的解码和执行。预测长度、实际执行长度、动作采样周期和重新推理周期分别影响反馈延迟与算力需求。

构造例：若预测 16 个动作，却每次只执行 4 个，再读取新观测，则重推理次数由执行策略决定，而不是仅由预测块长度决定。此例仅说明计数方式，不是 GR00T N1 的额外公开配置。

## 如何评价这个案例

视觉语言条件与动作头分开，允许分别研究图文编码和动作采样成本，但不保证两者完全异步或没有同步开销。跨本体数据训练也需要明确状态、动作映射和评测任务。

本文用于理解结构接口。与离散 token 路径的比较见 [OpenVLA](openvla.md)；动作频率及 NFE 的一般口径见 [VLA 工作负载](../06-chip-workload-analysis/vla-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [GR00T N1 原论文 v2，第 2.1 与 3.1 节](https://arxiv.org/html/2503.14734v2)
