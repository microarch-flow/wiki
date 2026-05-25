# MCU 里的 TCM，为什么实时性需要确定性 SRAM

上级：[SRAM 应用形态](./README.md)
相关：[Scratchpad 和 cache 都是 SRAM，差异在哪](./scratchpad-vs-cache.md), [MCU、CPU、GPU、NPU 为什么选择不同存储器](../07-system-architecture/why-systems-choose-different-memory.md)

## 这页在回答什么问题

为什么很多 MCU 和实时处理器宁愿给出一块容量不大、地址固定、功能朴素的 TCM，也不把同样面积全部拿去做 cache。更具体地说，在实时系统里，为什么“最坏情况可预测”常常比“平均情况更快”更值钱。

## 正文

如果站在通用计算的直觉上看，TCM 似乎有点”保守”——就像在高铁时代还有人坚持修建有轨电车。它通常不像 cache 那样透明、灵活，也不会自动根据局部性帮你提平均性能；很多时候它只是片上一块通过固定地址窗口访问的 SRAM，分成 `ITCM` 和 `DTCM`，分别给指令和数据走。可一旦系统目标从”平均吞吐更高”切换成”中断响应可控、控制回路抖动小、deadline 不丢”，TCM 的价值就会突然变得非常直接——有轨电车不能开很快，但它永远不会堵车。因为在实时系统里，真正危险的不是平均慢一点，而是某一次突然慢很多。

先把 TCM 的定位说清。`ITCM` 通常指 instruction tightly coupled memory，`DTCM` 指 data tightly coupled memory。它们之所以叫 tightly coupled，不是因为物理上神秘地“更近”，而是因为它们往往通过比 cache/memory hierarchy 更直接、更固定的路径接到核心上，地址映射固定，访问语义简单，命中与否不是概率事件。只要代码或数据被放进 TCM，对处理器来说，这一段访问延迟和带宽行为就更接近一个确定的本地 SRAM 资源，而不是一个可能 hit、可能 miss、可能触发 refill 的层次化对象。

这和 cache 的差别，不在”谁更快”这么简单，而在延迟分布的形状不同。想象两条通勤路线：cache 像走市区路线，大多数时候 20 分钟到，但偶尔遇上事故堵车要 2 小时；TCM 像走专用车道，每次都是 25 分钟，从不变化。对上班通勤来说，市区路线平均更快，偶尔迟到能忍受；但如果你是救护车司机，一次堵车就可能出人命——你一定选专用车道。MCU 里的中断处理、控制环、驱动时序和安全监控路径就是”救护车”：一个 ISR 如果平时 5 个周期取到指令，偶尔因为 I-cache miss 变成几十上百个周期，系统看到的不是”平均还行”，而是 deadline 被打穿。

这就是为什么实时系统更关注 `WCET`，也就是 worst-case execution time，而不只关注 average latency。TCM 的核心价值，就是帮助系统把一部分关键路径从概率型存储层次里剥离出来。只要最关键的代码段放进 ITCM，最关键的数据结构放进 DTCM，这些访问的时间边界就会更容易被分析和保证。常见误解是把 TCM 理解成”没有 cache 那么高级的老式 SRAM”；更准确的说法是，TCM 不是在追求更高级，而是在追求更可证明——就像机械表不是比智能手表落后，而是在追求不依赖电池的持续可靠性。

为什么要分成 ITCM 和 DTCM，也不只是命名习惯。代码流和数据流在实时处理器里往往有不同的带宽、并发和隔离需求。指令流更在意稳定取指和分支后的恢复成本，因此 ITCM 常常优先服务时间关键代码路径。数据流则可能混合栈、控制变量、DMA 交换区、采样窗口或中断共享数据，DTCM 需要更清晰的数据放置策略和与外设/DMA 的协同。把两者分开，一方面可以减轻结构冲突，另一方面也让软件更容易明确地把“哪些代码必须 deterministic、哪些数据必须 deterministic”区分出来。

从 SRAM 应用谱系看，TCM 更接近 scratchpad，而不是 cache。它通常没有 tag compare、没有替换逻辑、没有命中不确定性，也不会偷偷把某块数据驱逐掉。你放进去的东西，只要不被软件或 DMA 自己改掉，就会稳定待在那里。代价当然也很清楚：软件、链接脚本、启动加载流程、驱动和运行时系统必须显式知道什么应该进 TCM，容量也通常比“理想上想放进去的一切”小得多。也就是说，TCM 不是消灭复杂性，而是把复杂性从硬件局部性猜测，换成软件显式布局与容量管理。

这个 trade-off 对 MCU 特别合适，是因为许多 MCU 工作负载本来就能清楚区分关键与非关键路径。控制闭环代码、中断向量、启动代码、实时滤波核心、少量关键控制数据，都可以明确标记为“必须低抖动”；而大块非关键代码、配置数据或偶发访问数据则可以留在更便宜、更大的外部 Flash、SRAM 或普通存储层里。换句话说，MCU 往往不需要一个“尽量聪明地帮我优化一切访问”的系统，而需要一个“保证关键那部分永远可控，剩下的再谈平均效率”的系统。

这也解释了为什么很多 MCU 或实时核会同时存在 cache 和 TCM，而不是二选一。cache 适合服务那些控制流更复杂、但 deadline 没那么硬的访问；TCM 适合承载那些必须给出稳定边界的路径。两者放在一起，实际上是在把“平均优化”和“最坏情况优化”分摊给不同的 SRAM 形态。常见误解是认为有了 TCM 就不需要 cache，或者反过来有了 cache 就不需要 TCM；真正合理的设计通常是承认两者目标不同，因此让关键路径和普通路径走不同的内存契约。

从系统实现角度看，TCM 的另一个价值是分析简单。没有 tag、没有 replacement、没有 coherence 投机，访问路径更短，时序来源也更少。这不仅有利于实时分析，也有利于 safety case 和功能验证。因为你需要证明的事情少了：给定地址映射、仲裁规则和少量 DMA 交互，你更容易推导最坏访问时间。对功能安全或车规控制器来说，这种“容易证明”本身就是强价值，而不是附加属性。

当然，TCM 也不是免费午餐。它的容量通常有限，软件需要显式决定放什么进去，放错了会造成容量浪费或关键路径没保住；如果 DMA 和 CPU 共享 DTCM，还要小心银行冲突和仲裁；若系统后续 workload 变得更动态，纯 TCM 模式可能会增加软件维护成本。因此 TCM 的最佳使用方式，不是把所有热数据都塞进去，而是围绕 deadline 和 jitter 敏感度，挑出最需要 deterministic 行为的那一部分。

所以，TCM 的核心不是“更快的 SRAM”，而是“更可控的 SRAM”。它牺牲的是 cache 那种对平均局部性的自动适配，换来的是关键路径的低抖动、固定边界和更可分析的系统行为。把这一点看清，后面再讨论 MCU、CPU、GPU、NPU 为什么会选择不同的存储器路线时，实时系统的判断逻辑就会非常清楚。

## 一句话理解

TCM 的价值不在于它平均更快，而在于它把一部分关键访问从“可能 miss 的概率事件”变成“地址固定、时延边界可分析的确定性 SRAM 服务”。

## 建模启示

在性能模型里，TCM 不应被建成“小 cache”，而更应该被建成 `software-placed deterministic SRAM region`。最关键的字段不是 hit rate，而是 `fixed_access_latency`、`address_region`、`cpu_dma_contention_rule` 以及是否允许与普通 memory path 并存。

一个够用的抽象草图可以是：

```text
TcmModel {
  type: enum { ITCM, DTCM }
  capacity_bytes: uint64
  fixed_access_latency_cycles: int
  bank_count: int
  address_base: uint64
  address_limit: uint64
  cpu_dma_shared: bool
  arbitration_policy: enum { CPU_PRIORITY, FIXED_SLOT, ROUND_ROBIN }
}
```

对应事件流可以写成：

```text
event TcmAccess(req_id, addr, master)
event TcmService(req_id, bank_id)
event TcmConflict(req_id_a, req_id_b, bank_id)
```

如果只关心功能，`fixed_access_latency_cycles` 可能已经足够；但只要你关心实时性或 DMA 并发，`cpu_dma_shared` 和 `arbitration_policy` 就必须显式存在。因为很多系统中的抖动，不是来自 TCM 本身“像 cache 一样 miss”，而是来自关键路径和 DMA 或其他 master 在同一块 deterministic SRAM 上发生了竞争。
