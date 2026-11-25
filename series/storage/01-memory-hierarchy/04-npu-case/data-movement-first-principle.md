---
search:
  exclude: true
---

# NPU 数据搬运与复用（原入口）

本页已并入[NPU 连算三个块，为什么外存只读 4 B 权重，阵列却要接收 12 B？](./npu-memory-hierarchy.md)。原文各小节可直接在新文中阅读。

<div markdown="1" data-storage-redirect="true">

- <span id="npu-数据搬运如何权衡复用时间与能耗"></span>[按边界比较三块计算的搬运量](./npu-memory-hierarchy.md#traffic)
- <span id="数据搬运优先原则在-npu-设计中的体现"></span>[从外存跟到阵列入口](./npu-memory-hierarchy.md#paths)
- <span id="这页在回答什么问题"></span>[同一笔工作在哪里节省了搬运](./npu-memory-hierarchy.md#traffic)
- <span id="计算所需的数据跨越哪些边界"></span>[权重、激活和结果经过哪些接口](./npu-memory-hierarchy.md#paths)
- <span id="同一任务两种权重驻留策略"></span>[比较每块重取与跨块保留](./npu-memory-hierarchy.md#traffic)
- <span id="搬运量减少以后还要检查什么"></span>[时间和能耗还取决于什么](./npu-memory-hierarchy.md#energy)
- <span id="一句话理解"></span>[分别统计外存和阵列入口的流量](./npu-memory-hierarchy.md#traffic)
- <span id="建模启示"></span>[记录每个接口的活动](./npu-memory-hierarchy.md#model)
- <span id="接下来怎么读"></span>[继续看激活供给与片上带宽](./npu-memory-hierarchy.md#next)

</div>
