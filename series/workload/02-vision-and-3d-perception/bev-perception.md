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

LSS 为每个图像特征位置产生一份上下文向量 $c$ 和一份离散深度分布。深度箱 $d$ 上的向量是 $p(d)c$。这一步叫 lift。内外参给每个“位置、深度”组合确定空间坐标，再把落入同一平面网格的向量按通道求和，这一步叫 splat。[LSS 原论文 §3](https://arxiv.org/html/2008.05711v1)

取两个图像位置，各有一个标量特征。设车体坐标 $X$ 向前、$Y$ 在本例中向右。相机正对前方，水平平移为零。令 $q$ 是归一化横坐标，则深度为 $z$ 的点在平面上为 $(X,Y)=(z,zq)$。网格边长 1 m，从原点起取整分箱，只考虑有效范围内的点。

| 图像特征 | 深度（m） | 概率 × 特征 | 平面坐标（m） | 网格索引 |
| --- | ---: | --- | --- | --- |
| A，$q=0.1,\ c=4$ | 2 | $0.75\times4=3$ | $(2,0.2)$ | $(2,0)$ |
| A | 4 | $0.25\times4=1$ | $(4,0.4)$ | $(4,0)$ |
| B，$q=0.3,\ c=6$ | 2 | $0.5\times6=3$ | $(2,0.6)$ | $(2,0)$ |
| B | 4 | $0.5\times6=3$ | $(4,1.2)$ | $(4,1)$ |

两个近处假设落入同一格，$(2,0)$ 得到 $3+3=6$。两个远处假设落入不同格，分别得到 1 和 3。读者可用 $6+1+3=4+6$ 检查本例的贡献是否漏掉。成立条件是每个位置的深度概率和为 1、所有点都在有效范围内、汇聚采用求和。这里得到的是特征值，物体是否占用该格还要由任务头判断。

BEVFormer 从另一端出发。为某个 BEV 格放置不同高度的三维参考点，投影到可见相机，再在投影附近依学习到的偏移采样图像特征。该格的 query 对采样特征加权汇聚，时序模块另行融合历史 BEV。前一种方法要查“这个像素把贡献送到哪里”，后一种要查“这个网格到哪些图像位置取数”。两条路径所需的索引与临时张量不同。[BEVFormer 空间交叉注意力](https://arxiv.org/html/2203.17270v2)

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
