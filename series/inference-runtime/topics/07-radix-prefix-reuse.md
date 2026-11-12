# 07 前缀复用:RadixAttention / Prefix Reuse

> 状态:草稿
>
> 一句话定位:把 [`06`](06-paged-kv-cache.md) 的**手动** CoW 前缀共享,升级成**自动、跨请求、带索引与淘汰**的前缀 KV 复用——用 radix tree 索引「token 序列 → KV」,最长前缀匹配命中即跳过该段 prefill。这是「**prefill 固定成本摊薄**」的机制,也是 API 层 prompt caching 的引擎底座。

## 概念 (Concept)

[`06`](06-paged-kv-cache.md) 的 CoW 共享是**被动**的:必须由上层(parallel sampling / beam search)显式建立父子关系才会共享物理 block;它**不会自动发现**"两个互不相关的请求其实带着同一段 system prompt"。

但真实负载里**前缀大量隐式共享**:

- 一个 system prompt / few-shot 例子,服务千万次请求;
- 多轮对话:第 $N$ 轮的输入 = 前 $N-1$ 轮的全部历史 + 新问;
- agent / tree-of-thought:同一公共前缀分叉出多条推理。

**RadixAttention**(SGLang)自动发现并复用这些前缀:维护一棵 radix tree 索引**所有已缓存前缀 → KV**,新请求来做**最长前缀匹配**,命中段直接复用 KV(**跳过这段的 prefill 重算**),只对未命中的 suffix 做 prefill。

> 一句话经济学:prefill 是一笔**固定成本**(把 prompt 灌进 KV)。共享前缀让这笔成本在所有用它的请求间**摊薄** → TTFT 与 prefill 算力**双降**。这正好对上你成本模型里的"固定成本摊薄"主题。

## 机制 (Mechanism)

### radix tree(压缩前缀树)

trie 的路径压缩版:**边标注 token 子串**(而非单 token),**节点对应一个被缓存的前缀**、持有指向 KV [block](glossary.md#paged-attention) 的引用(直接建在 [`06`](06-paged-kv-cache.md) 的分页 + 引用计数上)。

- **插入**:沿树走最长公共前缀,在分叉处 split 节点,挂上新 suffix 分支。
- **查询(最长前缀匹配)**:从根按 token 逐段匹配,走到不能再匹配处;这条路径上的 KV 全部可复用。

### 最长前缀匹配 → 复用

命中长度 = matched prefix tokens;该请求只需对剩下 $(s_p-\text{matched})$ 个 token 做 prefill。**复用的是 KV cache 本身**(物理 block 引用计数 +1),不是重算 → **省的是 prefill 的算力与时间,不省 decode**(decode 仍要逐 token 读全量 KV,见 [`01`](01-prefill-decode.md))。

### LRU 淘汰

KV 显存有限,树会涨满 → 按 **LRU 淘汰最久未用的叶子**前缀。两条约束:

- **引用计数感知**:正在被运行请求使用的 block 不可淘汰;
- **从叶子开始**:内部节点被子节点依赖,只能先淘汰叶。

淘汰粒度 = block([`06`](06-paged-kv-cache.md));一个前缀被淘汰 = 下次用到它要重新 prefill。**cache 容量 → 淘汰率 → 命中率**,是一条直接的因果链。

### cache-aware scheduling

SGLang 还让调度配合复用:**把共享前缀的请求排到一起 / 优先**,最大化命中、压低淘汰抖动。这把本篇与 [`08`](08-scheduling.md) 接上——调度顺序本身成了命中率的旋钮。

### 与 API 层 prompt caching 的关系

**同一个 KV 复用思想的两个层次**:

| | 引擎层 | API 层 |
|---|---|---|
| 实例 | RadixAttention、vLLM Automatic Prefix Caching (APC) | Anthropic prompt caching、OpenAI prefix caching、Gemini context caching |
| 性质 | 自动、对用户透明、跨请求 | 把同一能力**产品化**:计费、TTL、断点、隔离 |
| 用户可见 | 否(纯运行时优化) | 是:cache_control 断点、TTL、命中计费 |

API 层在引擎机制之上多了四样:**(a) 计费语义**(cache read ≈ 0.1× 输入价,cache write ≈ 1.25×/2×);**(b) 用户可控 TTL/断点**(Anthropic 5min/1hr;OpenAI 自动,最长前缀从 1024 token 起、5–10min 不活跃即清);**(c) 跨租户安全隔离**(不能跨 org 共享 KV);**(d)** 通常只缓存到显式断点的前缀。**引擎层是底层实现,API 层是暴露给用户的旋钮 + 商业模型。**

## 量化与公式 (Quantification)

新符号:$L_p$ 共享前缀长 [token];$L_s$ 各请求独有 suffix 长 [token];$R$ 共享该前缀的请求数;$h$ 前缀命中率(命中 token / 总 prompt token)。

### (1) prefill 成本摊薄

$R$ 个请求共享前缀 $L_p$、各带 suffix $L_s$:

$$\text{prefill tokens}:\quad \underbrace{R(L_p+L_s)}_{\text{无复用}} \;\longrightarrow\; \underbrace{L_p + R\,L_s}_{\text{有复用}},\qquad \text{省下 FLOP}=(R-1)\,L_p\cdot 2P$$

每请求平摊的 prefill token 从 $(L_p+L_s)$ 降到 $(L_p/R + L_s)$。$L_p\gg L_s$ 且 $R$ 大时,趋近**省掉全部前缀算力**。

### (2) TTFT 对命中的敏感(prefill compute-bound,近线性于 token)

cache-hit 请求 $\text{TTFT}\approx \text{prefill}(L_s)$ 而非 $\text{prefill}(L_p+L_s)$。

**算例**:system prompt $L_p=2000$,用户问题 $L_s=50$。命中 → prefill token $2050\to50$ → **prefill 计算/TTFT 降约 $41\times$**(忽略固定开销;prefill compute-bound,时间近线性于 token 数,见 [`01`](01-prefill-decode.md))。【估算】

### (3) KV 存储/流量去重

树形去重后,存储 KV $=$ 树中 **unique token 数** $\times\,\text{KV}_\text{tok}$,而非 $\sum_\text{req} s$。多轮对话尤甚:$N$ 轮、历史递增,朴素逐轮存历史拷贝是 $O(N^2)$ token,树形只存一条增长链 $O(N)$。

### (4) API 计费即摊薄(把 (1) 翻译成钱)

cache read = 0.1× 输入价 → 命中前缀**按 10% 计费**。Anthropic 5min 档 write=1.25×:**一次 read 即回本**($1.25 + 0.1 < 2\times1.0$,两次调用就比不缓存便宜)。这就是 (1) 的 prefill 摊薄在账单上的样子。

### (5) 实测收益(论文报告值)

SGLang RadixAttention + cache-aware scheduling:**吞吐最高 ~6.4×**(早期基准 5×)vs 前代;共享前缀越多收益越大。【论文报告值,SGLang NeurIPS'24,口径依 workload】

## 与架构建模的接口 (Modeling Interface)

- **prefill 成本从"per-request 固定 $O(s_p)$"变成"命中率 $h$ 的函数"**:
  $$\mathbb{E}[\text{prefill tokens/req}] = (1-h)\,s_p + h\,L_s$$
  $h$ 是 **workload 属性**(可从 trace 直接测),喂进 TTFT 与 prefill 算力模型。这是把"前缀复用"接进成本模型最干净的一个量。
- **正交性**:RadixAttention 砍 **prefill 侧**(算力 / TTFT),**不动 decode 侧**(带宽 / TPOT,见 [`05`](05-attention-kernels.md))。两个杠杆正交 → 高共享 workload 下,**prefill 池可按 $(1-h)$ 折算缩小**,这是 [`12`](12-pd-disaggregation.md) PD 分离时 prefill/decode 资源配比的直接输入。
- **可扫/可测参数**:命中率 $h$(workload)、KV cache 容量(→ LRU 淘汰率 → $h$)、block 大小(淘汰粒度,联动 [`06`](06-paged-kv-cache.md))。
- **KV 去重改写流量模型**:从「$\sum s$」变「unique prefix tree size」→ 影响显存占用与 [`12`](12-pd-disaggregation.md) 的 KV 传输量(命中前缀若已在 decode 节点缓存,分离时可**免传**)。
- **隔离域是命中率的硬边界**:跨租户不可共享 → 命中率必须**按隔离域内统计**,不能全局平均。架构探索若忽略这点会高估缓存收益——这是从单租户 benchmark 外推到多租户生产的常见陷阱。

## 延伸阅读 (References)

- 上游:[`06` PagedAttention](06-paged-kv-cache.md)(CoW 物理共享、引用计数、block 淘汰粒度)、[`01`](01-prefill-decode.md)(prefill compute-bound)。
- 下游:[`08` 调度](08-scheduling.md)(cache-aware scheduling)、[`12` PD 分离](12-pd-disaggregation.md)(前缀 KV 传/免传)、[`14` 框架对比](14-framework-comparison.md)(SGLang 定位)。
- 外部(已核实):
  - **SGLang / RadixAttention**:*Efficient Execution of Structured Language Model Programs*, Zheng et al., NeurIPS '24,radix tree LRU + cache-aware scheduling,≤6.4× 吞吐。[arXiv 2312.07104](https://arxiv.org/abs/2312.07104) / [LMSYS blog](https://www.lmsys.org/blog/2024-01-17-sglang/)
  - vLLM Automatic Prefix Caching(APC)文档(引擎层等价能力)。
  - **Anthropic prompt caching**(read 0.1×、write 1.25×/2×、TTL 5min/1hr):[Claude API docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching);**OpenAI prompt caching**(自动、命中省 90%、≥1024 token 前缀):[OpenAI](https://openai.com/index/api-prompt-caching/)。
