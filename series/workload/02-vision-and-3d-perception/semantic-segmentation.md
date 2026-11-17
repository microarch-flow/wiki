# 语义分割：为每个位置分配类别

上级：[专题导读](README.md)

<span id="semantic-segmentation" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与那个写回带宽" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


语义分割回答“这里是什么类别”，输出通常是图像网格上的类别分布。它不区分同类目标的个体身份。三辆车都标为“车”是正确的语义输出，却不足以回答“第三辆车在哪里”。

## 输入、logits 与标签

输入图像为 $[B,3,H,W]$，任务头产生 $[B,K,H_o,W_o]$ 的 logits。经过上采样可对齐到需要的输出分辨率；softmax 给出每个位置的类别分布，argmax 得到离散标签。训练常对有效标注位置计算交叉熵：

$$
\mathcal L=-\frac1{|\Omega|}\sum_{p\in\Omega}\log P(y_p\mid x)
$$

$\Omega$ 不包含忽略区域。类别不平衡时可以调整权重或目标，但损失更低不一定使小目标或边界更好。

## 为什么需要上下文和细节

只看单个像素往往无法判断其语义；连续降采样又可能丢失细边界。FCN 将分类网络改成密集预测网络；DeepLab 系列使用空洞卷积和多尺度上下文，DeepLabv3+ 进一步用 decoder 恢复细节。

构造例：一条仅 3 像素宽的车道线，在步长 16 的特征上可能不足一个网格。简单双线性上采样只能插值已有输出，无法保证恢复丢失的边缘。高分辨率特征、跳连和边界监督各有计算与标注成本。

## 评价和误用

单类别 IoU 为 $TP/(TP+FP+FN)$；mIoU 对选定类别取平均。若把“忽略区域”误当背景，或改变类别集合，数字就不能直接比较。总体像素准确率可能被大面积道路或背景主导。

分割图表示类别估计，不是可通行性或碰撞风险的完整描述。图像中的道路仍需要深度、坡度、交通规则及动态信息才能支持行驶。三维空间占用问题见 [Occupancy 感知](occupancy-prediction.md)。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 输出规模也是成本

构造输出为 $1024\times2048$、19 类、FP16 时，完整 logits 约为 76 MiB。若最终只保留 uint8 类别图，则是 2 MiB，但在 logits 物化的实现中，argmax 前的容量不能省略。

融合和低分辨率预测可改变实际流量；它们对边界质量的影响需独立测量。与[实例分割](instance-segmentation.md)的区别在输出语义，不是“是否采用 Transformer”。

<span id="演进与系统意义" class="workload-legacy-anchor"></span>
<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [FCN](https://arxiv.org/abs/1411.4038)
- [DeepLabv3+](https://arxiv.org/abs/1802.02611)
