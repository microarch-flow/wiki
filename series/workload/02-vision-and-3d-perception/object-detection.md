# 目标检测：从图像到目标集合

上级：[专题导读](README.md)

<span id="object-detection" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与真实量级" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


目标检测输出目标类别、位置和置信度。二维框通常表示图像平面上的范围；三维框还涉及坐标系、尺寸与朝向。检测不是分割，也不自动提供跨帧身份或未来运动。

## 两类输出组织

密集检测器在多个特征位置或候选框上产生预测，再筛选结果。两阶段方法先产生候选区域，再分类和回归；单阶段方法直接在特征上输出结果。anchor-based 与 anchor-free 描述候选参数化方式，不等于是否需要后处理。

DETR 把检测写成集合预测：固定数量的 object query 并行输出类别与框。训练时，通过二分匹配把预测和标注一一对应；未匹配预测学习“无目标”。**Hungarian 匹配是训练损失分配步骤，不是原始 DETR 推理必须执行的算子。**

## 为什么密集输出需要去重

多个位置可能对同一目标产生重叠框。NMS 按分数选择框，再抑制与已选框高度重叠的候选。框的交并比为：

$$
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}
$$

构造例：两个面积均为 100 的框，交集为 80，则 IoU 为 $80/120\approx0.667$。若采用同类框 NMS、阈值 0.5，低分框会被抑制。拥挤场景中，两个人也可能高度重叠，因此阈值选择有召回率代价。

原始 DETR 利用集合训练减少重复预测，不依赖 NMS。其他 Transformer 检测器可能采用不同训练和后处理，不能把某个版本推广到整个家族。NMS 也可在 CPU、GPU 或其他加速实现上运行，并非天生属于 CPU。

## 检测质量怎样评价

先用 IoU 等规则定义预测是否匹配，再计算 precision、recall 和 AP。AP 的类别平均、IoU 阈值范围和数据集协议必须一致。高置信度不是经校准的正确概率；漏检率和误检率也会随阈值变化。

单帧检测无法保证轨迹连续。遮挡、相机运动和尺寸误差还会影响下游速度估计与规划。需要身份时应增加跟踪；需要轮廓时阅读[实例分割](instance-segmentation.md)。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载拆分

分别计骨干、neck、检测头和后处理。候选数影响排序与去重；query 数影响 decoder，但不等于场景真实目标数。训练时的匹配和损失不能塞入部署延迟。

小目标通常需要更密的输入或特征，这会增加骨干和头的工作量。三维检测还应注明深度来源和坐标变换，见 [BEV 感知](bev-perception.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [Faster R-CNN](https://arxiv.org/abs/1506.01497)
- [RetinaNet 与 Focal Loss](https://arxiv.org/abs/1708.02002)
- [DETR](https://arxiv.org/abs/2005.12872)
