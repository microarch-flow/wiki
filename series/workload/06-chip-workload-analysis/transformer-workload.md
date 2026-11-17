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
