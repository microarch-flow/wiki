# 实例分割：把同类目标分成不同个体

上级：[专题导读](README.md)

<span id="instance-segmentation" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="在-ad-和机器人中的意义" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


实例分割为每个可数目标输出类别、置信度和掩码。两辆车即使相邻，也应有两个实例。它与语义分割共享图像特征，但输出对象和评价规则不同。

## 两种常见生成路径

Mask R-CNN 先检测候选区域，再通过 RoIAlign 提取区域特征，并行预测类别、框和局部掩码。RoIAlign 用连续坐标插值，减少区域量化引起的错位；它不增加原图中不存在的细节。

另一类方法使用 query 表示实例。query 与像素特征结合生成掩码，再进行集合匹配训练。Mask2Former 使用 masked attention，把特定 query 的交互限制到其预测区域，统一处理语义、实例和全景分割任务。统一架构不意味着三种任务的标签定义相同。

## 掩码怎样成为一个实例

构造例：某 query 输出“车”的得分 0.9，以及 $4\times4$ 的前景概率图。选择阈值后得到二值区域，再映射回图像。若两个 query 覆盖同一辆车，仍需由训练设计或输出组合规则处理重复。

掩码 AP 通常用掩码 IoU 判断匹配；框 AP 衡量的是包围框。细长目标的框可能准确，掩码边界却差，因此两者不可替代。

全景分割进一步为可数目标分配实例身份，并为道路、天空等不可数区域分配语义类别。跨帧身份则属于跟踪或视频实例分割，单帧实例编号不能直接当成永久 ID。

<span id="计算结构与硬件瓶颈的分叉" class="workload-legacy-anchor"></span>
<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 工作负载与边界

区域方法的成本随候选数、RoI 尺寸与保留实例数变化；query 方法则与 query 数、像素特征分辨率和 decoder 层数有关。最坏场景可能包含大量目标，不能只用平均目标数预算延迟。

若对 100 个 query 物化 $256\times256$ 的 FP16 掩码 logits，仅这一项为 12.5 MiB。这是构造容量例；实际系统可能分块、低分辨率计算或提前筛选。

实例轮廓能改善几何描述，却不自动给出深度、刚体运动或遮挡后的完整形状。下游仍需坐标与时间接口。基础类别定义见[语义分割](semantic-segmentation.md)。

## 来源与延伸

- [Mask R-CNN](https://arxiv.org/abs/1703.06870)
- [Mask2Former](https://arxiv.org/abs/2112.01527)
