# 工作负载分析方法：从执行路径推导资源需求

上级：[专题导读](README.md)

<span id="workload-analysis-methodology" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="方法论的边界" class="workload-legacy-anchor"></span>
<span id="从算法到-workload-的五步流程" class="workload-legacy-anchor"></span>
<span id="1-抽象输入输出和状态" class="workload-legacy-anchor"></span>
<span id="2-拆成-stage而不是只看-end-to-end-graph" class="workload-legacy-anchor"></span>
<span id="3-定义主导成本而不是罗列所有算子" class="workload-legacy-anchor"></span>
<span id="4-用统一维度填写-workload-characterization" class="workload-legacy-anchor"></span>
<span id="5-映射到硬件-wiki-和-archax" class="workload-legacy-anchor"></span>
<span id="典型-workload-的分析入口" class="workload-legacy-anchor"></span>
<span id="端侧云端和仿真的口径" class="workload-legacy-anchor"></span>
<span id="常见误区" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


工作负载不是模型名称，而是模型在指定输入、阶段、实现和约束下的执行实例。分析应先确定任务与调用路径，再计工作量、流量、容量和依赖，最后用测量检验瓶颈判断。

## 第一步：固定比较对象

记录模型版本、输入形状、batch、精度、训练或推理阶段、生成长度、质量要求和设备。端侧还要记录更新频率与截止时间，服务端还要记录并发与到达分布。

构造例：“7B 模型很慢”不足以分析；“batch=1、FP16 权重、自回归生成、每步一个新 token，权重无法片上驻留”才给出可检查的流量假设。量化或 batch 改变后，应重新计算。

## 第二步：画实际执行图

区分一次性编码、循环体、条件分支、跨设备传输和最终后处理。每个节点标明输入输出与状态；每条边标明依赖及是否物化。

训练里的匹配、教师分支和反向传播，不应进入没有它们的部署路径。多步生成也必须明确单次调用是否已经包含全部预测时域。

## 第三步：分别计量四个量

| 量 | 口径 | 容易犯的错误 |
| --- | --- | --- |
| 工作量 F | 明确 1 MAC=2 FLOP、数据类型与算子范围 | 把 MAC 与 FLOP 混用 |
| 流量 Q | 指定 HBM、DRAM、SRAM 或互连边界 | 把张量容量当重复访问总量 |
| 峰值容量 | 同时存活的权重、激活、状态和工作区 | 把所有层激活无条件相加 |
| 依赖与调用 | 串行深度、并行轴、分支和循环次数 | 把工作量倍数当时延倍数 |

基础形状见[张量形状与计算量](../00-overview/tensor-shapes-and-cost.md)。逻辑索引不足以推出实际 bank 冲突、DRAM 行命中或 NoC 路由，后者还依赖布局、映射和硬件。

## 第四步：建立有条件的性能估算

在选定边界上，算术强度 $I=F/Q$。简化 Roofline 上界为：

$$
P\le\min(P_{\rm peak},\,BW\times I)
$$

相应的时间下界为 $\max(F/P_{\rm peak},Q/BW)$。计算和传输都必须完成，所以即使二者串行，这个下界仍成立。要接近它，较慢的一侧须接近有效上限，较快一侧的工作须能被掩盖。启动、同步、依赖和小矩阵利用率都可能拉长实际时间。

构造例：1 GFLOP、100 MB 流量，设备上界为 10 TFLOP/s 和 100 GB/s。理想计算时间 0.1 ms、传输时间 1 ms，下界为 1 ms。若测得 4 ms，应继续查有效带宽、额外流量与调度，不能直接声称理论模型已经解释了全部时间。

## 第五步：测量并做敏感性分析

记录 warm-up、测量区间、同步方式、重复次数、分位数和是否包含预后处理。改变一个关键变量，如长度、batch、采样 NFE 或活跃体素数，检查延迟是否按推导变化。

优化前后同时检查任务质量。p99 是样本分布的分位数，不是最坏执行时间证明；硬截止时间需要更强的上界分析和运行条件约束。

## 与其他系列和架构模型连接

[存储层级与数据路径](../../storage/01-memory-hierarchy/README.md)解释容量、带宽与复用；[NoC](../../interconnect/NOC/README.md)解释路由、流控和通信；[计算微架构](../../microarchitecture/README.md)承接执行结构；[推理运行时](../../inference-runtime/README.md)承接缓存与服务调度。链接到规划中内容时，应按目标页状态使用。

若将结果转为 Archax 实验输入，可以列资源容量、连接、执行依赖与所需算子能力，但本系列不证明某版本已经支持这些能力。要运行实验，仍需对照当前编译器、模拟器和接口契约。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [Roofline 原始技术报告（UC Berkeley，2008）](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.html)
- [NVIDIA：矩阵乘与算术强度](https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html)
