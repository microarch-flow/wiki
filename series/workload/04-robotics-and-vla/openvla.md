# OpenVLA 原模型：视觉语言骨干如何输出七维动作

上级：[专题导读](README.md)

<span id="openvla" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="真实结构与数字锚点" class="workload-legacy-anchor"></span>
<span id="它暴露的三处部署压力" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


本文以 OpenVLA 原论文 v3 为范围，讨论其 7B 模型的输入、动作编码与部署路径。后续微调方法和其他 OpenVLA 变体需要独立标注，不能混入原模型事实。

## 从图像和指令到动作

原模型将 DINOv2 与 SigLIP 的视觉特征拼接，经 MLP projector 接入 Llama 2 7B，再预测动作 token。论文使用约 97 万条真实机器人 demonstrations 训练。

原始实验的视觉输入使用第三人称相机。不能据此写成已经同时接入腕部相机、多相机或完整状态历史；这些扩展需要对应实现证据。

## 七维动作的含义

输出包含三维末端平移、三维旋转和夹爪控制。它是动作参数化的七个维度，不等同于“七个关节角”或“七自由度机械臂”。

每一维按训练动作的第 1—99 分位范围均匀划成 256 bins，并使用词表中相应 token 编码。模型在动作 token 上计算交叉熵。部署时须使用正确数据集的归一化统计量，将符号还原成动作量。

构造例：某平移维度的有效区间宽 0.256 m，则 bin 宽为 1 mm。这个例子展示分辨率计算，并非原论文所有动作维度的统一精度。分位范围外的动作和旋转表示仍需单独处理。

## 推理路径和权重读取

图像编码与提示处理完成后，动作 token 按模型的自回归路径生成。已有位置的 K/V 可以缓存，但每个新 token 仍需要相应层的计算。

如果 batch 为 1、权重不能驻留片上、且没有跨请求复用，读取大模型权重可能成为显著成本。这是条件性分析；不能写成“每个 token 必然把全部权重在 HBM 来回读写”。推理通常读取权重，未必写回；缓存、量化与执行实现也会改变流量。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 能力与测量边界

真实机器人任务成功率需要与机器人、环境、微调数据和评测协议一起阅读。开放权重便于复现，不等于所有本体可以不经适配直接使用。

本页保留原模型结构。动作压缩与连续头见[动作表示与生成](action-tokenizer.md)；完整资源计数见 [VLA 工作负载](../06-chip-workload-analysis/vla-workload.md)。

## 来源与延伸

- [OpenVLA 原论文 v3](https://arxiv.org/html/2406.09246v3)
- [OpenVLA 官方项目](https://openvla.github.io/)
