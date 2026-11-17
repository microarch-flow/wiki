# Occupancy 工作负载：三维分辨率、稀疏性与输出解码

上级：[专题导读](README.md)

<span id="occupancy-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="容量为什么是-occupancy-的第一约束" class="workload-legacy-anchor"></span>
<span id="dense-与-sparse-的取舍一个-determinism-难题" class="workload-legacy-anchor"></span>
<span id="时序与查询horizon-和-collision-check" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


Occupancy 的资源规模由空间范围、分辨率、通道与时间轴共同决定。稠密和稀疏是实现选择；占用任务本身不必固定使用稠密三维卷积。

## 分辨率怎样放大容量

构造范围 $100\times100\times8\,m$、边长 0.5 m，得到 $200\times200\times16$ 网格。每格 64 通道、FP16 的中间特征约 78.13 MiB。

若三轴分辨率都提高一倍，单元数增加八倍，约 625 MiB。若只提高平面分辨率，则增加四倍。不能不说明轴就统一称为“分辨率翻倍，容量翻四倍”。

最终 18 类 logits、单通道占用概率和 uint8 类别标签大小不同。峰值容量还取决于哪些层或未来时刻同时存活。

## 稀疏计算为什么不按占用率直接缩放

稀疏张量需要坐标与索引；邻域算子要寻找活跃位置之间的关系。活跃体素的聚集程度、邻接数和负载分配会影响性能。

构造“活跃率 10%”只说明一种计数。它不意味着时延恰好为稠密实现的 10%，也不说明未知空间可以不预测。稀疏化若改变任务覆盖范围，还应重新评价精度。

## 当前感知与未来生成分开

当前感知主要从观测恢复空间；世界模型还需预测未来。若输出 $T$ 个完整网格，输出元素数随 $T$ 增加；内部预测器可能使用压缩 token，不能把所有层都按原始体素数计。

只有应用需要完整输出时才解码相应网格。候选轨迹可否在 latent 中评分、是否仍需几何约束，应由任务设计决定。

## 测量重点

记录体素尺寸、有效区域、活跃率分布、索引格式、编解码和后处理。测量应包含稀疏索引构造与不同密度场景，避免仅比较卷积核吞吐。

语义与未知空间定义见 [Occupancy 感知](../02-vision-and-3d-perception/occupancy-prediction.md)，未来场景案例见[占用世界模型](../05-world-model-and-generative/occupancy-world-model.md)。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [Occ3D](https://arxiv.org/abs/2304.14365)
- [OccWorld](https://arxiv.org/abs/2311.16038)
