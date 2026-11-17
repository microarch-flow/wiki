# Occupancy 感知：已占用、空闲与未知空间

上级：[专题导读](README.md)

<span id="occupancy-prediction" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与容量爆炸的真实账" class="workload-legacy-anchor"></span>
<span id="为什么它是通向-world-model-的桥" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


Occupancy 感知估计三维空间中的占用状态，语义 occupancy 还为占用位置分配类别。它能表达框以外的形状，但不等于完整、无误的三维真值。本页讨论当前场景估计；未来演化属于[占用世界模型](../05-world-model-and-generative/occupancy-world-model.md)。

## 三种状态不能混为二类

传感器命中位置支持“这里存在表面”的证据；射线经过的区域可能提供空闲证据；未观测或被遮挡的位置没有同等证据。模型可预测这些位置，但预测不是观测。

因此必须分别说明 occupied、free 和 unknown/未标注区域的编码及损失掩码。数据集可能不显式设置 unknown 类，而是忽略部分网格；这仍不允许把它们一律记为 free。

## 从观测到体素

常见路径先编码图像或点云，再通过几何映射、BEV/三维特征或隐式查询建立空间表示，最后为体素或查询点预测占用和语义。

体素中心由坐标原点、分辨率和索引确定。同一个 $[X,Y,Z]$ 数组若轴顺序或原点不同，空间含义就不同。与规划接口交换数据时还要说明时间戳、有效范围与未知区域处理。

构造例：覆盖 $100\times100\times8\,m$，体素边长 0.5 m，网格为 $200\times200\times16$，共 640,000 格。单个 FP16 占用值约 1.22 MiB；若物化 18 类 FP16 logits，则约 21.97 MiB。中间特征可能比最终标签大得多。

## 稠密与稀疏表示的取舍

稠密网格规则、便于卷积与索引，但空间和分辨率增大时成本迅速增长。稀疏表示只处理活跃位置，却要维护索引、邻接关系和变长数据；活跃率高或碎片化严重时未必更快。

“背景大部分为空”不直接等于“所有计算都可以跳过”。感知模型仍可能需要判断哪些位置为空；误删未知或低置信区域会改变任务。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 评价与规划边界

IoU 和语义 mIoU 衡量选定有效区域内的预测重叠。不同可见性掩码、类别集合和输入监督会改变评价口径。应同时关注小障碍、远距离、遮挡区域与时间稳定性。

规划查询的是车辆在未来时刻扫过的体积，而不是一个点的一次查表。栅格量化、定位误差和预测不确定性都可能影响碰撞判断。更完整的几何输出不能单独保证安全。

## 来源与延伸

- [Occ3D：三维占用基准](https://arxiv.org/abs/2304.14365)
- [SurroundOcc](https://arxiv.org/abs/2303.09551)
