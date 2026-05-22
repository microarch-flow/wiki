# 学习路径与各章节依赖关系

上级：[概览](./README.md)
相关：[RAM 家族的分类与命名体系](./taxonomy.md), [存储器设计的第一性原理清单](../10-reference/first-principles.md)

## 这页在回答什么问题

如果目标不是“知道术语”，而是形成可用于架构判断和性能建模的存储器心智模型，应该按什么顺序读。更关键的是，每一章到底在给下一章提供什么前提，为什么这套顺序不适合随意打乱。

## 正文

这套 wiki 的阅读顺序不是按名词热度排的，也不是按市场产品排的，而是按因果依赖排的。你最终当然会关心 `DDR5`、`HBM`、`LPDDR`、`cache miss`、`NPU buffer` 这些问题，但如果一开始就从这些页面切入，很容易只记住“现象”和“对比表”，却不知道它们为什么必须这样设计。为了避免这个问题，这套路径强制先把底层约束建立起来，再逐层推到系统和应用。

第一步是完整读完 `01-overview/`。这一章的任务不是提供技术细节，而是校正问题的问法。你需要先接受三件事：第一，存储器问题天然跨层，不能压成一个“平均内存延迟”来理解。第二，`SRAM` 和 `DRAM` 不是一条技术路线上的高低配，而是两种目标函数不同的设计点。第三，后面讨论的每一个对象，都必须先分清它是在说单元、阵列、协议、控制器、系统角色还是封装形态。如果这三点没有先立住，后面的知识会不断串线。

第二步是读 `02-sram-foundations/`，然后接着读 `03-sram-applications/`。这个顺序看起来可能有点反直觉，因为很多人接触内存是从 DDR 开始的，不是从 SRAM 开始的。但对建立第一性理解来说，SRAM 更适合做起点。原因很简单：它的最小完备模型更干净。6T cell、双稳态、字线位线、sense amp、端口数、banking，这些概念在 SRAM 里可以先不被 refresh、row activate、prefetch、burst 这些额外复杂性打断。等你再去看 register file、cache、scratchpad、TCM、NPU local buffer，就会发现这些东西虽然系统语义不同，底层其实都在复用同一组 SRAM 约束。

第三步是读 `04-dram-foundations/`。这一步最好不要跳过，因为很多对 DRAM 的误解都来自把它当成“更慢的大 SRAM”。这一章要建立的不是几个专有名词，而是一套新的访问因果链：1T1C 单元为什么会导致破坏性读出，为什么破坏性读出又要求先感测整行、再恢复、再进行列访问，为什么 refresh 不是背景噪声而是系统成本，为什么 bank 和 row buffer 会决定访问模式是否友好。只要这条因果链没建立起来，后面的 DDR 协议页再详细，也容易被读成“时序参数记忆题”。

第四步是 `05-dram-protocol-families/` 和 `06-memory-controller/`。这两章建议连着读，因为协议和控制器在系统里本来就是配套出现的。`05` 章负责回答“DRAM 为什么给系统暴露出 ACT、RD、WR、PRE、tRCD、burst、bank group 这些接口和约束”；`06` 章负责回答“系统如何在这些约束下调度请求，把理论带宽尽量变成有效带宽”。如果只读协议不读控制器，你会停在器件视角；如果只读控制器不读协议，很多调度策略就会显得像经验规则，而不是从 cell 和阵列限制推出来的结果。

第五步是 `07-system-architecture/`。这一章开始把前面的组件重新拼回系统，回答的问题会从“一个存储器怎么工作”转成“多个存储层放在一起时会发生什么”。例如 cache miss 之后，如何一路映射到 channel/bank/row；峰值带宽为什么会被 row conflict、refresh 和总线切换侵蚀；多通道和 NUMA 为什么扩展了资源，也扩展了软件和拓扑代价；SRAM 和 DRAM 在访问模式上的根本差异，为什么会把同样的 workload 变成两种完全不同的瓶颈。这一章是从部件知识进入系统判断的分水岭。

第六步是 `08-packaging-integration/`。很多人会把封装看成后端工艺附录，所以倾向于最后再看。这一章放在系统章之后而不是最末尾，是为了强调一件事：在 HBM、AI 加速器和高带宽系统里，封装不是“实现细节”，而是直接决定 I/O 宽度、互连距离、功耗和成本的架构变量。只有在前面已经理解了“距离成本”之后，才会真正看懂为什么 `DIMM`、`PoP`、`HBM + 2.5D` 会走出完全不同的系统路线。

最后读 `09-ai-chip-memory-architecture/` 和 `10-reference/`。`09` 章不是平行主线，而是应用压缩层。它默认你已经理解 SRAM、DRAM、protocol、controller、system 和 packaging 的约束，然后把这些约束压到 NPU 的真实问题上，例如片上多级 SRAM 为什么要这样分工，weight/activation buffer 怎样从模型和数据流反推，HBM 和 LPDDR 的边界在哪里，什么叫“数据搬运优先”。`10` 章则是把前面的知识整理成可复用的查阅页、checklist 和建模模板，适合在你已经有全局图之后反复回看，而不是拿来替代主线阅读。

如果你的时间有限，可以跳读，但跳读需要知道自己在放弃什么。只想建立全局判断框架，可以先读 `01 -> 07 -> 08 -> 10`，但这样会牺牲对 SRAM/DRAM 物理约束的细节直觉。只想快速做 DRAM/DDR 性能建模，可以读 `01 -> 04 -> 05 -> 06 -> 07`，但这样会弱化对片上 SRAM 组织和 NPU buffer 设计的认识。只想理解 AI 芯片内存架构，最危险的跳法是直接去读 `09`，因为你会很容易把 `HBM` 当成一个更大的带宽数字，而不是一种由 DRAM 协议、封装和控制策略共同构成的系统选择。

所以，这页给出的不是“推荐目录”，而是一张依赖图。前面的章节不是为了铺垫而铺垫，而是在不断定义后面章节能否被正确理解的前提条件。你完全可以带着问题定向回跳，但第一次完整学习时，最好不要打乱这条顺序。

## 一句话理解

这套 wiki 的顺序是按因果依赖而不是按话题热度排列的：先建立单元与阵列直觉，再进入协议与控制器，最后回到系统、封装和 AI 场景。

## 建模启示

这页本质上是在给后续模型定义“抽象层级的构建顺序”。如果从建模角度表达，它对应的不是一个硬件模块，而是一张模型依赖图。比较实用的做法是把后续章节映射成四层对象：`primitive_model`、`protocol_model`、`controller_model`、`system_model`。只有下层对象已经定义清楚，上层对象的参数和事件语义才不会漂浮。

一个简单的依赖草图可以写成：

```text
primitive_model:
  - SRAMCellArray
  - DRAMBankArray

protocol_model:
  - DDRCommandTiming
  - LPDDRPowerState
  - HBMWideIOInterface

controller_model:
  - AddressMapper
  - Scheduler
  - RefreshManager

system_model:
  - CacheHierarchy
  - NocDmaPath
  - MemoryTierGraph
```

如果只做粗粒度系统吞吐评估，可以跳过部分 `primitive_model` 的电路细节，但不能跳过它定义出的资源语义。例如，即使不显式模拟 SRAM bitline，也仍然需要保留 `num_ports` 和 `bank_count`；即使不显式模拟 DRAM sense amp，也仍然需要保留 `open_row`、`timing_guard` 和 `refresh_event`。这一页的核心作用，就是提醒你不要在模型还没分层时就直接堆系统参数。
