# 06 KV cache 管理:PagedAttention / Paged KV Cache

> 状态:草稿
>
> 一句话定位:把 OS 虚存分页搬到 KV 上——逻辑连续、物理分页、中间隔一层 block table 做地址翻译。它把 [`03`](03-naive-bottlenecks.md) 的 $\eta_\text{mem}$ 从 ~0.18 推到 ~0.99,既是 [`04`](04-dynamic-shape-batching.md) continuous batching「随时插入新请求」的物理前提,也是 [`07`](07-radix-prefix-reuse.md) 前缀复用的底座。

## 概念 (Concept)

回顾 [`03`](03-naive-bottlenecks.md) 瓶颈 1:朴素按 $s_\max$ **连续预留** KV → 内部碎片(预留未用)+ 外部碎片(变长块留洞)+ 过度预留,$\eta_\text{mem}\approx0.18$。这与 1960 年代 OS 面对的内存碎片**同构**,当年的答案是**虚拟内存分页**。PagedAttention 就是把 KV 当成「按需分页的虚拟地址空间」来管:

> **逻辑连续 ≠ 物理连续。** 每条序列的 KV 在逻辑上是连续 token 流(token 0,1,2,…),物理上散落在一个全局 block 池里;中间隔一层 [block table](../glossary.md#block-table) 做地址翻译。这层间接换来:按需分配(不预留)、外部碎片归零、跨序列共享。

## 机制 (Mechanism)

### 分页 (paging)

KV 切成**定长 block**,每 block 存固定 $B_\text{blk}$ 个 token 的 $K,V$(vLLM 默认 $B_\text{blk}=16$),系统维护一个**全局 free block 池**。序列每多 $B_\text{blk}$ 个 token 才申请一个新 block,**不按 $s_\max$ 预留**。唯一残留的碎片:每条序列**最后一个未满 block** 内 $\le B_\text{blk}-1$ 个 token 的内部碎片——相对动辄上千的 $s_\text{actual}$ 可忽略。

### block table 寻址(地址翻译)

每条序列一张 **block table**:逻辑 block 号 → 物理 block 号。第 $t$ 个 token 落在逻辑 block $\lfloor t/B_\text{blk}\rfloor$ 的第 $t \bmod B_\text{blk}$ 个 slot。decode 时 paged attention kernel([`05`](05-attention-kernels.md))按这张表 **gather** 散落的物理 block 进 SRAM 再算。**这就是一层页表式间接:block table ≈ 页表,$B_\text{blk}$ ≈ page size,gather ≈ 查页表后取数。**

### 按层分桶 (per-layer bucketing)

> `TODO(确认)`:这是我对你列的「按层分桶」的理解,若你指别的请纠正。

物理 KV 池**按层组织**:每个 transformer 层各有自己的 key/value cache 张量(形如 `[num_blocks, …]`)。关键点是——**一个物理 block 号在全部 $L$ 层里指向相同 offset**,所以 **block table 与层无关:一张表服务全部 $L$ 层**,大小是 $O(\text{blocks})$ 而非 $O(\text{blocks}\cdot L)$;一次分配/释放/CoW 操作就覆盖某序列在所有层的那一块 KV。
> (实现细节:vLLM 的 key cache 为向量化访存用了 `[num_blocks, num_kv_heads, head_size/x, block_size, x]` 这类 layout;不影响上面的逻辑模型,`TODO` 若 `15` 要精确建模再展开。)

### CoW 前缀共享 (copy-on-write)

多条序列**共享前缀**时(同一 system prompt、parallel sampling、beam search 的公共祖先),它们的 block table 指向**同一批物理 block**,用**引用计数**管理。当某条序列要在共享 block 上**写入/分叉**,只**复制那一个 block**(CoW),改自己的副本、原 block 引用计数减一——**不复制整段前缀,只复制要动的那一块**。共享前缀因此只存一份。这正是 [`07`](07-radix-prefix-reuse.md) RadixAttention 的物理基础(它在 CoW 共享之上再加一层「自动前缀索引」)。

## 量化与公式 (Quantification)

新符号:$B_\text{blk}$ 块大小 [token];$M_\text{KV}$ 留给 KV 的显存 [byte]。其余沿用 [`01`](01-prefill-decode.md)/[`03`](03-naive-bottlenecks.md)。

### (1) $\eta_\text{mem}$:从预留到分页

$$\eta_\text{mem}^\text{paged} = \frac{s_\text{actual}}{\lceil s_\text{actual}/B_\text{blk}\rceil\cdot B_\text{blk}} \;\ge\; 1-\frac{B_\text{blk}}{s_\text{actual}}$$

**算例**:$B_\text{blk}=16$、$s_\text{actual}=1500$ → $\eta_\text{mem}\ge 1-16/1500\approx 98.9\%$,对比 [`03`](03-naive-bottlenecks.md) 的朴素 18% → **可并发数提升约 $0.99/0.18\approx 5.5\times$**。论文口径:既有系统 KV 仅约 **20.4–38.2% 有效(即浪费 60–80%)**,vLLM 近零浪费 → **2–4× 吞吐** vs FasterTransformer / Orca【论文报告值,PagedAttention SOSP'23,Fig.2 为浪费分解,abstract 为 2–4×/near-zero】。

### (2) 块大小 $B_\text{blk}$ 的权衡(cross-cutting 旋钮)

| $B_\text{blk}$ | 内部碎片 | gather 连续性 / 有效带宽([`05`](05-attention-kernels.md)) | block table 项数 | 分配频率 |
|---|---|---|---|---|
| 大 | ↑(最后块浪费多) | ↑ 更连续、DMA 友好 | ↓ | ↓ |
| 小 | ↓ | ↓ 指针追逐多 | ↑ | ↑ |

每序列内部碎片期望 $\approx B_\text{blk}/2$ token → 总浪费 $\approx b\cdot \tfrac{B_\text{blk}}{2}\cdot\text{KV}_\text{tok}$。**$B_\text{blk}$ 同时影响显存利用率(本篇)与 decode kernel 的 MBU([`05`](05-attention-kernels.md))——必须联合扫,不能各扫各的。**

### (3) block table 开销可忽略

每序列 block table 项数 $=\lceil s/B_\text{blk}\rceil$。$s=8\text{k},B_\text{blk}=16$ → 512 项 × 几字节 $\approx 2$ KB,且跨层共享不乘 $L$;相对该序列 KV 本身(Llama-3 70B:$320\text{ KiB/tok}\times8\text{k}=2.5$ GiB)**完全可忽略**。间接寻址的真实成本不在这张表的存储,而在 kernel gather 的**访存不连续**(→ [`05`](05-attention-kernels.md) MBU 折扣)。

## 与架构建模的接口 (Modeling Interface)

- **直接替换 `03` 的效率乘子**:把 $\eta_\text{mem}\!\approx\!0.99$ 代入并发上限 $\text{max\_concurrency}=\dfrac{M_\text{KV}\cdot\eta_\text{mem}}{\mathbb{E}[s_\text{actual}]\cdot\text{KV}_\text{tok}}$(→ [`08`](08-scheduling.md) 准入水位、[`15`](15-quantitative-estimation.md) 算例)。
- **$B_\text{blk}$ 是一个 cross-cutting 设计参数**:它同时落在「显存利用率」与「decode kernel 有效带宽(MBU)」两条线上,仿真器要**二维联合扫** $B_\text{blk}\times$(占用率),才能找到 goodput 最优点——这正是单独看任一层会漏掉的耦合。
- **block table = 地址翻译层**:对 archax,KV 访问可建成「一层间接(block table lookup,可建命中率/局部性)+ gather 不连续(有效带宽折扣)」,与你已熟的 TLB/页表/虚存模型同构,硬件侧类比直接套用。
- **CoW 把 KV 流量模型从「$\sum$ per-request $s$」改成「去重后的 unique KV + 共享读」**:共享前缀只存一份、只读一份摊给多序列。这把本篇与 [`07`](07-radix-prefix-reuse.md)(自动前缀复用)、[`12`](12-pd-disaggregation.md)(分离时共享前缀的 KV 传不传)接上——是 KV 流量/带宽建模里一个能大幅改写数字的因子。
- **"分页放在哪一层"是个体系结构选择**:vAttention(arXiv 2405.04437)改用 CUDA 底层虚拟内存(VMM API)做 demand paging,保持 KV **虚拟连续、物理分页**,从而**不必改写 attention kernel**。对 archax 有借鉴——地址翻译放在 **kernel 层(PagedAttention)还是驱动/硬件层(vAttention)** 是可比较的设计点。【作量级/方向参照】

## 延伸阅读 (References)

- 上游:[`03` 朴素瓶颈](03-naive-bottlenecks.md)($\eta_\text{mem}$ 碎片)、[`04`](04-dynamic-shape-batching.md)(continuous batching 需非连续 KV)、[`05`](05-attention-kernels.md)(paged kernel gather、$B_\text{blk}$ 与 MBU)。
- 下游:[`07` RadixAttention](07-radix-prefix-reuse.md)(在 CoW 上加自动前缀索引)、[`08` 调度](08-scheduling.md)(按 block 的准入/抢占)、[`12` PD 分离](12-pd-disaggregation.md)(KV offload/传输)。
- 外部(已核实):
  - **PagedAttention / vLLM**:*Efficient Memory Management for LLM Serving with PagedAttention*, Kwon et al., SOSP '23。[arXiv 2309.06180](https://arxiv.org/abs/2309.06180) —— 2–4× 吞吐、近零浪费、block_size 16、引用计数 + CoW。
  - vLLM Paged Attention 设计文档(物理 layout 细节)。[vLLM docs: paged_attention](https://docs.vllm.ai/en/stable/design/paged_attention/)
  - **vAttention**:*Dynamic Memory Management for Serving LLMs without PagedAttention*, 2024。[arXiv 2405.04437](https://arxiv.org/pdf/2405.04437) —— 用 CUDA VMM 做物理分页、免改 kernel,作"分页放哪层"的对比。
