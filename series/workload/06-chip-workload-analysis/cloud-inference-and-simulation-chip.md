# 云端推理与仿真：吞吐、并发和通信的取舍

上级：[专题导读](README.md)

<span id="cloud-inference-and-simulation-chip" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


云端资源可以容纳更大模型与更多并发，但仍受到质量、延迟、容量、功耗和成本约束。在线服务、离线生成和策略训练不是同一种 workload。

## 三类作业的目标不同

| 作业 | 首要度量 | 常见限制 |
| --- | --- | --- |
| 在线推理 | 请求延迟、token 间隔、吞吐与 SLO | 排队、状态容量、批处理等待 |
| 离线生成或仿真 | 满足质量的样本吞吐 | 采样、解码、存储与数据管道 |
| 训练与策略学习 | 有效更新速度、收敛与资源成本 | 反向激活、优化器、集体通信 |

大 batch 可以摊薄权重读取，却增加激活和状态容量，也可能增加等待。离线作业可接受的调度不一定满足在线请求。

<span id="大-batch-如何反转端侧的瓶颈" class="workload-legacy-anchor"></span>
<span id="云端-workload-的几种形态" class="workload-legacy-anchor"></span>
<span id="与端侧的分工端云协同的-workload-边界" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 多设备并行搬走了哪些成本

数据并行复制模型并分配样本；张量并行切分算子，增加归约或交换；流水并行切分层，产生阶段间传输和气泡；专家并行按专家分配 MoE 参数，增加 token 路由。

这些策略受模型、batch 和互连条件影响。拓扑带宽、拥塞和同步决定实际代价，不能只用设备数量除单卡时间。MoE 的路由案例见 [MoE 工作负载](moe-workload.md)。

## 生成系统还包含数据管道

未来视频或点云生成需要读取条件、运行生成器、解码、过滤、标注或评分，再存储结果。只测生成器的内核吞吐会漏掉其他阶段。

构造例：生成器每秒产生 100 个候选，但质量筛选仅保留 20 个，有效样本吞吐为 20/s。扩容应关注整个管道的有效产出，而不只看 GPU 利用率。

## 证据与跨专题入口

报告输入输出分布、并发、质量过滤、精度、设备数量和通信布局。容量、通信和排队可以限制规模扩展；云端不代表资源无限，也不代表所有模型必须云部署。

服务调度归于[推理与运行时](../../inference-runtime/README.md)，芯片互连机制归于[芯片与系统互连](../../interconnect/README.md)。本页负责把作业目标连接到可测资源。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [Efficiently Scaling Transformer Inference](https://arxiv.org/abs/2211.05102)
- [PagedAttention / vLLM](https://arxiv.org/abs/2309.06180)
