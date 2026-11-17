# 多尺度特征融合：FPN 为什么连接不同分辨率

上级：[专题导读](README.md)

<span id="neck-feature-fusion" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与代价分布" class="workload-legacy-anchor"></span>
<span id="在自动驾驶与机器人中的位置" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


骨干网络的各阶段同时存在空间分辨率和语义抽象程度的差异。neck 的职责是把这些特征变成任务头需要的输入。它不是每个视觉模型都必须具有的独立模块。

## FPN 的基本路径

设骨干产生步长为 8、16、32 的特征 $C_3,C_4,C_5$。FPN 先用侧向投影统一通道，再由低分辨率向高分辨率上采样相加。简化形式为：

$$
P_5=L_5(C_5),\qquad
P_4=L_4(C_4)+\operatorname{Up}(P_5),\qquad
P_3=L_3(C_3)+\operatorname{Up}(P_4)
$$

原始 FPN 还在融合结果上使用卷积形成输出特征。相加要求空间尺寸和通道一致；奇数尺寸、插值对齐与填充方式必须由实现明确。上采样不会恢复已丢失的真实细节，它只是把已有表示映射到更密的位置。

构造例：三个侧向特征为 $80\times80$、$40\times40$、$20\times20$，统一为 256 通道。总元素数为 2,150,400；FP16 占约 4.10 MiB。若三者同时存活，这是容量的一部分，尚不包括输入、卷积工作区和输出副本。

## 相加、拼接与双向融合

相加保持通道数，但要求特征具有可组合的表示；拼接保留各分支通道，通常再用投影融合，因此增加中间宽度和后续计算。PANet 添加自底向上的路径，以补充低层信息传播；BiFPN 使用可学习权重等设计组合多尺度输入。

更多连接不自动意味着更高效率。一个轻量骨干后面若接上宽通道、高分辨率、多轮融合的 neck，neck 可能成为主要成本。比较时必须同时固定骨干、输入尺寸和任务头。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 与任务头和三维融合的边界

FPN 输出仍是图像坐标中的多尺度特征。它不自动解决相机到 BEV 的几何投影，也不等于多传感器对齐。检测、分割或深度预测头可以消费这些特征，但各自的监督与输出不同。

算术量以卷积和投影为主；上采样、拼接、相加则容易增加流量与存活张量。是否需要片外物化取决于布局和融合，详见 [CNN 工作负载](../06-chip-workload-analysis/cnn-workload.md) 与 [BEV 感知](../02-vision-and-3d-perception/bev-perception.md)。

## 来源与延伸

- [FPN](https://arxiv.org/abs/1612.03144)
- [PANet](https://arxiv.org/abs/1803.01534)
- [EfficientDet 与 BiFPN](https://arxiv.org/abs/1911.09070)
