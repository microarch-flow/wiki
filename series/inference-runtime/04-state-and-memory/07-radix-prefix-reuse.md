# 前缀复用：缓存身份、查找与收益

<div class="inference-legacy-anchors" aria-hidden="true"><span id="07-前缀复用radixattention-prefix-reuse"></span></div>

上级：[本专题导读](README.md)

前缀复用保存已经计算的输入状态，使后续请求可以从匹配位置继续执行。正确性先取决于“是否是同一个计算前缀”，然后才是查找速度与命中率。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span></div>

## 缓存身份比文本相同更严格

相同可见文本不一定产生相同 token，分词器和聊天模板可能不同。相同 token 也不一定对应相同 KV，模型版本、适配器、位置处理及多模态输入可能不同。

因此缓存键需要覆盖影响状态的身份，或由隔离的缓存池保证这些条件一致。多租户服务还可能使用隔离域或盐值，限制跨请求复用范围。

以 vLLM 的分块哈希设计为例，块身份包含前序块哈希、当前 token 以及额外身份信息。哈希相等只是实现中的判定机制；碰撞处理、哈希选择和隔离仍属于系统设计。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism"></span><span id="radix-tree压缩前缀树"></span><span id="最长前缀匹配-复用"></span></div>

## 从查找到继续执行

1. 请求完成输入准备后，按其缓存身份查找最长可用前缀。
2. 固定所命中块的引用，防止执行期间被淘汰。
3. 将命中状态接入请求映射，计算剩余输入。
4. 完成后，把可复用状态加入缓存，或按策略释放。

Radix tree 通过压缩共享 token 路径组织前缀；分块哈希则按块身份索引。两者都需要管理匹配长度、引用、容量和淘汰，不能只比较数据结构名称。

完全命中的输入也可能需要重算末位置以获得 logits，具体取决于是否缓存了足够的输出状态和实现约定。统计“命中 token”时应注明是否扣除了这部分工作。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span></div>

## 两种命中率不要混用

令请求 $i$ 的输入长度为 $s_i$、按既定口径复用的位置数为 $c_i$，则 token 加权命中率为：

$$H_{\rm tok}=\frac{\sum_i c_i}{\sum_i s_i}$$

请求命中率则可定义为 $H_{\rm req}=\#\{i:c_i>0\}/N$。它回答“多少请求至少命中一些内容”，并不说明节省多少计算。

例如 2,050 个输入位置中命中 2,000 个，未命中为 50。不能把 $2000/2050$ 又作为“请求完全命中的概率”代入另一条混合成本式。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="1-prefill-成本摊薄"></span><span id="2-ttft-对命中的敏感prefill-compute-bound近线性于-token"></span><span id="3-kv-存储流量去重"></span></div>

## 容量、计算与流量分别计算

命中前缀可以减少投影和 MLP 等重复工作，也可以避免重复保存相同 KV。后缀查询仍需访问相关前缀状态，因此 Attention 成本不按未命中比例简单缩小。

Decode 仍然计算新的查询与输出。缓存对其直接作用不是跳过历史 KV 读取，但可能通过容量、批组成和硬件缓存间接改变性能。因此“只改变 TTFT，绝不影响 Decode”也过强。

衡量收益至少记录复用位置数、避免的实际计算、共享后分配块数，以及请求级延迟。不要将其中一项当作其余各项的代替。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="lru-淘汰"></span><span id="cache-aware-scheduling"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 淘汰、路由与缓存污染

LRU 是可选淘汰策略，不是前缀缓存的定义。活跃引用、复用价值和空间压力会影响可淘汰集合。大量一次性长输入可能挤走高复用前缀。

跨副本时，路由会改变命中机会；优先命中最多的副本也可能增加排队。相关决策见[副本路由](../08-serving-lifecycle/routing-and-scaling.md)。缓存命中率同时取决于工作负载顺序、容量、策略、身份隔离和路由，不能当作模型固定常数。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与-api-层-prompt-caching-的关系"></span><span id="4-api-计费即摊薄把-1-翻译成钱"></span><span id="5-实测收益论文报告值"></span><span id="延伸阅读-references"></span></div>

## API 产品与引擎机制的边界

API 的 prompt caching 还涉及保留期、计费和服务承诺。价格与 TTL 会变化，不作为本系列的机制常数。应先查引擎实际复用了什么，再查具体服务合同。

来源：[SGLang 原论文](https://arxiv.org/abs/2312.07104)、[vLLM v0.20.1 前缀缓存设计](https://docs.vllm.ai/en/v0.20.1/design/prefix_caching/)。后者是注明版本的实现例子，不用于声称两个框架采用完全相同的索引。
