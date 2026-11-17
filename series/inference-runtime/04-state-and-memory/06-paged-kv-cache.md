# 分页 KV：分配、寻址、共享与释放

<div class="inference-legacy-anchors" aria-hidden="true"><span id="06-kv-cache-管理pagedattention-paged-kv-cache"></span></div>

上级：[本专题导读](README.md)

分页 KV 将序列的逻辑位置映射到固定大小的缓存块，使请求不必预留一整段最大长度空间。它解决分配与寻址问题；连续批处理和前缀复用还需要各自的调度与身份规则。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="分页-paging"></span><span id="block-table-寻址地址翻译"></span></div>

## 从逻辑位置找到缓存块

设一个块容纳 $b_{\rm blk}$ 个 token。位置 $j$ 对应逻辑块号 $\lfloor j/b_{\rm blk}\rfloor$，块内偏移为 $j\bmod b_{\rm blk}$。请求的块表再将逻辑块号映射到池中的块标识。

构造例子：$b_{\rm blk}=4$，请求有 10 个已缓存位置，块表为 `[7,2,11]`。位置 9 对应逻辑块 2、池块 11、块内偏移 1。三个池块无需相邻。

这里的“物理块”指软件缓存池中的分配单元，不等于硬件虚拟内存的物理页。内核可以直接按块表访问，或者采用其他地址转换设计。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism"></span></div>

## 分配与释放的执行过程

1. 请求进入或增长时，管理器计算新增状态需要多少块。
2. 从对应空闲池取得块，更新映射；失败时由调度器等待、抢占或拒绝。
3. 执行器把块表和长度交给 Attention 内核。
4. 请求结束后解除引用；最后一次设备访问完成且引用为零时，块才能回到空闲池。

核心不变量是：有效逻辑位置只能读取属于该请求语义的状态；仍被任何请求或在途操作引用的块不能被覆盖。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="按层分桶-per-layer-bucketing"></span></div>

## 不同层怎样组织池

同类全注意力层可以共享逻辑块分配结构，同时在各层的存储区保存对应 K/V。这样的实现可减少元数据。

但“所有层永远共用一张块表”不是通用要求。混合模型的层类型、窗口、状态尺寸和生命周期可能不同，应按缓存组或池分别管理。池间剩余空间也未必可以即时互换。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="cow-前缀共享-copy-on-write"></span></div>

## 前缀共享与写时复制

若两个请求具有相同的缓存身份和已计算前缀，可以让块表引用相同块，并维护引用计数。对不可变的完整块，读取共享是直接的。

若两个分支共享一个尚未写满的块，而其中一个要追加不同内容，必须先获得私有可写存储；写时复制是一种实现。也有系统只缓存完整块，以减少此类情况。

共享容量不等于共享一次 Attention 计算。不同请求的查询向量通常不同；实际 HBM 读流量还受内核和缓存影响。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-eta_textmem从预留到分页"></span><span id="2-块大小-b_textblk-的权衡cross-cutting-旋钮"></span><span id="3-block-table-开销可忽略"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 块大小的量化取舍

单请求长度为 $s$ 时，分配位置数为：

$$n_{\rm alloc}=b_{\rm blk}\left\lceil s/b_{\rm blk}\right\rceil$$

若没有共享，其末块空置为 $n_{\rm alloc}-s$，范围是 0 到 $b_{\rm blk}-1$。例如 $s=1500,b_{\rm blk}=16$，分配 1504 个位置，载荷占比为 $1500/1504\approx99.73\%$。

小块减少尾部空置和复制粒度，但增加映射、管理及部分内核开销；大块反之。元数据应按请求数、块数、表项宽度和缓存组数计算，不能无条件称为可忽略。

固定块池减少了池内变长连续分配造成的外部碎片，但没有消除所有显存浪费。工作区、池间不均衡和块尾部仍须计入。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="延伸阅读-references"></span></div>

## 分页不是唯一实现路线

[PagedAttention 原论文](https://arxiv.org/abs/2309.06180)展示软件块管理与内核寻址；[vAttention](https://arxiv.org/abs/2405.04437)利用虚拟内存管理保持连续虚拟地址。这说明动态分配与连续批处理不必绑定某一种 Attention 接口。

继续阅读[前缀复用](07-radix-prefix-reuse.md)和[请求调度](../05-batching-and-scheduling/08-scheduling.md)。混合层布局可查阅[vLLM 混合 KV 设计](https://docs.vllm.ai/en/stable/design/hybrid_kv_cache_manager/)。
