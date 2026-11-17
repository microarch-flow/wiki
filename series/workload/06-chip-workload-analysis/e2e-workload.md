# 端到端驾驶工作负载：共享计算与关键路径

上级：[专题导读](README.md)

<span id="e2e-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么-e2e-必须按-latency-critical-path-拆而不是按模型拆" class="workload-legacy-anchor"></span>
<span id="系统瓶颈是同步不是算力" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


端到端系统可能共享大量编码，也可能包含多任务、候选生成和优化迭代。模型名称不能决定总延迟。分析要从传感器数据可用时刻，沿依赖追到可执行输出。

## 一次请求的阶段

典型阶段包括预处理、多路编码、空间融合、历史更新、目标/运动/占用头、规划与控制接口。联合训练可能改善共享表示，但部署时仍有多个算子和同步点。

构造依赖图：六路相机编码各 5 ms，可并行；融合 3 ms；两个任务头分别 2 ms 和 4 ms，可并行；规划等两个头完成后需 2 ms。若资源确实独立且忽略调度，关键路径为 $5+3+4+2=14$ ms，而不是所有节点时间之和。若并发争用同一设备，实际时间可能更长。

## 共享与分支要分别计量

共享骨干应只计一次，但不同任务的中间状态和输出仍占容量。某任务需要保留的高分辨率特征可能延长整个系统的存活区间。

条件分支会使执行时间随场景变化。规划候选数、目标数、稀疏体素数和优化停止条件都可能影响尾部，而平均 FLOPs 无法体现这些变化。

## 延迟、吞吐与截止时间

流水线可使多帧同时在不同阶段处理，提高吞吐，却未必降低单帧从采集到控制的延迟。更新率、排队和旧帧丢弃策略需要一起说明。

p99 是测量分位数，不能代替最坏情况保证。若任务有硬截止时间，还需限制输入、分支和资源争用，并建立可验证的执行上界。

## 评价方法

先确认端到端范围是否包含传感器等待、预后处理、主机传输和控制接口，再测各阶段与整条链。对共享模块做消融时同时检查任务质量，避免用更少输出换取未说明的速度提升。

算法职责见[规划导向端到端](../03-autonomous-driving-algorithms/planning-oriented-e2e.md)。本页不强制将每个系统映射成固定的“编码—BEV—规划”三段，也不由论文名称推断实际硬件能力。

<span id="演进对-workload-的影响" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [UniAD](https://arxiv.org/abs/2212.10156)
