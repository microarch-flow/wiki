# BEV 感知：把多视角观测对齐到地面坐标

上级：[专题导读](README.md)

<span id="bev-perception" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与那个大中间体" class="workload-legacy-anchor"></span>
<span id="为什么-bev-是-0203-的转折点" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


鸟瞰图（BEV）是一种空间组织方式。它把来自相机、LiDAR 等传感器的信息放到统一的平面坐标中，便于表达目标、地图和运动。BEV 既不限定输入传感器，也不等于某一种 Transformer。

## 坐标变换为什么需要深度

图像像素只确定一条射线。给定相机内参 $K$、像素齐次坐标 $u$ 和沿光轴定义的深度 $z$，相机坐标可写为 $p_c=zK^{-1}u$；再用外参变到车辆坐标。没有深度时，同一像素对应射线上的多个可能位置。

深度估计、标定与时间对齐因此都会影响 BEV。统一坐标只统一表达，不会消除观测误差，也不会让遮挡区域自动变成已知空间。

## Lift-Splat 与查询式方法

LSS 为图像位置预测深度分布和特征，将它们沿多个深度位置提升到三维，再汇聚到 BEV 网格。深度分布表达多个位置假设；splat 汇聚多个来源对同一网格的贡献。

BEVFormer 使用网格状 BEV query，从多相机图像特征的相关位置采样，并通过时序模块融合历史 BEV。它需要定义参考点、可见相机、采样点和历史坐标对齐，不能简化为全图稠密 attention。

PETR 则把三维坐标信息编码进图像特征，用 object query 做三维检测。它不是与 BEVFormer 相同的“先构建稠密 BEV 网格”路径。

## 一个网格例子

构造覆盖范围为 $100\,m\times100\,m$，分辨率为 $0.5\,m$，得到 $200\times200=40{,}000$ 个平面单元。每格 128 通道、FP16 的特征为 9.77 MiB。若两轴分辨率都提高一倍，单元数增加四倍。

这只是二维特征容量。LSS 的中间规模还与相机数、图像特征尺寸和深度分箱数有关；BEVFormer 则与 query、采样点及时间历史有关。不能只看最终 BEV 大小估算所有方法。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 时序融合与实现边界

历史特征通常需要按自车运动变换到当前坐标；动态目标的运动无法仅靠自车补偿对齐。时间戳误差、延迟与遮挡要在任务评估中单独观察。

朴素 LSS 可以产生很大的视锥特征，但它不是必须物化的算法契约。BEVPoolv2 通过实现重组避免构造大型视锥中间张量，说明逻辑计算图与物理流量需要分开分析。

BEV 的二维组织适合多任务共享；高度方向信息如何保留由表示决定。需要显式三维占用时阅读 [Occupancy 感知](occupancy-prediction.md)，性能分析见 [BEV 工作负载](../06-chip-workload-analysis/bev-workload.md)。

## 来源与延伸

- [Lift-Splat-Shoot](https://arxiv.org/abs/2008.05711)
- [BEVFormer](https://arxiv.org/abs/2203.17270)
- [PETR](https://arxiv.org/abs/2203.05625)
- [BEVPoolv2](https://arxiv.org/abs/2211.17111)
