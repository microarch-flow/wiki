# VLA 工作负载：编码、动作生成与执行节拍

上级：[专题导读](README.md)

<span id="vla-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="visual-token-爆炸vla-比纯-llm-更难的第一个原因" class="workload-legacy-anchor"></span>
<span id="action-输出的两条路线自回归-vs-连续对-workload-影响相反" class="workload-legacy-anchor"></span>
<span id="action-chunk-与控制频率摊薄昂贵的大模型前向" class="workload-legacy-anchor"></span>
<span id="端侧-vs-训练侧两个完全不同的-workload" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


VLA 的资源需求由观测编码和动作生成共同决定。动作频率通常高于策略重推理频率；必须先区分预测块、执行块和控制器，再估算每秒工作量。

## 离散动作与连续动作路径

离散自回归模型包括视觉编码、提示 prefill 和动作 token decode。串行长度取决于动作编码；RT-1 这类非动作间自回归预测不能套用同一公式。

连续动作模型可先缓存图文条件，再用多次动作头求值更新整个块。NFE、动作头大小、条件是否复用及求解器都会影响成本。Flow matching 不等于只有一次前向。

## 一个执行节拍例子

构造策略每次预测 50 步、动作周期 20 ms，但只执行前 25 步，则约每 0.5 s 重新推理。若每次有 10 次动作网络求值，稳定执行下约每秒 20 次动作网络求值，而不是 $50\times10=500$ 次。

这个预算还需考虑异步生成、启动与阻塞。观测可能在块内变旧；重推理频率更低可节约计算，却增加反馈延迟。π0 的原论文案例见[动作表示与生成](../04-robotics-and-vla/action-tokenizer.md)。

## 权重、缓存和状态

离散 LLM 路径要分别计权重流量与 KV cache。连续头路径要计图文条件、动作 latent、各 NFE 的临时激活和条件复用。每条机器人请求的状态不能错误地在并发请求间共享。

动作输出张量可能很小，却位于强依赖的链路末端。总体 FLOPs 不大也可能受小矩阵利用率、采样串行性或同步限制。

## 测量协议

报告视觉分辨率与相机数、语言长度、本体状态、动作维数、预测/执行长度、NFE、精度、设备，以及是否包含反归一化、通信和控制调用。

同时检查闭环成功率和动作误差。量化应明确作用于权重、激活、KV 还是动作输出；对语言质量有效的配置不能自动保证控制质量。

RT、OpenVLA 和 GR00T 的版本数字留在各自[案例文章](../04-robotics-and-vla/README.md)，本页只提供可复用计数方法。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [π0 原论文 v1](https://arxiv.org/html/2410.24164v1)
- [RT-1 原论文 v1](https://arxiv.org/html/2212.06817v1)
- [GR00T N1 原论文 v2](https://arxiv.org/html/2503.14734v2)
