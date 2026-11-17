# 占用世界模型：预测未来三维空间如何变化

上级：[专题导读](README.md)

<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="容量的乘法为什么访存先撑爆" class="workload-legacy-anchor"></span>
<span id="主流做法离散-occupancy-token-的自回归-rollout" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


占用世界模型预测未来的 occupied、free 或语义占用分布。与当前 [Occupancy 感知](../02-vision-and-3d-perception/occupancy-prediction.md)相比，它增加时间演化问题。输出更接近空间查询，不等于可以直接保证轨迹安全。

<span id="occupancy-world-model" class="workload-legacy-anchor"></span>

## OccWorld 的表示与生成

OccWorld 用基于重建的 scene tokenizer 将三维语义 occupancy 压成离散 token，再用 GPT 类时空 Transformer 自回归预测未来场景 token 和自车 token，解码为未来占用与自车轨迹。

原论文的一项配置使用 2 s 历史预测 3 s 未来。此处保留已核实的时间范围，不把未统一确认的采样频率或帧数补成规格。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 联合预测不等于动作条件评估

OccWorld 联合预测场景和自车运动。它不能被不加说明地改写成“给定任意候选动作，输出其后果”的统一 MPC 接口。若要比较候选动作，需要验证动作如何进入预测器以及训练是否支持这种使用方式。

论文中不同输入配置也必须分开：使用真值 occupancy 的结果，不能当作从相机到未来场景的完整端到端性能。感知预测输入会引入额外误差。

## 碰撞检查为什么不只是一次 lookup

构造例：自车宽 2 m，网格边长 0.5 m，车辆横向至少覆盖多个单元。规划要检查未来各时刻的车辆体积及其扫掠区域，并处理定位误差、离散时间间隔和未知区域。

仅查询轨迹中心点可能漏掉侧面障碍；仅检查离散时刻可能漏掉两帧之间的穿越。模型预测、tokenizer 重建和感知输入的误差都会影响判断。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 成本与误差怎样分解

稠密未来网格的规模随 $TXYZ$ 增长；压缩 token 可降低时序模型的输入规模，但增加编解码路径与有损表示。自回归的依赖、缓存策略以及输出解码时机需要按实现记录。

应同时报告不同预测时刻的误差、类别/可见性掩码、重建误差和下游轨迹指标。不能用单个平均 IoU 代替长期环境演化质量。

## 来源与延伸

- [OccWorld 原论文](https://arxiv.org/pdf/2311.16038)
- [Occ3D：可见性与占用评价](https://arxiv.org/abs/2304.14365)
