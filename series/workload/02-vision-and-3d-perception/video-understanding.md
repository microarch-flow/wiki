# 视频理解：时间采样如何改变模型看到的问题

上级：[专题导读](README.md)

<span id="video-understanding" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与决定性的乘积" class="workload-legacy-anchor"></span>
<span id="从视频理解到-world-model" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


视频理解根据已有帧判断动作、事件或状态。未来视频生成属于另一个任务。输入都是视频，并不意味着监督目标、可用时间范围或部署方式相同。

## 三种时序处理方式

逐帧编码再聚合，先提取每帧特征，再通过池化、递推或时序模块组合。三维卷积在空间和时间窗口共同计算。视频 Transformer 则把时空 patch 作为 token，可采用全局、分解或局部 attention。

TimeSformer 研究分解的时空 attention，把空间与时间交互分开组织。这减少某些配对，但不能简单视为“与全时空 attention 完全相同的快速实现”，因为连接结构发生了改变。

## 帧数与时间跨度不是同一量

构造例：从 30 fps 视频每 4 帧取 1 帧，取 8 帧，首尾相隔 $7\times4/30\approx0.933$ s。若改成连续取 8 帧，首尾仅相隔约 0.233 s。输入张量大小相同，看到的运动范围却不同。

抽帧可降低成本，也可能丢失短暂事件或产生时间混叠。任务需要估计速度时，时间间隔必须作为已知条件处理。

## 在线与离线的可用信息

离线片段分类可以读取整个片段；在线系统在时刻 $t$ 不能使用真实的未来帧。模型若用双向上下文，部署时必须等待窗口结束，或改成因果路径。等待本身属于算法延迟。

状态缓存能复用过去特征，但缓存更新、坐标对齐和历史截断会影响结果。流式系统应测试状态重置和长时间运行，而不是仅测试独立短片段。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载中的时间轴

若每帧 196 个 token、输入 8 帧，则共有 1568 个时空 token。全局 attention 的配对数约为单帧的 64 倍；逐帧骨干工作量则约为 8 倍。分解或窗口方法采用不同公式，应按实际连接计数。

评价指标随任务变化：动作分类准确率、时序定位、跟踪和未来预测不能互相替代。未来环境预测的任务边界见[世界模型基础](../05-world-model-and-generative/world-model-fundamentals.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [TimeSformer](https://arxiv.org/abs/2102.05095)
- [I3D](https://arxiv.org/abs/1705.07750)
