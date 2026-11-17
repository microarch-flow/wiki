# 端侧推理约束：从截止时间推导芯片需求

上级：[专题导读](README.md)

<span id="edge-inference-chip-requirements" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么端侧不能只看-tops" class="workload-legacy-anchor"></span>
<span id="端侧需求的六个层次" class="workload-legacy-anchor"></span>
<span id="流式与确定性端侧最难的两件事" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


端侧推理首先受到任务质量、响应时间、功耗和容量约束。峰值 TOPS 只描述部分算术能力，不能替代完整链路的预算。

## 从周期中分配预算

构造系统每 100 ms 更新一次决策。若采集与输入对齐占 15 ms、后处理和控制接口占 10 ms，则留给模型与调度的预算最多为 75 ms；还需为争用和波动留出适当余量。这个算例是预算分解，不是测量结果。

吞吐达到 10 次/s 不保证每次延迟小于 100 ms。流水线可能维持输出速率，却让每个结果基于较旧观测。应同时记录数据年龄与端到端时延。

## 容量先于带宽可行性

权重、持久状态、峰值激活和工作区必须放入可用存储。超过容量后可能需要分片、卸载或重算，这会改变流量与延迟，不能继续使用原来的带宽估算。

片上 SRAM 应依据 tile、状态与双缓冲需求配置，不按模型总参数直接拍数。共享缓存和显式 Scratchpad 有不同管理方式，见[存储基础](../../storage/reading-and-reference/01-reading/cache-scratchpad-introduction.md)。

## 特殊算子来自实际执行图

卷积和 GEMM 之外，几何采样、归约、归一化、排序、稀疏索引与状态更新可能位于关键路径。若某算子必须回到主机执行，需计入传输与同步，而非只比较该算子的 FLOPs。

是否需要特定 DMA 或 NoC 能力，应由布局、映射与并行方案推导。算法中出现“采样”并不直接证明某种硬件指令是唯一实现。

## 精度与实时性分别验收

量化可减小计算和流量，但校准范围、累加精度及任务误差要单独确认。控制系统还应测试动作偏差与闭环成功率。

报告平均、分位及观测到的最大时延，并注明采样范围。观测最大值不是理论最坏上界；硬实时论证需要限制运行条件和分析执行边界。本页不把 p99 当作确定性保证。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [NVIDIA：算术强度与硬件上界](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html)
