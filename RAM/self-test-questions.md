# RAM Wiki 自测问题列表

总共 80 题。使用方式：从头到尾过一遍，能立刻答上来的跳过，犹豫的标记下来回 wiki 查证。
所有题目不附答案，每题指明对应的 wiki 文件名，查不出来时去源文件确认。

题目分层标记：[F] = 事实回忆，[T] = 理解迁移，[J] = 架构判断力。

---

## 01-overview（5 题）

1. [F] 当有人说“HBM 比 cache 更先进”时，你会用 RAM 的哪几个分类维度判断这句话哪里层级错位？
   `01-overview/taxonomy.md`

2. [T] 一次 NPU pipeline bubble 表面上是“数据没到”，你会沿哪些存储层级追问它可能来自 SRAM bank、DRAM row、MC 调度、封装带宽还是 workload 复用问题？
   `01-overview/problem-statement.md`

3. [J] 如果一个系统同时要求大容量、低延迟、低功耗和低成本，你为什么不应该寻找一种单一“最优 RAM”，而应该设计存储层次？
   `01-overview/memory-hierarchy-tension.md`

4. [F] SRAM 和 DRAM 的根本分化为什么不是“一个要 refresh、一个不要”，而是两种 bit 存储方式对应的目标函数分化？
   `01-overview/sram-dram-divergence.md`

5. [T] 如果一个架构模型只把 HBM 当成高峰值带宽资源，而不建 DRAM row/bank、MC 调度和封装约束，会遗漏哪些关键因果链？
   `01-overview/learning-roadmap.md`

---

## 02-sram-foundations（8 题）

6. [F] 6T SRAM cell 为什么必须同时满足 hold stability、read stability 和 write-ability，而不能只说“能存 0/1”？
   `02-sram-foundations/6t-cell-bistable-storage.md`

7. [T] SRAM 读是 cell 轻推位线、写是位线强推 cell；这个差异会怎样导致读延迟、写延迟和恢复窗口不能简单合成一个 access time？
   `02-sram-foundations/read-write-cycle-timing.md`

8. [J] 在一个局部 buffer 需要两路并发读的场景里，你如何判断应付 true multi-port SRAM 的代价，还是用 banking、复制或时分复用规避？
   `02-sram-foundations/single-port-dual-port-multi-port.md`

9. [F] SRAM 的字线、位线和 sense amp 分别在一次低延迟读访问中承担什么角色，为什么 sense amp 不是可有可无的外围电路？
   `02-sram-foundations/wordline-bitline-sense-amp.md`

10. [T] 当 SRAM 容量从几十 KB 增到数 MB 时，为什么把阵列切成 bank、sub-array、mat 既影响并行度，也影响单次访问延迟和能耗？
   `02-sram-foundations/sram-array-organization.md`

11. [J] 对一块长时间不访问但后续仍可能复用的数据 SRAM，你会如何在 retention 和 power-off 之间做选择，关键取舍是什么？
   `02-sram-foundations/sram-power-leakage-retention.md`

12. [F] 先进制程下 SRAM scaling 失速主要卡在哪些约束上，为什么不能假设 SRAM 面积、Vmin 和稳定性随逻辑工艺线性变好？
   `02-sram-foundations/sram-process-scaling-challenge.md`

13. [T] 如果一个 SRAM 模型只有 capacity、latency、bandwidth 三个字段，你会如何判断它遗漏了 bank 冲突、端口占用或 post-access recovery 这些关键行为？
   `02-sram-foundations/sram-array-organization.md`

---

## 03-sram-applications（7 题）

14. [F] cache 的 tag array 为什么不是 data array 的“注释信息”，而是命中路径里决定数据能否被当作结果的关键结构？
   `03-sram-applications/cache-sram-tag-data-arrays.md`

15. [T] 对一个可由编译器精确 tiling 的矩阵计算 workload，为什么 scratchpad 可能比 cache 更适合承载局部数据？
   `03-sram-applications/scratchpad-vs-cache.md`

16. [J] 在 MCU 的中断处理和控制闭环路径中，为什么 TCM 的确定性可能比 cache 的平均命中收益更重要？
   `03-sram-applications/tcm-itcm-dtcm-in-mcu.md`

17. [F] register file 为什么是 SRAM 设计空间中的极端点，尤其在端口数、同拍语义和执行管线时序上？
   `03-sram-applications/register-file-as-sram.md`

18. [T] weight、activation、accumulator buffer 的生命周期、读写方向和复用模式分别不同，这会怎样改变 NPU 片上 SRAM 的瓶颈位置？
   `03-sram-applications/npu-weight-buffer-activation-buffer.md`

19. [J] 两个 NPU 都宣称 16 MB 片上 SRAM，为什么按 weight/activation/psum 角色切分不同，会导致完全不同的实际吞吐？
   `03-sram-applications/npu-weight-buffer-activation-buffer.md`

20. [J] 在 L1 cache 设计中，你会何时选择 tag/data 并行访问，何时选择先判 tag 再读 data 或 way prediction，取舍依据是什么？
   `03-sram-applications/cache-sram-tag-data-arrays.md`

---

## 04-dram-foundations（10 题）

21. [F] 1T1C DRAM cell 为什么会把读出、恢复和刷新变成同一条物理路线上的系统负担？
   `04-dram-foundations/1t1c-cell-destructive-read.md`

22. [T] 如果一个 DRAM bank 当前打开 row A，而请求目标是 row B，你如何从物理访问路径推导出 PRE、ACT、RD/WR 的必要顺序？
   `04-dram-foundations/row-column-decode-sense-amplify.md`

23. [J] 在仿真中把 row buffer 建成 set-associative cache 会引入哪些错误假设，为什么更合理的抽象是 per-bank open-row state？
   `04-dram-foundations/row-buffer-as-cache.md`

24. [F] bank 为什么是 DRAM 内部最小的并行调度单位，它复制了哪些状态，又仍然共享哪些资源？
   `04-dram-foundations/bank-organization-parallelism.md`

25. [T] 如果请求流热点持续集中在同一个 bank，为什么增加总 bank 数未必提高有效吞吐，问题可能出在什么映射或流量形状上？
   `04-dram-foundations/bank-organization-parallelism.md`

26. [J] 在容量需求上升时增加 rank 为什么可以增加容量和部分并行机会，却不能被当作增加 channel 峰值带宽？
   `04-dram-foundations/channel-rank-chip-hierarchy.md`

27. [F] refresh 为什么应被理解为会占用 bank/rank 资源的 blocking event，而不是平均摊进每个请求的常数延迟？
   `04-dram-foundations/refresh-the-fundamental-cost.md`

28. [T] 对一个 bursty workload，controller 推迟 refresh 可能改善当前读延迟；为什么这种策略也可能在后续形成更大的 tail spike？
   `04-dram-foundations/refresh-the-fundamental-cost.md`

29. [T] DRAM core 慢而宽、I/O 快而窄的节奏失配，为什么会自然推导出 prefetch 和 burst 这两个机制？
   `04-dram-foundations/bank-group-prefetch-burst.md`

30. [J] 当 DRAM 平面缩放继续推进时，为什么 cell 电容保持能力会成为密度、retention 和 I/O 密度路线的共同瓶颈？
   `04-dram-foundations/dram-process-stacking-trends.md`

---

## 05-dram-protocol-families（10 题）

31. [F] DDR 的“双倍数据率”提升的是什么层面的速率，为什么不能把它理解为 DRAM cell/core 随机访问频率翻倍？
   `05-dram-protocol-families/why-double-data-rate.md`

32. [T] 给定 row hit、bank closed 的 row miss、row conflict 三种状态，你如何分别生成最小 DRAM 命令流？
   `05-dram-protocol-families/commands-act-rd-wr-pre.md`

33. [J] 如果一个 DRAM 设备对外隐藏 ACT/PRE，只暴露 read/write 黑盒接口，controller 利用 row locality 和 bank interleaving 的能力会受到什么影响？
   `05-dram-protocol-families/commands-act-rd-wr-pre.md`

34. [F] tRCD、tCL、tRAS、tRP 分别对应 DRAM 哪些物理等待过程，为什么它们不是孤立的规格表常数？
   `05-dram-protocol-families/timing-parameters-trcd-trp-tras.md`

35. [T] 从 timing guard 的角度看，为什么 row conflict 比 row hit 多付出的不是一个小常数，而是完整的关行和开行等待链？
   `05-dram-protocol-families/timing-parameters-trcd-trp-tras.md`

36. [J] 比较 DDR 代际时，如果只把模型里的 MT/s 调高，为什么可能严重误判真实 workload 的有效带宽收益？
   `05-dram-protocol-families/ddr-generation-evolution.md`

37. [F] LPDDR 为了待机功耗、I/O 能耗和近封装集成，主动牺牲了通用 DDR 的哪些系统自由度？
   `05-dram-protocol-families/lpddr-low-power-mobile.md`

38. [T] 对一个多数时间轻载、偶尔短 burst 的移动端 workload，LPDDR 的 self-refresh 或 partial-array 策略在什么条件下才有系统收益？
   `05-dram-protocol-families/lpddr-low-power-mobile.md`

39. [T] GDDR 继续提高 pin-rate，而 HBM 缩短距离并扩大位宽；这两条路线分别是在缓解哪类互连和能耗压力？
   `05-dram-protocol-families/hbm-stacked-wide-io.md`

40. [J] 在 DDR、LPDDR、GDDR、HBM 之间选型时，为什么“峰值带宽最高”不能作为唯一排序标准？
   `05-dram-protocol-families/ddr-lpddr-gddr-hbm-tradeoff-map.md`

---

## 06-memory-controller（12 题）

41. [F] 地址映射为什么不是把物理地址被动切成 channel/rank/bank/row/col，而是在塑造请求流的几何形状？
   `06-memory-controller/address-mapping-channel-rank-bank-row-col.md`

42. [T] 对连续 cache line 访问，你会如何分析“保留 row locality”和“更早做 bank/channel striping”之间的取舍？
   `06-memory-controller/address-mapping-channel-rank-bank-row-col.md`

43. [J] 多 master 共享 DRAM 时，如果低带宽控制流被大吞吐流长期压住，你会如何设计 QoS 规则来保护尾延迟而不过度牺牲总吞吐？
   `06-memory-controller/qos-multi-master-arbitration.md`

44. [F] FR-FCFS 中的 ready-first 和 row-hit-first 分别在利用 DRAM 的哪两类状态机会？
   `06-memory-controller/command-scheduling-fr-fcfs.md`

45. [T] FR-FCFS 为什么会同时提高吞吐并制造 starvation 风险，这两个结果如何来自同一个 row-hit 偏好？
   `06-memory-controller/command-scheduling-fr-fcfs.md`

46. [J] 当一个 row-friendly DMA 流持续压制 CPU 控制读请求时，你会给 FR-FCFS 增加 aging、max-wait 还是 per-master quota，判断依据是什么？
   `06-memory-controller/command-scheduling-fr-fcfs.md`

47. [F] open-page、close-page 和 adaptive page policy 分别在赌未来访问模式的哪种性质？
   `06-memory-controller/page-policy-open-close-adaptive.md`

48. [T] 为什么 page policy 会改变 FR-FCFS 能看到的 row-hit 候选分布，因此两者不能分开评价？
   `06-memory-controller/page-policy-open-close-adaptive.md`

49. [J] 当 workload 从大块顺序 GEMM 切到 attention decode 的散点 KV cache 访问时，page policy 应如何重新判断 open 与 close 的风险？
   `06-memory-controller/page-policy-open-close-adaptive.md`

50. [F] write buffer 的 high/low watermark 和 write-drain 模式分别解决什么问题，为什么读写请求不能完全对称调度？
   `06-memory-controller/write-buffer-write-drain.md`

51. [T] 推迟 refresh 和 write drain 都是在调整事件相位；为什么前者的主要风险是 deadline debt，后者的主要风险是读延迟和写缓冲压力？
   `06-memory-controller/refresh-management-distributed-postponed.md`

52. [J] 如果要在 cycle-level 模型中解释多 master QoS 尾延迟，哪些 MC 状态必须显式保留，哪些电路细节可以折叠？
   `06-memory-controller/mc-modeling-for-simulation.md`

---

## 07-system-architecture（10 题）

53. [F] latency 和 bandwidth 分别回答什么系统问题，为什么“带宽高”不等于“第一份关键数据更快到达”？
   `07-system-architecture/bandwidth-vs-latency-fundamental.md`

54. [T] 为什么 HBM 这类高带宽路径可能显著改善大张量搬运，却不一定改善小而急的控制访问？
   `07-system-architecture/bandwidth-vs-latency-fundamental.md`

55. [J] 面对张量流式搬运和指针追踪两类 workload，你会分别优先优化 startup latency、sustained throughput 还是 outstanding 并发能力？
   `07-system-architecture/bandwidth-vs-latency-fundamental.md`

56. [F] 一次 cache miss 从 tag miss 到 refill 完成，中间通常会经过哪些状态和事务边界？
   `07-system-architecture/cache-dram-coordination.md`

57. [T] cache 为什么不只是减少外存访问次数，还会改变 DRAM 看到的请求粒度、顺序和并发形态？
   `07-system-architecture/cache-dram-coordination.md`

58. [J] 如果实测有效带宽远低于峰值，你会按什么逻辑顺序定位瓶颈，避免只盯着峰值带宽数字？
   `07-system-architecture/effective-bandwidth-vs-peak.md`

59. [F] register file、cache、scratchpad、DRAM、HBM 在系统角色上分别解决什么问题，而不只是“快慢容量不同”？
   `07-system-architecture/memory-hierarchy-as-system.md`

60. [T] SRAM 的访问成本主要受当前端口/bank 冲突影响，而 DRAM 强依赖 open-row 短历史；这个差异如何改变 workload 映射策略？
   `07-system-architecture/sram-vs-dram-access-pattern.md`

61. [J] 多 channel 或 NUMA 扩大了总资源，为什么单个任务如果线程和页面放置不匹配，可能不变快甚至变慢？
   `07-system-architecture/numa-multi-channel-multi-socket.md`

62. [J] 对 MCU、CPU、GPU、NPU 四类系统，你如何先识别失败模式，再推导各自更合理的存储层次组合？
   `07-system-architecture/why-systems-choose-different-memory.md`

---

## 08-packaging-integration（5 题）

63. [F] DIMM/SODIMM 为什么愿意接受更长电气路径，它换来的容量扩展、可维护性和生态自由度是什么？
   `08-packaging-integration/dimm-sodimm-traditional-forms.md`

64. [T] PoP/MCP 为什么适合移动 SoC 的近距集成和低功耗目标，却不适合服务器式模块化扩容？
   `08-packaging-integration/pop-mcp-mobile-integration.md`

65. [J] HBM 的超宽近距 I/O 为什么不能只靠协议成立，而必须依赖 TSV、stack、base die、interposer 或 2.5D/3D 集成共同支撑？
   `08-packaging-integration/hbm-2.5d-3d-tsv.md`

66. [F] HBM 的高成本应如何从 DRAM stack、KGD/test、interposer、封装良率、热设计和供应链协同这些环节拆解？
   `08-packaging-integration/why-hbm-is-expensive.md`

67. [T] CXL memory expansion、near-memory compute 和先进封装分别在改变哪一层内存边界，为什么它们不是互相替代的同类方案？
   `08-packaging-integration/future-packaging-cxl-near-memory.md`

---

## 09-ai-chip-memory-architecture（8 题）

68. [F] NPU 的 L0/L1/L2 SRAM 层次为什么应被看成数据流拓扑，而不是 CPU cache hierarchy 的简单平移？
   `09-ai-chip-memory-architecture/npu-memory-hierarchy.md`

69. [T] data movement first 原则会如何改变 NPU 中 dataflow、buffer 大小、DMA 节拍和外存路线的设计优先级？
   `09-ai-chip-memory-architecture/data-movement-first-principle.md`

70. [J] 设计 weight buffer 时，你如何从权重复用距离、tile blocking、PE 分发几何和读带宽反推容量与 bank 组织？
   `09-ai-chip-memory-architecture/weight-buffer-design.md`

71. [T] activation double buffering 在什么条件下真正隐藏 refill，在什么条件下只是多占了一份 SRAM 但仍然 stall？
   `09-ai-chip-memory-architecture/activation-buffer-and-double-buffering.md`

72. [F] NPU 的片上带宽预算为什么必须拆成 weight、activation、psum、refill 和 drain 多类流量，而不能只报一个总 SRAM 带宽？
   `09-ai-chip-memory-architecture/on-chip-bandwidth-budget.md`

73. [T] 判断一个 NPU 是否 memory-bound 时，为什么要继续定位瓶颈是在外存、NoC 分发、本地 SRAM bank，还是 psum read-modify-write 回路？
   `09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md`

74. [J] 面对云端大模型推理和边缘 NPU 两种产品目标，你会如何在 HBM 与 LPDDR 之间做外存路线判断？
   `09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md`

75. [J] 如果外层必须选 LPDDR 而不是 HBM，片上 SRAM 容量、tiling 粒度、复用策略和 DMA overlap 应怎样补偿外带宽约束？
   `09-ai-chip-memory-architecture/hbm-vs-lpddr-for-npu.md`

---

## 跨 wiki 综合题（5 题）

76. [J] DRAM controller 接到 AXI 总线时，如何处理 QoS 透传、read/write ordering、outstanding transaction 与 write-drain 策略之间的冲突？
   `[RAM × BUS]`

77. [J] 多个 NPU tile 通过 NoC 共享 HBM 时，NoC 的 burst 聚合、拥塞和 response path 会如何改变 MC 看到的 row/bank 流量形状？
   `[RAM × NOC]`

78. [J] 在 NPU double buffering 中，DMA refill 应如何同时对齐 DRAM 访问局部性和片上消费节拍？
   `[RAM × DMA]`

79. [J] HBM 的理论带宽为什么可能被 interposer routing、PDN/SI、热耦合、package test 和良率折损成更低的系统可持续带宽？
   `[RAM × FAB]`

80. [J] 从 RAM 视角看，DRAM-PIM 与 SRAM-CIM 在数据位置、刷新/保持、外围计算开销和上层 memory hierarchy 边界上有什么本质差异？
   `[RAM × CIM]`
