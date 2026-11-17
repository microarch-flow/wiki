# 动作表示与生成：分箱、FAST、扩散和 flow matching

上级：[专题导读](README.md)

<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="三种表示的计算图各卡在哪" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


动作表示先规定“输出数字是什么意思”，生成模型再规定“如何产生这些数字”。分箱、压缩 token 和连续动作头的比较应固定动作空间、预测长度和任务质量。

## 逐维分箱

给连续动作的每个维度选择区间，再切成离散 bins。模型预测 bin 编号，解码时映射回代表值。区间宽度为 $R$、均匀分为 $K$ 个 bin 时，bin 宽度为 $R/K$；超出范围的值如何裁剪或编码必须另行规定。

RT-2 使用 256 个动作 bins；其 PaLI-X 词表能表示更多单 token 整数，并不表示动作采用 1000 个 bins。OpenVLA 则按训练数据的第 1—99 分位区间设定分箱范围。不同数据归一化不能混用。

若每步动作有 $D$ 维，预测 $H$ 步，逐维离散表示通常需要约 $HD$ 个动作符号，另加控制符。只有采用自回归条件时，这些符号才构成对应的串行生成依赖。

## FAST 压缩了什么

FAST 对动作块归一化，沿时间维做离散余弦变换（DCT），缩放并取整系数，再按规则展平，最后用 BPE 编码常见整数片段。系数量化有损；BPE 对量化后的符号序列可逆。

平滑动作的能量可能集中在少量低频系数，从而得到更短序列。但压缩率依动作频谱、量化和词表而变，不能统一宣称减少一个数量级。需要同时报告 token 长度与重建误差。

<span id="action-tokenizer" class="workload-legacy-anchor"></span>

## 连续动作块也可以有 token

Diffusion Policy 学习条件动作分布，通过多次去噪生成动作块。π0 使用 flow matching，以连续动作 token 表示整个未来块，再逐步更新它们。二者无需逐维离散动作词表，但仍可在 Transformer 中使用 token 序列。

一次网络求值若覆盖整个 $H\times D$ 动作块，则总成本按实际 NFE 计，不再把调用次数重复乘 $H$。训练时抽取噪声时间与采样时多次求值，也应分开。

## 预测长度、执行长度与频率

π0 原论文 v1 的配置说明了三个量的区别：预测长度为 50；50 Hz 的机器人执行其中 25 个动作后再推理，即约 0.5 s 一个执行块。它不等于每秒调用 50 次完整生成器。

同文在 RTX 4090 上报告总推理 73 ms，其中视觉 14 ms、观测前向 32 ms、10 次动作前向合计 27 ms。这个数字是特定实现的完整推理时间，不能全归给动作专家，也不能迁移到另一设备当规格。

## 选择时比较哪些代价

| 方式 | 主要收益 | 需要验证 |
| --- | --- | --- |
| 逐维分箱 | 接入离散分类或语言词表方便 | 量化误差、序列长度、串行依赖 |
| FAST | 利用时间相关性压缩符号 | 重建误差、任务相关压缩率 |
| 连续回归 | 输出路径较直接 | 多峰动作分布可能被均值化 |
| 扩散或 flow | 表达多种可行动作，联合生成块 | NFE、采样随机性、反馈延迟 |

输出平滑不等于动作安全，长块也不要求执行完全部预测。闭环接口见 [VLA 基础](vla-fundamentals.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [FAST 原论文 v1](https://arxiv.org/html/2501.09747v1)
- [π0 原论文 v1，表 I 与附录 B](https://arxiv.org/html/2410.24164v1)
- [Diffusion Policy 项目与论文](https://diffusion-policy.cs.columbia.edu/)
