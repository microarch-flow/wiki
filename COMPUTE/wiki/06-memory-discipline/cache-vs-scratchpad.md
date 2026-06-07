# Cache vs Scratchpad:确定性延迟的设计分歧

上级:[06 · 存储 discipline](./README.md)
相关:[算力单元要解决什么问题](../01-overview/problem-statement.md)、[FPGA vs ASIC](../05-fpga-vs-asic/lut-mux-and-10x-overhead.md)、[CPU vs GPU 核面积](../07-chip-organization/cpu-vs-gpu-core-area.md)
强链接:[`RAM/.../scratchpad-vs-cache`](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md)、[`RAM/.../data-movement-first-principle`](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md)
主线:[计算 / 通信比](../01-overview/compute-communication-ratio.md)——本篇:把分母从运行时随机变成编译期确定。

---

## 这页在回答什么问题

CPU 跑同一段代码,两次耗时可能不同;TPU/Groq 却能给出确定性延迟。差别的核心在一个设计选择:**让硬件偷偷决定数据从哪来(cache),还是让软件显式决定(scratchpad)。** 本篇从算力单元的视角讲这个分歧——RAM 域从存储器件视角讲同一块 SRAM,这里讲"为什么算力单元想要确定性"。

> **本篇是 COMPUTE↔RAM 的接口篇,刻意不重写 RAM 的器件分析。** scratchpad/cache 作为 SRAM 形态的器件差异、面积效率、bank 组织,见 [`RAM/.../scratchpad-vs-cache`](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md);本篇只讲"确定性语义对算力单元和建模意味着什么"。

---

## 1. CPU 非确定性延迟的最大来源:cache

CPU 在 die 上放一块 cache,挡在核和 DDR 之间:

```
CPU die ──[cache]── DDR        每次访存先查 cache,命中则快约两个数量级
```

- **因为** cache 比 DDR 快约**两个数量级**,没有 cache 几乎所有程序慢 ~100×——cache 对 CPU 跑出合理速度是**绝对必要**的。
- **但** 命中与否取决于运行时环境:其他程序占用了 cache、最近访问历史、cache 替换策略里的(伪)随机数。**所以** cache 是 CPU 运行时间**非确定性的最大来源**:同一段代码,这次数据在 cache(快),下次被别的程序挤掉了(慢),你无法静态预测。

这对通用计算是可接受的代价(换来了对任意访问模式的自动适应),但对需要确定性延迟的场景(实时、加速器流水)是个问题。

---

## 2. Scratchpad:把数据放置决策搬到软件

TPU / Groq 的不同哲学:**不让硬件偷偷决定数据从 cache 还是 DDR 来,而是做成两条不同的指令。**

```
TPU die ──[scratchpad]── HBM
          ↑ 一种指令:读 scratchpad(片上,快,确定)
                          ↑ 另一种指令:读 HBM(片外,慢,但也确定)
                          软件显式选择走哪条
```

**因为** 数据来源由软件指令**显式指定**——读 scratchpad 是一条 opcode、读 HBM 是另一条 opcode,没有硬件层面的"猜命中";**所以** 获得**确定性延迟**:每条访存指令的耗时在编译期就能算出来,不依赖运行时环境。

代价是把局部性管理的责任交给了软件:编译器/程序员必须显式安排"什么数据什么时候搬进 scratchpad、什么时候可以覆盖"——这正是 [RAM 域那篇](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md) 详述的"谁管理局部性"分水岭。

---

## 3. 一个反直觉的事实:确定性是更简单的起点

⚠️ 常见误解:以为"确定性延迟"是 TPU/Groq 费力加上去的高级特性。**恰恰相反——确定性是更简单的起点,非确定性是 CPU 后来主动加进去的。**

- 一块裸 SRAM + 显式访存,天然就是确定性的。
- 是 CPU 为了对任意程序自动优化局部性,**主动加入 cache(及其替换、预取、coherence)** 这些机制,才把确定性弄成了非确定性。
- 完全可以做确定性 CPU,但市场不青睐(通用代码享受不到 cache 的自动加速),所以没人做了。

**真实硬件锚点**:Groq 公开宣传过确定性延迟(全静态调度、编译器决定每个数据何时在哪);TPU 核内也用 scratchpad。所以"Groq 全静态、编译器决定数据放置"不是噱头,而是**回到了确定性这个更简单的起点**,并把它做到极致。

> 这和 [FPGA 的确定性低延迟卖点](../05-fpga-vs-asic/lut-mux-and-10x-overhead.md#1-商业账先行-10k-vs-3000-万) 同源:都是"放弃自动优化、换可预测性"。AI workload 访问模式静态可知,所以放弃 cache 的自动适应几乎无损,换来的确定性极其值钱。

---

## 4. 为什么 AI 加速器适合 scratchpad

cache 优化"平均情况"(赌局部性,大多数时候赌对);scratchpad 优化"计划内情况"(软件提前安排好)。哪个适合 AI?

- **AI 的复用模式是结构化的**:tile 大小、权重块、激活块、部分和生命周期都相对可推导(见 [dataflow-taxonomy](../03-systolic-array/dataflow-taxonomy.md))。
- **所以** 你不是在"赌"局部性,而是在"设计"局部性——编译期就能算出每块数据何时该在片上。scratchpad 的显式管理在这里是优势不是负担。
- 反观 CPU 通用负载,控制流复杂、访问模式难静态预测,cache 的自动透明性才有价值。

这正是 archax 把 scratchpad 当默认模型的理由:目标架构(Groq 式静态、编译器决定数据放置)天然是 scratchpad 语义。

---

## 5. 本篇在主线上的位置

cache vs scratchpad 不直接改变[计算 / 通信比](../01-overview/compute-communication-ratio.md)的**大小**,而是改变分母的**可预测性**:把"数据从哪来"这个决策从运行时硬件随机(cache 命中/未命中)前移到编译期软件确定(scratchpad 显式指令)。对一个把 `data movement bytes` 当可审计物理量来建模的工具链而言,**确定性比平均更快更重要**——因为只有确定的分母才能在编译期精确求值。这是主线第三类手段("把分母变确定")的核心篇。

---

## 建模启示

- **cache 和 scratchpad 是两种不可混淆的 Interaction 语义,仿真里要用不同模型。**
  - **cache**:需要命中率模型、替换策略、非确定性 latency 分布(命中 vs 未命中两个分支)。
  - **scratchpad**:编译期可解析的确定性访存,latency 是固定值。
- **必须显式建模的状态变量**:`mem_kind ∈ {cache, scratchpad}`;cache 下额外需要 `hit_rate`、`replacement_policy`、`miss_latency`;scratchpad 下需要 `access_latency`(确定)和软件的搬运计划(`prefetch`/`evict` 时序)。
- **事件类型建议**:`ScratchpadAccess`(确定 latency)vs `CacheAccess`(带命中/未命中分支,latency 是分布)。两者在仿真里走不同代码路径。
- **archax 的默认与对照**:对 Groq 式静态架构,scratchpad 模型是默认(确定性、编译期可解析);但要保留对 cache 语义的建模能力以做对照(比较"自动 vs 显式"两种存储管理的代价)。
- **边界(不在 COMPUTE 模型里重复实现)**:cache 命中率、替换策略、DRAM 时序属于 RAM 域职责,见 [`RAM/.../why-mc-is-the-real-bottleneck`](../../../RAM/wiki/06-memory-controller/why-mc-is-the-real-bottleneck.md)。COMPUTE 模型只在"访存指令的 latency 是确定值还是分布"这个接口上对接。
