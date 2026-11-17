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

BEVWorld 原论文 v3 先用多模态 tokenizer 把相机与 LiDAR 编码为 BEV latent，再用序列 diffusion 预测未来 latent，以高层动作 token 为条件。解码器通过体素与射线渲染重建多视角图像和点云。

这个案例同时具有 BEV、latent、diffusion 和观测生成四个属性，直接说明它们不是互斥分类。也不能仅因内部采用二维组织，就把最终输出和解码成本删除。

## 保留什么、压缩什么

BEV 统一了平面坐标，便于多任务共享，但高度、遮挡、外观和细粒度几何怎样编码取决于通道与解码器。一个二维特征图可以隐式携带三维信息，却不等于没有信息损失。

若 $H\times W$ 网格每格有 $C$ 维 latent，容量与 $HWC$ 成正比。空间分辨率提高、历史增多和预测时域扩大都可能增加成本；具体是否乘到同一张量上取决于网络结构。

<span id="基本结构与-workload-的三个决定因素" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 评价与工作负载

应分别检查 latent/重建质量、未来场景预测和下游任务收益。真实 LiDAR 输入、预测几何输入和纯相机配置具有不同信息条件，不能直接混报性能。

成本必须包含实际执行的 tokenizer、时序生成和解码路径；采样次数见[扩散世界模型](diffusion-for-world-model.md)。BEV 并不固定处于“视频最重、latent 最轻”之间。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [BEVWorld 原论文 v3](https://arxiv.org/html/2407.05679v3)
- [BEVFormer：当前感知的对照](https://arxiv.org/abs/2203.17270)
