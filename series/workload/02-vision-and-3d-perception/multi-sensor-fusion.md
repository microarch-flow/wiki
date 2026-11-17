# 多传感器融合：先对齐证据，再组合表示

上级：[专题导读](README.md)

<span id="multi-sensor-fusion" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


融合的目标是利用互补观测，改善单个传感器难以解决的问题。增加传感器也增加标定、同步、故障和数据搬运的复杂度。融合收益应以联合系统的任务结果验证。

## 先确定共同参考

相机提供丰富外观，LiDAR 提供几何采样，雷达可提供与其测量方式相关的距离和速度信息。融合前要约定坐标系、时间基准、有效范围和置信度。

构造例：两路观测相差 50 ms，目标相对速度为 20 m/s，位置已经相差 1 m。仅用同一个外参投影不足以补偿这个时间差；自车和目标运动也应分开处理。

## 三个融合位置

早期融合组合原始或低层数据，保留细节但要求较严的对齐。中间融合让各传感器先编码，再在特征空间交互。后期融合组合目标或轨迹结果，接口更紧凑，但已被各分支丢弃的信息难以恢复。

BEVFusion 把相机和 LiDAR 特征对齐到 BEV，便于共享空间任务。其他方法可以通过投影、点级采样或交叉注意力实现。不能把“多模态”都归为 BEV，也不能假定融合必须用全局 attention。

## 缺失与错误如何传播

融合器应面对真实异常：某路输入缺失、延迟、外参漂移或质量退化。训练时使用随机丢弃可以帮助适应缺失，但不等于证明系统能处理所有故障。

例如相机投影误差把车的外观特征采到背景，可能污染原本准确的几何特征。学习权重能否抑制这类错误需要专门实验；更高平均精度不能替代降级测试。

<span id="计算结构与那个同步瓶颈" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 成本沿数据路径统计

每路编码器可以并行，但融合阶段要等待它所需的输入。端到端延迟包含输入到齐、坐标变换、采样、特征交换和输出头；不是各分支时间简单取最大后结束。

应记录相机数、分辨率、点数、历史长度及失配场景。传感器接口带宽、主存流量和片上通信属于不同边界，不能把原始输入字节数当成全部内存流量。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [BEVFusion](https://arxiv.org/abs/2205.13542)
- [PointPainting](https://arxiv.org/abs/1911.10150)
