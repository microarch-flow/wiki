# Transformer 工作负载：prefill、decode 与 KV 容量

上级：[专题导读](README.md)

<span id="transformer-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么必须先把-transformer-拆成两个阶段" class="workload-legacy-anchor"></span>
<span id="分阶段的逐算子画像" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


Transformer 是结构；prefill 和 decode 是自回归执行阶段。ViT、双向 encoder 或一次性轨迹预测不应自动套入语言生成的两阶段模型。算子机制见 [Attention 与 Transformer](../01-foundation-model-components/attention-and-transformer.md)。

## 阶段改变了矩阵形状

Prefill 处理已知提示中的多个位置，可沿 token 轴形成较大的矩阵乘。Decode 每次追加新位置，单请求通常只有少量新 query，但要读取其允许访问的历史 K/V。batch 增大可提高权重复用，同时增加状态和排队需求。

训练还包括反向传播与激活保存；推理只有前向并不意味着完全没有持久状态。

## 同一层的两次前向

构造一个 decoder 层，batch 为 1，隐藏宽度 64，4 个 query 头、2 个 KV 头，每头 16 维。FFN 用两个线性层 $64\to128\to64$。权重和 KV 均为 FP16。先 prefill 四个提示 token，再将已选出的第五个 token 送入同一层做一次 decode。只统计投影、FFN 和注意力的两次矩阵乘，忽略偏置、归一化、位置处理、softmax、激活及词表头。

Q 与输出投影各有 $64\times64$ 个权重，K 与 V 投影各有 $64\times32$ 个。FFN 有 $2\times64\times128$ 个权重。合计 28,672 个，每处理一个新位置就是 57,344 FLOP。按 1 MAC = 2 FLOP 计，一对有效 query-key 位置跨 4 个 query 头的点积和加权求和共 $4\times4\times16=256$ FLOP。

| 一层、单请求 | 四位置 prefill | 下一位置 decode |
| --- | ---: | ---: |
| 新输入矩阵 | $[4,64]$ | $[1,64]$ |
| 有效因果位置对 | $1+2+3+4=10$ | 5（含当前） |
| 投影与 FFN | 229,376 FLOP | 57,344 FLOP |
| 注意力有效矩阵乘 | 2,560 FLOP | 1,280 FLOP |
| 以上合计 | **231,936 FLOP** | **58,624 FLOP** |
| 读取已有 KV / 追加新 KV | 0 / 512 B | 512 B / 128 B |

每位置追加的 K 与 V 共 $2\times2\times16\times2=128$ B。表中流量针对持久 KV 缓冲区，假设当前 K/V 在运算中直接复用，历史各读一次，所有新项各写一次。第五个 token 完成后 KV 共 640 B。若该层权重在每次调用时都从观察边界外取一次，两列还各需读 **56 KiB** 权重。四个提示位置可以共享这一次读取。

上表计有效因果位置对。若内核先做完整 $4\times4$ 的两次乘法再屏蔽上三角，注意力部分实际执行 4,096 FLOP。分块、KV 头复用与缓存命中都可能改变跨内存边界的字节数。此处的手算给出了核对执行图的基准。

## 权重流量与 KV 流量分开

构造单 token 线性层，权重每个元素参与一次乘加。若每个 FP16 权重从选定边界读取一次，忽略其他流量，则强度约为 $2\ \mathrm{FLOP}/2\ \mathrm B=1\ \mathrm{FLOP/B}$。batch 为 $B$ 且权重可共享时，理想强度可随 $B$ 增加，但真实系统还包含激活和状态流量。

这解释了一种小 batch 权重带宽压力，不等于所有 decode 都由 KV cache 主导。短上下文可能以权重读取为主，长上下文可能显著增加 KV 读取；多请求、量化和分片会改变比例。

<span id="kv-cache同时压垮容量和带宽的状态" class="workload-legacy-anchor"></span>

## KV 容量的明确例子

对标准分头缓存，容量为：

$$
C_{KV}=2LBT h_{kv}d_hs
$$

$L$ 为层数，$T$ 为每条序列长度，$s$ 为每元素字节数。构造 $L=32,B=1,T=4096,h_{kv}=8,d_h=128,s=2$，得到 512 MiB；若 KV 头为 32，则为 2 GiB。分页碎片和量化元数据另计。

这个公式不适用于所有压缩 KV 或混合架构。SSM 层和 attention 层应分别计量，见 [SSM 工作负载](ssm-workload.md)。

## 算法结构与内核实现分开

FlashAttention 可避免完整分数矩阵写入 HBM；GQA 减少 KV 头；分页管理改善缓存分配。三者处理不同问题，收益不能简单相乘。

显式 attention 分数容量也不等于实际峰值内存。norm、布局变换、采样和内核启动虽 FLOPs 较小，仍可能出现在关键路径中。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 测量与跨专题边界

记录输入长度、输出长度、batch/并发、权重和 KV 精度、设备、内核及缓存策略。服务指标还要区分首 token 延迟、后续 token 间隔与总请求时间。

本页负责模型工作量和存储规模；调度、前缀复用和服务 SLO 的主要入口是[推理与运行时](../../inference-runtime/README.md)。Pope 等论文的测量来自其 TPU 配置，不能直接作为所有 GPU/NPU 的固定瓶颈结论。

## 来源与延伸

- [Efficiently Scaling Transformer Inference](https://arxiv.org/abs/2211.05102)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [GQA](https://aclanthology.org/2023.emnlp-main.298/)
