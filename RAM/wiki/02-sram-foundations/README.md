# SRAM 基础

上级：[`RAM/wiki/`](../)
相关：[同样是 RAM，为什么 SRAM 和 DRAM 走向了完全不同的工程路径](../01-overview/sram-dram-divergence.md), [SRAM 的应用形态](../03-sram-applications/README.md)

## 这页在回答什么问题

如果要把 SRAM 看成一条完整工程路线，而不是一句“快但贵”的摘要，最少需要先建立哪些基础概念。本章的任务，就是用最少但足够的电路和阵列语言，把后面 cache、scratchpad、register file、TCM、NPU buffer 共用的底层约束讲清楚。

## 正文

这一章之所以放在 DRAM 之前，不是因为 SRAM 在系统里一定更重要，而是因为它更适合做 RAM 的最小完备模型。SRAM 把一个 bit 存成可持续维持的双稳态电路，因此它没有 refresh、row activate、destructive read 这些额外复杂性。这样一来，很多最基本的问题就可以先在更干净的环境里成立：一个 bit 为什么能稳定存在，读写为什么会扰动这个状态，字线和位线分别在干什么，sense amp 为什么仍然重要，端口数为什么会迅速推高面积和时序难度，阵列为什么必须切成 bank 和 sub-array，而不能无限平铺。

本章的阅读顺序本身就是一条推导链。`6t-cell-bistable-storage.md` 先回答“一个 bit 为什么能被稳定存住”，这是最底层前提。`wordline-bitline-sense-amp.md` 接着回答“稳定存住之后，怎样把它变成可读可写的阵列资源”。`read-write-cycle-timing.md` 再把这些电路元素串成一次完整访问，明确读和写分别在什么阶段最脆弱。到这里为止，你得到的是一个能工作的单 bank SRAM 直觉。后面的 `single-port-dual-port-multi-port.md`、`sram-array-organization.md`、`sram-process-scaling-challenge.md`、`sram-power-leakage-retention.md`，则是在问：当你把这个局部电路放大成真正的工程对象时，哪些代价会先暴露出来。

这一章有一个很重要的边界条件：它讨论的是 SRAM 作为“物理与阵列基础”的共性，不直接展开它在系统里的具体语义。比如 cache 和 scratchpad 都可能用 SRAM 实现，但它们的差异不是先从 bit cell 开始的，而是从管理方式、命中语义、数据流角色开始的。因此这些话题会留到 `03-sram-applications/` 再讲。本章只关心一个问题：如果底层介质是 SRAM，那么无论上层把它叫 cache、register file 还是 local buffer，它们都会共同继承哪些约束。

这些共性约束主要有四类。第一类是稳定性约束，也就是 cell 在保持、读取、写入三种状态下如何避免翻转错误。第二类是访存路径约束，即字线、位线、预充、感测和写驱动如何决定访问时间。第三类是结构扩展约束，即端口数、banking、阵列尺寸和布线长度如何一起决定面积与频率。第四类是工艺与功耗约束，即先进制程下的漏电、Vmin 和保持能力如何反过来限制你“把 SRAM 做大、做低功耗、做高频”的自由度。后面每一篇其实都在处理这四类约束中的某一组。

这也是为什么理解 SRAM 不能只靠一句“6T、快、不刷新”。这句话虽然正确，但它没有告诉你为什么多端口 register file 如此昂贵，也没有告诉你为什么大容量片上 buffer 往往要切 bank、为什么低功耗模式下 retention 会变成设计变量、为什么先进制程反而会让 SRAM 更难收敛。你如果想做系统建模，这些问题都比“SRAM 的定义是什么”更接近真实瓶颈，因为它们决定了片上存储资源到底能以什么形状、什么延迟和什么能效被系统使用。

阅读这一章时，建议始终带着一个系统问题往回看：上层为什么喜欢用 SRAM 承担离计算最近的角色。答案当然包括低延迟，但更本质的原因是 SRAM 的访问成本更局部、更稳定、更容易被做成确定性资源。这个特性会在 `03-sram-applications/` 被系统化展开，在 `07-system-architecture/sram-vs-dram-access-pattern.md` 与 DRAM 形成直接对照。因此本章虽然在讲电路和阵列，目的并不是让你停在电路，而是为后面所有“片上快速存储”的系统判断提供地基。

## 一句话理解

本章要建立的是 SRAM 作为片上快速存储介质的最小完备模型：一个 bit 怎样稳定存在，一次访问怎样完成，一个阵列怎样扩展，以及这些能力为什么都要付出明确代价。

## 建模启示

这一章对应的建模重点，是先把 SRAM 当成“有限端口、有限 bank、近固定访问成本”的资源原型，而不是直接当成抽象 cache。为了做到这一点，后续模型至少需要能表达三类属性：`稳定属性`，例如容量、bank 数、端口数、基线访问延迟；`竞争属性`，例如端口冲突、bank 冲突；`功耗属性`，例如 active/read/write/retention 几种能耗状态。

一个适合作为后续章节公用底座的数据结构草图可以是：

```text
SramArrayModel {
  capacity_bytes: uint64
  bank_count: int
  ports_per_bank: int
  read_latency_cycles: int
  write_latency_cycles: int
  bank_busy_until[bank_count]: cycle
  port_busy_until[bank_count][ports_per_bank]: cycle
  retention_mode: enum { ACTIVE, LIGHT_SLEEP, DEEP_SLEEP }
}
```

如果只关心系统吞吐，bit cell 稳定性和 sense amp 电气细节可以暂时折叠，但 `ports_per_bank`、`read/write latency asymmetry`、`retention_mode` 这类属性最好保留，因为它们会直接影响 register file、scratchpad、TCM 和 NPU local buffer 的可行组织方式。后面 `03-sram-applications/` 的很多建模差异，本质上都建立在这一底座之上。
