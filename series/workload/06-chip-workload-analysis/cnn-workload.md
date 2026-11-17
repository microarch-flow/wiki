# CNN 工作负载：复用、分块与中间特征

上级：[专题导读](README.md)

<span id="cnn-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="standard-conv-为什么是-npu-最友好的-workload" class="workload-legacy-anchor"></span>
<span id="depthwise-group-conv-为什么相反" class="workload-legacy-anchor"></span>
<span id="早层和后处理另两类容易被忽略的成本" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


CNN 的成本取决于卷积形状、实现算法和数据驻留。卷积的局部复用提供优化机会，但是否计算受限，需要把工作量与指定边界的实际流量一起比较。

## 一个可复算的卷积

构造输入 $[1,16,32,32]$，输出通道 32，$3\times3$ 卷积、步长 1、填充 1。输出形状为 $[1,32,32,32]$：

$$
\mathrm{MAC}=32^2\times32\times16\times9=4{,}718{,}592
$$

对应约 9.44 MFLOP。FP16 输入 32 KiB、权重 9 KiB、输出 64 KiB。若各读写一次，流量为 105 KiB，理想算术强度约 87.8 FLOP/B。该假设要求复用成功，未计偏置与工作区。

若实现把每个卷积窗口显式展开成 im2col，中间矩阵和访问会增大；隐式 GEMM 不必物化这个完整矩阵。因此卷积公式不能直接给出实际片外流量。

## 分块需要同时满足什么

一个 tile 需要输入窗口、权重和累加器。相邻输出 tile 的输入可能重叠，形成 halo；过小的片上容量会使这些输入反复加载。输出通道切分可以复用输入，却可能增加权重调度或累加开销。

双缓冲能够重叠部分搬运与计算，但要付出额外容量，并且依赖无冲突的传输和执行资源。没有实测或调度分析时，不能假定所有传输都被隐藏。

## 深度卷积和特征融合

深度卷积显著减少乘加，却未同比减少输入输出字节。因此它可能更受带宽或启动开销影响，但仍需看尺寸与融合。

FPN 的多尺度特征、上采样和拼接会延长张量存活时间。算子 FLOPs 小不代表系统成本小；融合若消除了中间写回，改善可能来自流量而非峰值算力。

## 该测什么

分别测骨干、neck、任务头与后处理，并记录分辨率、batch、通道和布局。改变 tile、精度或算法后重新检查精度和流量。

卷积机制见 [CNN 骨干](../01-foundation-model-components/cnn-backbone.md)。片上存储方式见[缓存与 Scratchpad](../../storage/reading-and-reference/01-reading/cache-scratchpad-introduction.md)，避免在本页重复存储层级基础。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [NVIDIA：GEMM 与数据复用](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html)
- [MobileNet](https://arxiv.org/abs/1704.04861)
