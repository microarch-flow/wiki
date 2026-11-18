# BEV 世界模型：在统一空间中预测场景演化

上级：[专题导读](README.md)

<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


BEV 世界模型在鸟瞰坐标组织内部状态或预测结果。它可以输出 BEV 特征、空间占用，也可以进一步解码图像和点云。BEV 只约束空间表达，不能直接推断是否使用解码器或多步采样。

## 从当前感知到未来预测

[BEV 感知](../02-vision-and-3d-perception/bev-perception.md)主要估计当前场景。世界模型还需学习时间演化，并明确未来受哪些条件控制。历史特征通常要补偿自车运动；动态目标仍需单独预测。

构造例：当前 BEV 中一辆车位于前方 10 m。若只将历史网格按自车位移平移，只校正了观察坐标，并没有预测那辆车下一秒会加速还是转弯。

<span id="bev-world-model" class="workload-legacy-anchor"></span>

## BEVWorld 的完整路径

沿 BEVWorld 原论文 v3 的推理路径看一段未来，先区分哪些数据在起始时刻已经可用。

| 阶段 | 输入 | 输出及其用途 |
| --- | --- | --- |
| 编码历史 | 已观测的多视角相机与 LiDAR | 多模态 tokenizer 产生按鸟瞰坐标组织的历史 latent |
| 有条件地预测 | 历史特征、车辆高层动作 token、未来位置的噪声 | 序列扩散模型反复更新未来 latent，动作条件在预测中起作用 |
| 解码未来 | 预测的 BEV latent 与相应射线 | 解码器构造体素表示，经渲染得到未来多视图图像和点云 |

若保持历史和初始噪声相同，只更换动作条件，两次预测的差异可用来检查模型是否使用了条件。若保持动作相同、只更换噪声，则可观察同一条件下生成的多种未来。前者需要有动作覆盖的数据来验证响应，后者的多样性需要和实际未来的分布比较，才能评价概率校准。[BEVWorld 原论文 §3](https://arxiv.org/html/2407.05679v3)

## 保留什么、压缩什么

BEV 统一了平面坐标，便于多任务共享，但高度、遮挡、外观和细粒度几何怎样编码取决于通道与解码器。一个二维特征图可以隐式携带三维信息，却不等于没有信息损失。

若 $H\times W$ 网格每格有 $C$ 维 latent，容量与 $HWC$ 成正比。空间分辨率提高、历史增多和预测时域扩大都可能增加成本；具体是否乘到同一张量上取决于网络结构。

<span id="基本结构与-workload-的三个决定因素" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 评价与工作负载

应分别检查 latent/重建质量、未来场景预测和下游任务收益。真实 LiDAR 输入、预测几何输入和纯相机配置具有不同信息条件，不能直接混报性能。

需要未来图像和点云时，将 tokenizer、时序生成和解码全部纳入成本。单次求值已含未来序列时的计算例见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [BEVWorld 原论文 v3](https://arxiv.org/html/2407.05679v3)
- [BEVFormer：当前感知的对照](https://arxiv.org/abs/2203.17270)
