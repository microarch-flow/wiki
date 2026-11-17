# CNN 骨干：局部卷积如何形成多尺度特征

上级：[专题导读](README.md)

<span id="cnn-backbone" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与真实的-flops-账" class="workload-legacy-anchor"></span>
<span id="cnn-在自动驾驶与机器人中的位置" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


CNN 骨干把图像变成可供检测、分割等任务使用的特征。卷积规定局部连接和权重共享；任务头才规定最终输出。本文讨论特征提取，不把整个视觉系统的成本都归到卷积。

## 一个卷积层在计算什么

输入为 $[B,C_{\rm in},H_i,W_i]$，卷积核为 $[C_{\rm out},C_{\rm in}/g,K_h,K_w]$。每个输出位置取一个局部窗口，对通道和窗口坐标做乘加。步长决定窗口移动的距离，填充决定边界处理，dilation 决定采样间隔。

以高度为例：

$$
H_o=\left\lfloor\frac{H_i+2P_h-D_h(K_h-1)-1}{S_h}+1\right\rfloor
$$

其中 $D_h=1$ 表示普通连续采样。按 1 MAC = 2 FLOP 计数，计算量为 $2BH_oW_oC_{\rm out}(C_{\rm in}/g)K_hK_w$，不能把输出尺寸直接替换成输入尺寸。

构造例：输入 $[1,3,32,32]$，16 个 $3\times3$ 核，步长 1、填充 1、无分组。输出为 $[1,16,32,32]$，包含 442,368 MAC，即 884,736 FLOP。偏置与激活另计。这个例子只说明运算量，不预测实际延迟。

## 为什么要逐级降采样

浅层保留较密的空间细节；后续层通过多次局部交互扩大感受野。降采样减少空间位置，通常同时增加通道数。残差连接让一组层学习输入上的增量，有助于训练深网络，但不保证每个深网络都更准确。

构造例：输入边长 256，若四个阶段的步长分别为 4、8、16、32，对应特征边长为 64、32、16、8。小目标可能只占低分辨率图的一个位置，所以检测和分割常保留多个阶段，再交给 [FPN 等融合结构](neck-feature-fusion.md)。

卷积的局部连接是一种归纳偏置，不是“只能理解局部”。多层网络可以建立大范围依赖；相反，全局 attention 也不自动得到更好的任务结果。平移等变性还受填充、步长和边界影响。

## 普通卷积、深度卷积与 1×1 卷积

| 结构 | 连接方式 | 主要作用与限制 |
| --- | --- | --- |
| 普通卷积 | 每个输出通道组合组内多个输入通道 | 同时混合空间与通道，计算量较大 |
| 深度卷积 | 每个输入通道独立做空间滤波 | 减少乘加，但单算子的通道混合有限 |
| 1×1 卷积 | 在同一空间位置混合通道 | 改变通道维度，本身不扩大空间感受野 |

MobileNet 用深度卷积加逐点卷积替代普通卷积。以通道乘数 1、核边长 $K$ 为例，MAC 比值约为 $1/C_{\rm out}+1/K^2$。这是算术量比较；实际速度仍取决于内核、布局和数据搬运。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 工作负载边界

卷积有规则的逻辑索引和空间复用，但并不由此保证 DRAM 行命中或阵列利用率。实现可以采用直接卷积、隐式 GEMM 或其他算法；是否物化展开矩阵也会改变流量。深度卷积减少计算后，可能更容易受带宽或启动开销限制。

完整成本分析见 [CNN 工作负载](../06-chip-workload-analysis/cnn-workload.md)。训练时的反向传播、优化器和激活保存不能混入仅前向的推理数字。

## 来源与延伸

- [ResNet：残差学习](https://arxiv.org/abs/1512.03385)
- [MobileNet：深度可分离卷积](https://arxiv.org/abs/1704.04861)
