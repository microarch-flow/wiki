# 术语表 / Glossary

> **占位状态。** 这里只放跨多篇复用的核心术语种子;每写一篇 topic,把该篇首次出现的术语补进来(见 [_conventions.md](_conventions.md) §3)。
>
> 格式:每行「中文(English, 缩写)— 一句话定义」。锚点用行内 `<a id="…">`,供各篇 `glossary.md#锚点` 链接。定义只给概念,**不放具体数字**(数字进各篇算例)。

## A–C

| 术语 | 一句话定义 |
|---|---|
| <a id="autoregressive"></a>自回归 (autoregressive) | 逐 token 生成,第 $t$ 个 token 的输入依赖前 $t-1$ 个的输出,因此 decode 天然串行。 |
| <a id="prefill"></a>预填充 (prefill) | 一次性并行处理整段 prompt、填充 KV cache 的阶段;通常 compute-bound。 |
| <a id="decode"></a>解码 (decode) | 自回归逐 token 生成阶段;每步只算 1 个新 token,通常 memory-bound。 |
| <a id="kv-cache"></a>KV 缓存 (KV cache) | 缓存历史 token 的 Key/Value 张量,避免每步重算注意力;显存占用随 Σseq_len 线性增长。 |
| <a id="compute-bound"></a>计算受限 (compute-bound) | 算术强度高于硬件 ridge point,瓶颈在算力 (FLOP/s) 而非带宽。 |
| <a id="memory-bound"></a>访存受限 (memory-bound) | 算术强度低于 ridge point,瓶颈在带宽 (byte/s),算力闲置。 |
| <a id="arithmetic-intensity"></a>算术强度 (arithmetic intensity) | FLOP 数 ÷ 访存字节数 [FLOP/byte];与硬件 ridge point 比较判定 compute/memory-bound。 |
| <a id="roofline"></a>Roofline | 以算术强度为横轴、可达性能为纵轴的上界模型;拐点 (ridge point) $= C/BW$。 |
| <a id="chunked-prefill"></a>分块预填充 (chunked prefill) | 把长 prompt 的 prefill 切成多个 chunk,与 decode 步交错调度,平滑算力占用。 |
| <a id="continuous-batching"></a>连续批处理 (continuous batching) | 以 iteration 为粒度动态增删 batch 内请求,完成即出、空位即补,消除静态批尾部浪费。 |

## D–K

| 术语 | 一句话定义 |
|---|---|
| <a id="gqa"></a>分组查询注意力 (Grouped-Query Attention, GQA) | 多个 query 头共享一组 KV 头,把 KV cache 字节数按 $h_{kv}/h$ 缩小;MQA 是 $h_{kv}=1$ 的极端。 |
| <a id="mqa"></a>多查询注意力 (Multi-Query Attention, MQA) | 所有 query 头共享单一 KV 头($h_{kv}=1$)。 |
| <a id="hbm"></a>高带宽显存 (High Bandwidth Memory, HBM) | GPU 片上堆叠显存;decode 阶段权重+KV 的读取带宽常是吞吐上界。 |
| <a id="flash-attention"></a>FlashAttention | IO-aware 精确注意力:tiling + online softmax,不在 HBM 物化 $O(s^2)$ 的 $QK^\top$;prefill 主力 kernel。 |
| <a id="flash-decoding"></a>FlashDecoding(split-KV) | 在 batch×head 之外再沿 KV 序列维切分并行、最后 reduction 合并;救低 batch/长 context 的 decode 占用率。 |
| <a id="online-softmax"></a>在线 softmax (online softmax) | 增量遍历 KV 块时维护 running max/sum,按指数差 rescale 部分输出,免物化整行;FlashAttention/Decoding 的数值核心。 |
| <a id="internal-fragmentation"></a>内部碎片 (internal fragmentation) | 已分配给某请求、但未被实际 token 用到的 KV 空间(如按 $s_\max$ 预留却只用一小段)。 |
| <a id="external-fragmentation"></a>外部碎片 (external fragmentation) | 变长连续块分配/释放后,显存里留下的、装不下新请求的空闲"洞"。 |
| <a id="head-of-line-blocking"></a>队头阻塞 (head-of-line blocking) | 新请求被前面未排空的批/队列挡住,无法及时进入服务,推高 TTFT。 |
| <a id="static-batching"></a>静态批处理 (static batching) | 凑齐一批一起跑到全部完成才换批;长度异质时尾部空转,被 continuous batching 取代。 |
| <a id="paged-attention"></a>分页注意力 (PagedAttention) | 把 KV cache 切成固定大小 block、用 block table 间接寻址,消除显存碎片、支持前缀共享 (CoW)。 |
| <a id="block-table"></a>块表 (block table) | 每个请求一张「逻辑 block → 物理 block」映射表,是 PagedAttention 的间接寻址结构;跨层共享。 |
| <a id="cow"></a>写时复制 (Copy-on-Write, CoW) | 多序列共享前缀 block(引用计数),某序列要写入分叉时只复制那一个 block;前缀共享的物理机制。 |

## L–R

| 术语 | 一句话定义 |
|---|---|
| <a id="ragged-layout"></a>不规则布局 (ragged / packed / varlen layout) | 把变长序列首尾相接拍平成一维(总长 $\sum s_i$)、用 cu_seqlens 记边界,免 padding。 |
| <a id="padding"></a>填充 (padding) | 把变长序列补到 batch 内最长以凑矩形张量;pad 位仍耗算力/显存,被 ragged 布局取代。 |
| <a id="selective-batching"></a>选择性批处理 (selective batching) | Orca 提出:对可批的大 GEMM(投影/FFN)整批算、对依赖 KV 长度的 attention 逐序列拆算。 |
| <a id="iteration-level-scheduling"></a>迭代级调度 (iteration-level scheduling) | 以单次 forward 为粒度调度:每步踢掉已完成、补入新请求;是 continuous batching 的机制。 |
| <a id="stall-free-scheduling"></a>无停顿调度 (stall-free scheduling) | Sarathi-Serve:新请求的 prefill chunk 拼入运行中 batch 而不暂停在跑的 decode。 |
| <a id="radix-attention"></a>基数注意力 (RadixAttention) | 用 radix tree 索引已缓存的 KV 前缀,做最长前缀匹配复用 + LRU 淘汰。 |
| <a id="tp"></a>张量并行 (Tensor Parallelism, TP) | 把单层权重按维度切到多卡,每步需 all-reduce;降低单卡权重/激活占用,增加通信。 |
| <a id="pp"></a>流水线并行 (Pipeline Parallelism, PP) | 按层切分到多卡,micro-batch 流水;省显存但有 bubble。 |
| <a id="ep"></a>专家并行 (Expert Parallelism, EP) | MoE 场景把不同专家放到不同卡,按路由 all-to-all 分发 token。 |
| <a id="dp"></a>数据并行 (Data Parallelism, DP) | 整模型多副本,各处理不同请求;扩吞吐,不降单请求延迟、不省单卡显存。 |
| <a id="moe"></a>混合专家 (Mixture of Experts, MoE) | 每层多个专家,每 token 路由 top-$k$;总参数大但每 token 仅激活 $k/E$,配 EP 部署。 |
| <a id="all-reduce"></a>all-reduce | 跨卡规约+广播(TP 每层 2 次,同步、在关键路径);需高带宽互连(NVLink)。 |
| <a id="all-to-all"></a>all-to-all | 每卡向所有卡分发/收集不同分片;MoE EP 的 token 派发/合并(每 MoE 层 2 次)。 |
| <a id="pipeline-bubble"></a>流水线气泡 (pipeline bubble) | PP 中 stage 等待上游的空闲;占比 $\frac{N_{pp}-1}{m+N_{pp}-1}$,decode 因 micro-batch 难做大而气泡大。 |
| <a id="pd-disaggregation"></a>PD 分离 (Prefill-Decode Disaggregation) | 把 prefill 与 decode 放到不同节点/池,各自独立扩缩,KV 经链路传输。 |
| <a id="kv-transfer"></a>KV 传输 (KV transfer) | PD 分离中把 prefill 算出的 KV 过链路传给 decode 池;layer-wise 流式 + 前缀复用免传隐藏开销。 |
| <a id="tiered-kv"></a>分层 KV / KV offload | KV 在 HBM→DRAM→SSD/NVMe 多级存储;热的留 HBM、冷的下沉,按链路档与复用率决定放哪层。 |

## S–Z

| 术语 | 一句话定义 |
|---|---|
| <a id="prompt-caching"></a>提示缓存 (prompt caching) | API 层把前缀 KV 复用产品化:cache read ≈0.1× 输入价、write ≈1.25×/2×、带 TTL 与跨租户隔离;引擎侧对应 RadixAttention / APC。 |
| <a id="apc"></a>自动前缀缓存 (Automatic Prefix Caching, APC) | vLLM 中按前缀自动复用已缓存 KV 的功能,与 RadixAttention 同类。 |
| <a id="speculative-decoding"></a>投机解码 (speculative decoding) | 用小 draft 模型猜多个 token,大模型一次并行 verify,rejection sampling 保证分布无损。 |
| <a id="acceptance-rate"></a>接受率 (acceptance rate, $\alpha$) | draft 提议 token 被 target 接受的概率;决定投机加速比上界 $1/(1-\alpha)$,由模型×workload 决定、需实测。 |
| <a id="rejection-sampling"></a>拒绝采样 (rejection sampling) | 以 $\min(1,p/q)$ 接受 draft、否则从残差分布 $\propto\max(0,p-q)$ 重采;保证产出精确服从 target 分布 $p$。 |
| <a id="tree-attention"></a>树注意力 (tree attention) | 在一棵候选 token 树上用不规则 mask 一次并行验证多条续写;Medusa/EAGLE/SpecInfer 的验证机制。 |
| <a id="admission-watermark"></a>准入水位 (admission watermark) | 准入新请求时为 KV 增长保留的 block 缓冲比 $w$;防 iteration 中途 OOM 与抖动。 |
| <a id="preemption"></a>抢占 (preemption) | 显存不够时把运行中请求踢回等待;恢复有 recompute(重跑 prefill)与 swap(KV 出/回 CPU)两种。 |
| <a id="thrashing"></a>抖动 (thrashing) | 准入过激导致 preempt↔resume churn、有用产出塌方;同 OS 换页抖动。 |
| <a id="weight-only-quant"></a>权重量化 (weight-only, W4A16) | 仅压权重(常 INT4)、激活仍 FP16,在线 dequant;代表 AWQ/GPTQ。压 $P p_w$,利低 batch decode 与装卡,不提算力。 |
| <a id="w8a8"></a>W8A8 / FP8 量化 | 权重+激活都低精(INT8/FP8),启用低精 tensor core 提算力;代表 SmoothQuant、Hopper FP8(E4M3/E5M2)。 |
| <a id="awq"></a>AWQ | Activation-aware Weight Quantization:用激活幅度找 ~1% salient 权重通道并 per-channel 保护,W4 近无损。 |
| <a id="gptq"></a>GPTQ | 基于 Hessian/OBQ 二阶误差补偿的逐层权重量化(W4/W3)。 |
| <a id="kv-quant"></a>KV 量化 (KV quantization) | 压 KV cache($\text{KV}_\text{tok}\propto p_{kv}$),FP8 常近无损;利并发与长上下文 decode 带宽。 |
| <a id="outlier-channel"></a>离群通道 (outlier channel) | 激活中少数幅值极大的维度,使激活量化困难;weight-only 易、W8A8 需 SmoothQuant 类处理。 |
| <a id="cu-seqlens"></a>cu_seqlens | 变长 batch 的累积序列长度前缀和数组,配合 ragged/packed 布局免 padding。 |
| <a id="constrained-decoding"></a>约束解码 (constrained decoding) | 每步对 logits 打 mask 强制输出符合 regex/CFG/JSON;保证合法但偏移分布(区别于投机的无损)。 |
| <a id="token-mask"></a>token 掩码 (token mask / logit mask) | 把违反约束的 token logit 置 $-\infty$ 的向量;预编译 FSM 使其计算降到 O(1)/步。 |
| <a id="fsm"></a>有限状态机 (Finite-State Machine, FSM) | 约束解码跟踪合法续写的状态机;Outlines 将 regex/CFG 编译为 FSM 并对词表建索引。 |
| <a id="ttft"></a>首 token 时延 (Time To First Token, TTFT) | 请求到达到吐出第一个 token 的时间;主要由 prefill 决定。 |
| <a id="itl"></a>token 间时延 (Inter-Token Latency, ITL) | decode 阶段相邻输出 token 的**实际间隔**,是一个分布(含 jitter);SLO 关心其尾部 p99。本 wiki 约定 ITL=分布、TPOT=其均值(见 [`02`](topics/02-metrics-slo.md))。 |
| <a id="tpot"></a>每输出 token 时间 (Time Per Output Token, TPOT) | 首 token 之后的**平均**每 token 时间 $=(\text{E2E}-\text{TTFT})/(N_\text{out}-1)$,一个标量;由 decode 带宽决定。 |
| <a id="e2e"></a>端到端时延 (End-to-End latency, E2E) | 请求到达到最后一个 token $=\text{TTFT}+(N_\text{out}-1)\cdot\text{TPOT}$。 |
| <a id="mbu"></a>模型带宽利用率 (Model Bandwidth Utilization, MBU) | decode 实测等效 HBM 带宽 ÷ 峰值带宽;memory-bound 阶段的效率上界指标。 |
| <a id="mfu"></a>模型算力利用率 (Model FLOPs Utilization, MFU) | prefill/训练实测 FLOP/s ÷ 峰值算力;compute-bound 阶段的效率指标。 |
| <a id="throughput"></a>吞吐 (throughput) | 单位时间产出 token 数 (token/s),系统级或单请求级。 |
| <a id="goodput"></a>有效吞吐 (goodput) | 仅计满足 SLA(TTFT/ITL 约束)的请求贡献的吞吐。 |
| <a id="vllm"></a>vLLM | 以 PagedAttention 为核心抽象的通用高吞吐推理服务器(Berkeley);重心在 block 内存管理。 |
| <a id="sglang"></a>SGLang | 以 RadixAttention + 结构化前端 DSL 为核心的推理框架(LMSYS);重心在程序结构感知与前缀复用。 |
| <a id="xgrammar"></a>XGrammar | 高效结构化生成引擎(SGLang 集成):上下文无关/相关 token 分离 + mask 缓存 + 与 GPU 重叠。 |

---

**待补**:随各篇推进补充——FlashAttention、FlashDecoding、prompt caching、recompute/swap 抢占、algorithm intensity 的 decode 推导、量化 (FP8/INT8/AWQ/GPTQ) 等。
