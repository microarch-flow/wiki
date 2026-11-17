# LiDAR 点云：从不规则采样到可计算的空间表示

上级：[专题导读](README.md)

<span id="lidar-point-cloud-processing" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与稀疏的真实账" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


LiDAR 提供带空间坐标的采样点，常附带强度、时间或其他属性。点数随距离、遮挡和扫描条件变化。点云描述被采样到的表面，不等于完整的实体体积。

## 先统一坐标和时间

输入可写为 $[N,F]$，其中前三维通常是坐标，其余属性须明确。机械扫描或多束采样并非在同一瞬间完成；运动平台可能需要逐点运动补偿。裁剪范围、地面处理和采样策略也会改变后续输入。

构造例：车辆以 10 m/s 行驶，100 ms 的扫描期间移动 1 m。若忽略运动，静态物体也可能在聚合点云中变形。这个位移只由假设速度和时间计算，不是某型号传感器规格。

## 三类常见处理路径

| 路径 | 组织方式 | 主要代价 |
| --- | --- | --- |
| 逐点网络 | 对点编码，再以对称归约或邻域聚合组合 | 邻域搜索、变长访问，需保持排列性质 |
| 体素化 | 按三维网格聚合点，再用稀疏或稠密网络 | 量化误差、索引构造、活跃体素分布 |
| 柱状表示 | 在平面单元内聚合高度方向的点 | 便于二维骨干，但压缩了垂直结构 |

PointNet 用共享逐点变换和对称归约处理无序输入。PointPillars 把点编码到平面柱，再形成伪图像，连接二维检测网络。两者的索引结构与输出语义不同。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 体素化的边界条件

若坐标原点为 $o$、体素边长为 $\Delta$，可用 $\lfloor(p-o)/\Delta\rfloor$ 得到索引。边界点如何取舍、越界点如何处理、每格最多保留多少点都必须明确。

以每格最多 32 点为例，拥挤单元中的第 33 个点可能被截断或采样替换。这会同时影响精度和工作量。固定上限使张量更规则，却不是无损变换。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载与融合

前处理、排序/散列、点到体素归约和稀疏邻接可占据明显成本，不能只计后端卷积。平均活跃体素数不足以描述尾部延迟，应记录空间分布和高密度场景。

与相机融合时，还需要外参和采样时间对齐；投影落在图像上不等于同一个真实表面可见。接口见[多传感器融合](multi-sensor-fusion.md)。

## 来源与延伸

- [PointNet](https://arxiv.org/abs/1612.00593)
- [PointPillars](https://arxiv.org/abs/1812.05784)
- [VoxelNet](https://arxiv.org/abs/1711.06396)
