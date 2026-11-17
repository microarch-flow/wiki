# 规划导向端到端：让中间任务服务自车决策

上级：[专题导读](README.md)

<span id="planning-oriented-e2e" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="关键设计维度与工程边界" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


规划导向系统以自车的最终决策为目标，组织感知、预测与场景表示。它可以联合学习多个任务，也可以使用模仿损失、约束代价或候选优化；这些选择不是互斥分类。

## UniAD 的信息链

UniAD 连接跟踪、地图、运动预测、占用预测和规划等任务，通过 query 与共享特征交换信息。其重点是把前序任务与规划目标联系起来，而不是证明所有中间表示都应被删除。

不同任务的输出尺度不同：目标轨迹描述个体运动，占用图描述空间使用，自车规划输出可执行的未来轨迹。坐标、时间范围及不确定性要在交接处一致。

## 目标函数如何表达取舍

一个教学目标可以写为：

$$
J(\tau)=\lambda_{\rm im}L_{\rm imitation}(\tau,\tau^*)
+\lambda_{\rm col}L_{\rm collision}(\tau)
+\lambda_{\rm sm}L_{\rm smooth}(\tau)
$$

这表示轨迹接近示范、避开预测占用并保持平滑之间的权衡，不是 UniAD 全部实现的逐项复刻。原论文及补充材料包含模仿与碰撞相关目标，足以说明 BC 与规划导向可以同时存在。

损失权重必须结合单位和尺度调节。把碰撞惩罚写入目标，并不等于优化解一定无碰撞；预测错误、离散化与软约束都可能留下风险。

## 一个信息不足的反例

若上游只给出某车“最可能向左”的单一路径，而真实情况也可能直行，规划器可能低估冲突。联合训练可以改善表示，但不会凭空提供所有可能未来。多模态预测、置信度与保守边界仍需定义。

## 评价和计算路径

开放环评价比较预测轨迹与记录轨迹；闭环评价让自车动作改变后续状态。还应区分其他参与者是否响应，以及模拟器是否覆盖传感器与动力学误差。

运行成本按实际依赖图统计。多头共享骨干可节约重复编码，但也会引入跨任务同步。候选数、优化迭代和历史状态可能影响尾部延迟，详见 [E2E 工作负载](../06-chip-workload-analysis/e2e-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [UniAD 原论文](https://arxiv.org/abs/2212.10156)
- [UniAD 补充材料](https://openaccess.thecvf.com/content/CVPR2023/supplemental/Hu_Planning-Oriented_Autonomous_Driving_CVPR_2023_supplemental.pdf)
- [NAVSIM](https://arxiv.org/abs/2406.15349)
