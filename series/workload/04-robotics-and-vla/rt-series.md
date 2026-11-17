# RT-1 与 RT-2：机器人数据和视觉语言预训练如何衔接

上级：[专题导读](README.md)

<span id="rt-series" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="rt-1小脑子能实时的起点" class="workload-legacy-anchor"></span>
<span id="rt-2动作即-text-token泛化与延迟的换价" class="workload-legacy-anchor"></span>
<span id="rt-x-与-open-x-embodiment跨本体的数据统一" class="workload-legacy-anchor"></span>
<span id="rt-h动作层次不必一步到位" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


RT-1 与 RT-2 展示了两种机器人动作学习路径。本文讨论两篇原论文的配置，帮助比较表示、训练和执行；不把论文实验中的设备和频率当成整个路线的永久限制。

## RT-1：压缩视觉输入，学习机器人动作

RT-1 读取 6 帧图像历史和语言指令。图像路径使用 ImageNet 预训练的 EfficientNet-B3，并由语言表示调制；TokenLearner 压缩视觉特征，再交给 Transformer 预测离散动作。

原模型约 35M 参数。动作覆盖手臂/夹爪、底盘和模式选择。它使用视觉与语言预训练，因此“全部知识来自机器人数据”不成立。

RT-1 原论文的消融指出，动作维度之间加入自回归条件没有改善结果，却增加推理时间；采用的模型移除了这类动作间自回归条件。因此不能仅凭离散动作 token 就把它归为逐 token 串行 decode。

## RT-2：把动作加入视觉语言任务

RT-2 在视觉语言模型上共同微调网页视觉语言任务与机器人动作数据。动作连续维度离散为 256 bins，并用文本词表中的符号表示。训练目标因此可以沿用 token 预测形式。

这种迁移试图把网页数据中的语义与机器人行动关联，但实际可执行的动作仍需机器人轨迹训练。看到一种新物体，不代表已经学会与它稳定接触和操作。

## 频率必须与配置一起引用

| 论文配置 | 原论文报告口径 | 不能推导的结论 |
| --- | --- | --- |
| RT-1 | 3 Hz 的机器人控制要求包含相机与通信链路 | 不能直接取倒数当网络前向时延 |
| RT-2 PaLI-X 55B | 多 TPU 云服务实验中约 1—3 Hz | 不能断言所有 RT-2 必须在云端 |
| RT-2 PaLI-X 5B | 同文约 5 Hz | 不能误记为 PaLM-E 12B 的测量 |

这些是 2022—2023 年原论文的系统实验。设备、精度、并发和优化会改变实际结果，本文不据此预测产业最终会收敛到某个参数规模。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 两篇论文对工作负载的启示

RT-1 的视觉压缩改变后续 token 数；RT-2 的语言模型与动作生成增加不同的权重和依赖成本。比较应画出视觉、语言、动作头、解码与通信的实际路径，并记录每个阶段的调用次数。

离散动作模型的后续案例见 [OpenVLA](openvla.md)，更一般的动作接口见[动作表示与生成](action-tokenizer.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [RT-1 原论文 v1，尤其附录 D.1](https://arxiv.org/html/2212.06817v1)
- [RT-2 原论文 v1，尤其第 3.4 节](https://arxiv.org/html/2307.15818v1)
