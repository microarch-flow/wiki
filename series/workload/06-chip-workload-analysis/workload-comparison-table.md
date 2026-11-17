# 工作负载比较索引：先选阶段，再看资源

上级：[专题导读](README.md)

<span id="workload-comparison-table" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="总表" class="workload-legacy-anchor"></span>
<span id="端侧优先级" class="workload-legacy-anchor"></span>
<span id="云端优先级" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


本表用于找到对应案例，不给模型家族排固定成本名次。每条判断都需要输入形状、阶段、精度和实现条件。

## 按执行特征定位

| 工作负载 | 关键规模变量 | 优先核对的问题 | 案例 |
| --- | --- | --- | --- |
| CNN | 输出空间、通道、核、分组 | tile 复用与中间物化 | [CNN](cnn-workload.md) |
| Transformer | token、宽度、层、KV 头、batch | 当前是 encoder、prefill 还是 decode | [Transformer](transformer-workload.md) |
| SSM | 状态宽度、通道、序列、batch | 训练 scan 与流式状态分开 | [SSM](ssm-workload.md) |
| MoE | token、top-k、专家与路由分布 | 最忙专家与跨设备交换 | [MoE](moe-workload.md) |
| BEV | 相机、深度、网格、历史 | 视角变换是否物化视锥 | [BEV](bev-workload.md) |
| Occupancy | XYZ、通道、时间、活跃率 | 稀疏元数据与解码容量 | [Occupancy](occupancy-workload.md) |
| 驾驶 E2E | 共享分支、候选、动态目标 | 关键路径与数据年龄 | [E2E](e2e-workload.md) |
| VLA | 动作表示、执行块、NFE | 重推理频率与动作频率 | [VLA](vla-workload.md) |
| 世界模型 | 调用图、候选、时域、NFE | 一次求值已包含哪些轴 | [世界模型](world-model-workload.md) |

## 两个不能直接比较的例子

小 batch decode 与大 batch prefill 使用相同权重，却有不同矩阵形状与复用。只报模型参数量无法解释两者性能。

同样预测 16 帧，一种模型逐帧递推，另一种在 10 次求值中更新整段序列。二者都“多步”，但依赖和调用数不同。

需要建立自己的比较表时，先填写[记录字段](workload-characterization-axes.md)，再使用[分析方法](workload-analysis-methodology.md)推导，不复制没有条件的瓶颈标签。
