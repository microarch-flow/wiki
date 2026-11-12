# 13 约束解码:grammar / FSM / JSON / Constrained Decoding

> 状态:草稿
>
> 一句话定位:强制输出符合形式结构(JSON schema、正则、CFG)。机制是**每步对 logits 打 mask、再推进一个状态机**。架构上的关键不是"语法",而是 **mask 计算是否落在 decode 热路径上、能否被 GPU 前向掩盖**——这是它和调度开销([`08`](08-scheduling.md))同类的 host 侧瓶颈问题。SGLang 的差异化点之一。

## 概念 (Concept)

约束解码 = 让输出严格符合某个形式规范:JSON schema、正则(regex)、上下文无关文法(CFG/EBNF)、有限状态机(FSM)。用于结构化输出、function/tool calling、按语法生成代码。

机制一句话:**每个 decode 步,模型出 logits 后,把"会违反约束的 token" mask 成 $-\infty$,只在允许集合里采样;然后用采到的 token 推进状态机到下一状态。** 约束由一个状态机(FSM / 下推自动机)跟踪,随每个吐出的 token 前进。

> 与 [`09`](09-speculative-decoding.md) 的关键区别:投机解码**分布无损**;约束解码**对"合法性"无损(保证输出合规),但会改变分布**(mask 后在允许集合上重归一)——它**故意**偏移模型本来的输出。约束下得太早可能损伤推理质量,这是它和纯加速手段的本质不同。

## 机制 (Mechanism)

### mask + 状态推进(热路径)

每步两件事:**(1) 由当前状态机状态算出"允许 token 掩码" $\in\{0,-\infty\}^V$ 加到 logits;(2) 采样后按所采 token 推进状态机。** 难点全在**第 (1) 步的 mask 怎么算得快**——$V$(词表)动辄 32k–256k,若每步现算就可能吃掉整个 decode 步($\sim$ms)。

### 让 mask 变便宜:从 O(V)/步 到 O(1)/步

- **朴素**:每步遍历全词表、逐 token 测是否合法 → **O(V × 语法检查)/步**,直接压垮 decode。
- **Outlines(FSM 预编译)**:把 regex/grammar **离线编译成 FSM**,并**对词表建索引**——每个 FSM 状态预存其允许 token 集。运行时只需按当前状态 **O(1) 查表** + O(V) 的 mask 应用(GPU 上廉价 elementwise)。把贵的活搬到一次性编译。
- **XGrammar(SGLang 在用)**:支持完整 CFG。把词表分**上下文无关 token**(可预检、存进 *adaptive token mask cache*)与**上下文相关 token**(用**下推自动机**运行时算,持久栈加速);并**让语法执行(CPU)与 GPU 前向重叠** → 端到端近零开销,最高 100× 于既有方案。

### tokenization 对齐(真正的硬骨头)

状态机定义在**字符/字节**上,模型却吐**子词 token**:一个 token 可能跨多个文法终结符,一个终结符可能要多个 token。所以"哪些 token 让状态机仍处合法状态"的判定必须在 **token 层**做(byte-level FSM / token healing)。这是约束解码实现里最易出错、也是各引擎差异所在的地方。

### 两笔成本(又是"固定成本摊薄")

1. **编译成本**(一次性 / 每 grammar):构 FSM / 索引,复杂语法可能要秒级 → **缓存已编译语法、跨共享同一 schema 的请求摊薄**(和 [`07`](07-radix-prefix-reuse.md) 前缀缓存同构,只是缓存对象是语法)。
2. **每步成本**:状态推进 + mask 应用,预编译后近可忽略;上下文相关部分(括号配对、递归)仍需运行时算,这是 XGrammar 区分 context-indep/dep 的原因。

## 量化与公式 (Quantification)

新符号:$V$ 词表大小;$t_\text{mask}$ 每步 mask 计算时间(host 侧);$t_\text{gpu}$ 每步 GPU decode 时间;$T_\text{compile}$ 语法编译时间;$R$ 共享同一 schema 的请求数。

### (1) 每步有效时间:mask 在不在关键路径

$$t_\text{step}^\text{eff} = \begin{cases} t_\text{gpu} + t_\text{mask} & \text{串行(mask 算完才采样)}\\[2pt] \max(t_\text{gpu},\ t_\text{mask}) & \text{重叠(mask 与 GPU 前向并行)} \end{cases}$$

- 朴素 $t_\text{mask}=O(V\cdot\text{语法检查})$ 可 $\gg t_\text{gpu}$ → decode 被 host 拖垮。
- 预编译后 $t_\text{mask}\approx$ O(1) 查表 + O(V) 应用($\sim\mu$s) $\ll t_\text{gpu}$ → 即使串行也近零;XGrammar 进一步**重叠**到 $\max(\cdot)$,彻底隐藏。
- **这与 [`08`](08-scheduling.md) 的"调度开销必须 ≪ 一个 GPU step"是同一条约束**:任何 host 侧每步任务都要么远小于 step、要么和 GPU 重叠,否则 decode 出气泡。

### (2) 编译摊薄

$$\text{每请求编译成本} = \frac{T_\text{compile}}{R}\ \xrightarrow[R\ \text{大}]{}\ 0$$

同一 JSON schema 服务大量请求时,编译近乎免费——前提是**命中已编译语法缓存**。

### (3) mask 应用本身廉价,贵的是 mask 计算

mask 应用是 $[b,V]$ 的 elementwise 加,$\sim b\,V$ 次操作,相对模型每步 $2Pb$ FLOP **可忽略**(70B:$2Pb$ vs $bV$ 差 $\sim P/V\approx 70\text{e}9/128\text{e}3\approx 5\times10^5$ 倍)。**风险从来不是 mask 应用,而是 mask 计算的 host 延迟**。

## 与架构建模的接口 (Modeling Interface)

- **约束解码 = 一条 shadow GPU decode loop 的 host 侧每步任务**:建模为 $t_\text{step}^\text{eff}=\max(t_\text{gpu}, t_\text{host\_mask})$(重叠)或加和(串行)。**这是 archax 里"非 GPU 部分会成为瓶颈"的典型案例**——若只建 GPU roofline 会完全漏掉它;要显式建一条 **host lane**(CPU 算 mask)+ CPU↔GPU 同步,重叠是其缓解手段。
- **已编译语法缓存是又一个"固定成本摊薄"对象**,与 [`07`](07-radix-prefix-reuse.md) 的 radix KV 缓存并列:都可扫"命中率 → 每请求摊薄成本"。
- **可扫参数**:词表 $V$(大词表 → mask 更大、host 成本更高)、grammar 复杂度(上下文相关比例 → 运行时算的份额)、是否重叠。
- **与投机解码([`09`](09-speculative-decoding.md))组合**:verify 的每个投机位置都要一份 mask → **mask 树**,host 成本随 $\gamma$ 涨;两者可组合但放大 host lane 压力,仿真器要把它们的 host 开销叠加。
- **质量是约束维度,不是性能维度**:约束保证合法、但偏移分布 → 若你的探索目标含输出质量,约束解码要单列一条"结构合规 vs 质量"的轴,不能并进纯性能 goodput(区别于 [`09`](09-speculative-decoding.md) 可纯当加速)。

## 延伸阅读 (References)

- 上游:[`08` 调度](08-scheduling.md)(host 每步开销 ≪ GPU step 的同款约束)、[`07` 前缀复用](07-radix-prefix-reuse.md)(语法缓存同构于 KV 缓存)、[`09` 投机解码](09-speculative-decoding.md)(无损 vs 偏移分布的对比、mask 树)。
- 下游:[`14` 框架对比](14-framework-comparison.md)(SGLang 的结构化生成定位)。
- 外部(已核实):
  - **Outlines**:*Efficient Guided Generation for LLMs*, Willard & Louf, 2023——FSM + 词表索引,每 token O(1)(对比 Guidance O(N))。[arXiv 2307.09702](https://arxiv.org/abs/2307.09702)
  - **XGrammar**:*Flexible and Efficient Structured Generation Engine*, Dong et al., 2024——context-indep/dep 分离 + adaptive token mask cache + 下推自动机 + 与 GPU 重叠,≤100×。[arXiv 2411.15100](https://arxiv.org/abs/2411.15100)
  - 相关:llguidance(Microsoft)、lm-format-enforcer、Guidance。
