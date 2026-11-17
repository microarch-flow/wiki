# TP、PP 与 DP：切分模型还是复制服务

<div class="inference-legacy-anchors" aria-hidden="true"><span id="11-集群并行tp-pp-ep-cluster-parallelism"></span></div>

上级：[本专题导读](README.md)

多设备推理有两类基本目的：让一个模型实例能够执行，或增加可同时服务的请求。TP、PP 与 DP 采用不同方式，产生的内存布局和通信路径也不同。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="tp张量并行megatron-式"></span></div>

## TP：在层内切分张量

张量并行将权重或激活按维度切到多个 rank。以 $Y=XW$ 为例，按输出列切分 W，可分别得到 Y 的不同列；若下一算子需要完整 Y，则还需合并或重新组织布局。

按输入维切分时，各 rank 可以产生部分和，随后进行规约。经典 Megatron 式层结构常出现特定次数的集合通信，但不同算子融合和切分方案可能不同，不能把“每层固定两次 all-reduce”作为所有实现的定义。

TP 的收益是分担容量和计算，代价是层内通信与同步。它可以跨节点执行；NVLink 不是正确性的必要条件。网络带宽、启动延迟和实际拓扑决定可用性能。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="pp流水线并行"></span><span id="3-pp-气泡"></span></div>

## PP：按层划分阶段

流水线并行将不同层放到不同阶段。请求的中间激活沿阶段传递，KV 通常随其层分布。多个微批可交错运行以利用各阶段。

在 P 个阶段耗时相等、m 个独立微批、只考虑理想填充与排空的模型中，阶段槽位利用率为 $m/(m+P-1)$。这个表达不能直接当作自回归服务的实际效率：微批依赖、采样回传、阶段失衡和调度都会改变时间线。

阶段之间传输多少数据，应按实际激活形状和数据类型计算，不能仅称为“小消息”。

## DP：建立多个服务副本

对于稠密模型，数据并行服务可以让多个完整副本处理不同请求。它主要增加吞吐与容量，单次模型执行本身通常不会因为增加副本而缩短。

排队减少后，用户延迟仍可能改善。请求路由、前缀缓存分布和副本冷启动会影响实际收益，见[副本管理](../08-serving-lifecycle/routing-and-scaling.md)。

MoE 框架中的 DP 与 EP 组合有特定 rank 组织方式，不能把所有 DP 都等同于完全独立的模型副本。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-各维如何重映射成本模型的量"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 先画 rank 布局，再算容量

只有当 TP、PP、DP 等是独立的设备网格维度时，设备数才等于这些维度的乘积。某些实现的专家组由已有维度共同构成，EP 不能再额外乘一次。

KV 也不总能直接除以 TP 数。若 KV 头按 rank 均匀切分，容量可以相应分担；若 TP 数超过可切分 KV 头数，某些 rank 可能复制 KV。应逐层列出分片和复制。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-tp-通信成本为什么-tp-吃-nvlink"></span><span id="推理-vs-训练的差异架构师视角"></span></div>

## 通信成本与关键路径

对一次指定通信，可用 $\alpha+D/BW_{\rm eff}$ 表示启动项与有效载荷项的简化模型。集合通信的每 rank 字节、轮次数及并发方式由算法决定，D 不能随意取整个张量大小。

一轮执行时间取决于串行依赖、各 rank 最慢路径，以及通信能否与计算重叠。不能先把所有卡的峰值相加，再忽略同步直接推断线性加速。

推理通常没有训练中的反向传播和梯度同步，却增加逐 token 依赖、请求长度差异和动态 KV；复用训练并行术语时应重新画执行路径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="ep专家并行moe"></span><span id="延伸阅读-references"></span></div>

## 后续与来源

专家派发已拆到[MoE 专家并行](moe-expert-parallelism.md)，长上下文分布见[上下文并行](context-parallelism.md)。通信事件和链路分析主要归属 [Scale-up](../../interconnect/SCALEUP/05-workloads-and-performance/parallelism-traffic.md)。

[vLLM 并行部署](https://docs.vllm.ai/en/stable/serving/parallelism_scaling/)给出跨节点 TP 与 TP/PP 组合；[Megatron 原论文](https://arxiv.org/abs/1909.08053)是经典层内切分的来源。
