# RAM Wiki 自测问题列表

总共 82 题。前 80 题保留原 RAM 章节编号；第 81、82 题跨专题。使用方式：从头到尾过一遍，能立刻答上来的跳过，犹豫的标记下来回 wiki 查证。
所有题目不附答案。每题附有现行 wiki 的参考正文；跨专题题附多个来源。

题目分层标记：[F] = 事实回忆，[T] = 理解迁移，[J] = 架构判断力。

---

## 01-overview（5 题）

<ol start="1" markdown>

1. [F] 当有人说“HBM 比 cache 更先进”时，你会用 RAM 的哪几个分类维度判断这句话哪里层级错位？
   [参考正文](../../01-memory-hierarchy/01-system-basics/taxonomy.md)

2. [T] 一次 NPU pipeline bubble 表面上是“数据没到”，你会沿哪些存储层级追问它可能来自 SRAM bank、DRAM row、MC 调度、封装带宽还是 workload 复用问题？
   [参考正文](../../01-memory-hierarchy/01-system-basics/problem-statement.md)

3. [J] 如果一个系统同时要求大容量、低延迟、低功耗和低成本，你为什么不应该寻找一种单一“最优 RAM”，而应该设计存储层次？
   [参考正文](../../01-memory-hierarchy/01-system-basics/memory-hierarchy-tension.md)

4. [F] SRAM 和 DRAM 的根本分化为什么不是“一个要 refresh、一个不要”，而是两种 bit 存储方式对应的目标函数分化？
   [参考正文](../../01-memory-hierarchy/01-system-basics/sram-dram-divergence.md)

5. [T] 如果一个架构模型只把 HBM 当成高峰值带宽资源，而不建 DRAM row/bank、MC 调度和封装约束，会遗漏哪些关键因果链？
   [参考正文](./learning-roadmap.md)

</ol>

---

## 02-sram-foundations（8 题）

<ol start="6" markdown>

6. [F] 6T SRAM cell 为什么必须同时满足 hold stability、read stability 和 write-ability，而不能只说“能存 0/1”？
   [参考正文](../../02-sram/foundations/6t-cell-bistable-storage.md)

7. [T] SRAM 的读出、写入与恢复有哪些不同电气阶段？宏接口的输出可见边沿和下一次接纳间隔为何要分别确定？
   [参考正文](../../02-sram/foundations/read-write-cycle-timing.md)

8. [J] 在一个局部 buffer 需要两路并发读的场景里，你如何判断应付 true multi-port SRAM 的代价，还是用 banking、复制或时分复用规避？
   [参考正文](../../02-sram/foundations/single-port-dual-port-multi-port.md)

9. [F] 典型 6T 差分读中，字线、位线和 sense amp 各承担什么角色？为什么感测方式必须以具体宏为准？
   [参考正文](../../02-sram/foundations/wordline-bitline-sense-amp.md)

10. [T] 当 SRAM 容量从几十 KB 增到数 MB 时，为什么把阵列切成 bank、sub-array、mat 既影响并行度，也影响单次访问延迟和能耗？
   [参考正文](../../02-sram/foundations/sram-array-organization.md)

11. [J] 对一块长时间不访问但后续仍可能复用的数据 SRAM，你会如何在 retention 和 power-off 之间做选择，关键取舍是什么？
   [参考正文](../../02-sram/foundations/sram-power-leakage-retention.md)

12. [F] 先进制程下 SRAM scaling 失速主要卡在哪些约束上，为什么不能假设 SRAM 面积、Vmin 和稳定性随逻辑工艺线性变好？
   [参考正文](../../02-sram/foundations/sram-process-scaling-challenge.md)

13. [T] 如果一个 SRAM 模型只有 capacity、latency、bandwidth 三个字段，你会如何判断它遗漏了 bank 冲突、端口占用或 post-access recovery 这些关键行为？
   [参考正文](../../02-sram/foundations/sram-array-organization.md)

</ol>

---

## 03-sram-applications（7 题）

<ol start="14" markdown>

14. [F] cache 的 tag array 为什么不是 data array 的“注释信息”，而是命中路径里决定数据能否被当作结果的关键结构？
   [参考正文](../../02-sram/applications/cache-sram-tag-data-arrays.md)

15. [T] 对一个可由编译器精确 tiling 的矩阵计算 workload，为什么 scratchpad 可能比 cache 更适合承载局部数据？
   [参考正文](../../01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)

16. [J] 在 MCU 中断和控制闭环中，TCM 的显式放置可能有什么价值？若端口或总线发生竞争，访问时间还需要哪些前提才能确定？
   [参考正文](../../02-sram/applications/tcm-itcm-dtcm-in-mcu.md)

17. [F] register file 为什么是 SRAM 设计空间中的极端点，尤其在端口数、同拍语义和执行管线时序上？
   [参考正文](../../02-sram/applications/register-file-as-sram.md)

18. [T] weight、activation、accumulator buffer 的生命周期、读写方向和复用模式分别不同，这会怎样改变 NPU 片上 SRAM 的瓶颈位置？
   [参考正文](../../02-sram/applications/npu-weight-buffer-activation-buffer.md)

19. [J] 两个 NPU 都宣称 16 MB 片上 SRAM，为什么按 weight/activation/psum 角色切分不同，会导致完全不同的实际吞吐？
   [参考正文](../../02-sram/applications/npu-weight-buffer-activation-buffer.md)

20. [J] 在 L1 cache 设计中，你会何时选择 tag/data 并行访问，何时选择先判 tag 再读 data 或 way prediction，取舍依据是什么？
   [参考正文](../../02-sram/applications/cache-sram-tag-data-arrays.md)

</ol>

---

## 04-dram-foundations（10 题）

<ol start="21" markdown>

21. [F] 1T1C DRAM cell 为什么会把读出、恢复和刷新变成同一条物理路线上的系统负担？
   [参考正文](../../03-dram/foundations/1t1c-cell-destructive-read.md)

22. [T] 如果一个 DRAM bank 当前打开 row A，而请求目标是 row B，你如何从物理访问路径推导出 PRE、ACT、RD/WR 的必要顺序？
   [参考正文](../../03-dram/foundations/1t1c-cell-destructive-read.md#row-state)

23. [J] 在仿真中把 row buffer 建成 set-associative cache 会引入哪些错误假设，为什么更合理的抽象是 per-bank open-row state？
   [参考正文](../../03-dram/foundations/1t1c-cell-destructive-read.md#model)

24. [F] 常见 DRAM bank 为何是控制器可见的重要并行调度单位？它维护哪些状态，又与其他 bank 共享哪些资源？更细粒度并行能力为何要以具体器件为准？
   [参考正文](../../03-dram/foundations/bank-organization-parallelism.md)

25. [T] 如果请求流热点持续集中在同一个 bank，为什么增加总 bank 数未必提高有效吞吐，问题可能出在什么映射或流量形状上？
   [参考正文](../../03-dram/foundations/bank-organization-parallelism.md)

26. [J] 在容量需求上升时增加 rank 为什么可以增加容量和部分并行机会，却不能被当作增加 channel 峰值带宽？
   [参考正文](../../03-dram/foundations/channel-rank-chip-hierarchy.md)

27. [F] refresh 为什么应被理解为会占用 bank/rank 资源的 blocking event，而不是平均摊进每个请求的常数延迟？
   [参考正文](../../03-dram/foundations/refresh-the-fundamental-cost.md)

28. [T] 对一个 bursty workload，controller 推迟 refresh 可能改善当前读延迟；为什么这种策略也可能在后续形成更大的 tail spike？
   [参考正文](../../03-dram/foundations/refresh-the-fundamental-cost.md)

29. [T] DRAM core 慢而宽、I/O 快而窄的节奏失配，为什么会自然推导出 prefetch 和 burst 这两个机制？
   [参考正文](../../03-dram/foundations/bank-group-prefetch-burst.md)

30. [J] DRAM 单元缩放时，电容、漏电和制造约束如何影响密度与 retention？I/O 密度又需要单独检查哪些接口和封装因素？
   [参考正文](../../03-dram/foundations/dram-process-stacking-trends.md)

</ol>

---

## 05-dram-protocol-families（10 题）

<ol start="31" markdown>

31. [F] DDR 的“双倍数据率”提升的是什么层面的速率，为什么不能把它理解为 DRAM cell/core 随机访问频率翻倍？
   [参考正文](../../03-dram/protocols/why-double-data-rate.md)

32. [T] 给定 row hit、bank closed 的 row miss、row conflict 三种状态，你如何分别生成最小 DRAM 命令流？
   [参考正文](../../03-dram/protocols/commands-act-rd-wr-pre.md)

33. [J] 如果一个 DRAM 设备对外隐藏 ACT/PRE，只暴露 read/write 黑盒接口，controller 利用 row locality 和 bank interleaving 的能力会受到什么影响？
   [参考正文](../../03-dram/protocols/commands-act-rd-wr-pre.md)

34. [F] DDR4 中 tRCD、CL、AL、tRAS 和 tRP 的参考动作各是什么？即使 ACT 后没有列命令，显式 PRE 还须满足什么条件？
   [参考正文](../../03-dram/protocols/timing-parameters-trcd-trp-tras.md)

35. [T] 假设 DDR4 BL8、CA parity 和 CS-to-CA latency 均关闭、无写 CRC、AL=0、CWL=9、nWR=12，WR 在周期 0。写恢复参考沿和 PRE 的写约束下界如何计算？若 ACT 的 tRAS 下界更晚，还应怎样处理？
   [参考正文](../../03-dram/protocols/timing-parameters-trcd-trp-tras.md)

36. [J] 比较 DDR 代际时，如果只把模型里的 MT/s 调高，为什么可能严重误判真实 workload 的有效带宽收益？
   [参考正文](../../03-dram/protocols/ddr-generation-evolution.md)

37. [F] 比较具体 LPDDR 与 DDR 系统时，待机功耗、I/O、封装、容量和模块化扩展分别有什么约束？为什么不能假定所有 LPDDR 都采用同一种封装？
   [参考正文](../../03-dram/protocols/lpddr-low-power-mobile.md)

38. [T] 对一个多数时间轻载、偶尔短 burst 的移动端 workload，LPDDR 的 self-refresh 或 partial-array 策略在什么条件下才有系统收益？
   [参考正文](../../03-dram/protocols/lpddr-low-power-mobile.md)

39. [T] GDDR 与 HBM 如何分别利用单引脚速率、总位宽和连接方式获取带宽？比较能耗时还需要限定哪些测量边界？
   [参考正文](../../03-dram/protocols/hbm-stacked-wide-io.md)

40. [J] 在 DDR、LPDDR、GDDR、HBM 之间选型时，为什么“峰值带宽最高”不能作为唯一排序标准？
   [参考正文](../../03-dram/protocols/ddr-lpddr-gddr-hbm-tradeoff-map.md)

</ol>

---

## 06-memory-controller（12 题）

<ol start="41" markdown>

41. [F] 地址映射为什么不是把物理地址被动切成 channel/rank/bank/row/col，而是在塑造请求流的几何形状？
   [参考正文](../../04-dram-controller/address-mapping-channel-rank-bank-row-col.md)

42. [T] 对连续 cache line 访问，你会如何分析“保留 row locality”和“更早做 bank/channel striping”之间的取舍？
   [参考正文](../../04-dram-controller/address-mapping-channel-rank-bank-row-col.md)

43. [J] 多 master 共享 DRAM 时，如果低带宽控制流被大吞吐流长期压住，你会如何设计 QoS 规则来保护尾延迟而不过度牺牲总吞吐？
   [参考正文](../../04-dram-controller/qos-multi-master-arbitration.md)

44. [F] 某个 FR-FCFS 实现如何定义 ready 和优先级？列命令就绪与 row hit 有何联系，为什么不能假定所有实现的排序规则相同？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md)

45. [T] FR-FCFS 的 row-hit 偏好在什么流量和资源条件下可能提高吞吐？它为何也可能增加其他请求的饥饿风险？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md)

46. [J] 当一个 row-friendly DMA 流持续压制 CPU 控制读请求时，你会给 FR-FCFS 增加 aging、max-wait 还是 per-master quota，判断依据是什么？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md)

47. [F] open-page、close-page 和 adaptive page policy 分别在赌未来访问模式的哪种性质？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md#page-policy)

48. [T] 为什么 page policy 会改变 FR-FCFS 能看到的 row-hit 候选分布，因此两者不能分开评价？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md#queue-choice)

49. [J] 当 workload 从大块顺序 GEMM 切到 attention decode 的散点 KV cache 访问时，page policy 应如何重新判断 open 与 close 的风险？
   [参考正文](../../04-dram-controller/command-scheduling-fr-fcfs.md#自适应策略要看什么)

50. [F] write buffer 的 high/low watermark 和 write-drain 模式分别解决什么问题，为什么读写请求不能完全对称调度？
   [参考正文](../../04-dram-controller/write-buffer-write-drain.md)

51. [T] 推迟 refresh 或 write drain 分别改变哪些时限和队列状态？分析时为什么还要考虑写队列填满、读写切换和读延迟？
   [参考正文](../../04-dram-controller/refresh-management-distributed-postponed.md)

52. [J] 如果要在 cycle-level 模型中解释多 master QoS 尾延迟，哪些 MC 状态必须显式保留，哪些电路细节可以折叠？
   [参考正文](../../04-dram-controller/mc-modeling-for-simulation.md)

</ol>

---

## 07-system-architecture（10 题）

<ol start="53" markdown>

53. [F] latency 和 bandwidth 分别回答什么系统问题，为什么“带宽高”不等于“第一份关键数据更快到达”？
   [参考正文](../../01-memory-hierarchy/03-performance/bandwidth-vs-latency-fundamental.md)

54. [T] 为什么 HBM 这类高带宽路径可能显著改善大张量搬运，却不一定改善小而急的控制访问？
   [参考正文](../../01-memory-hierarchy/03-performance/bandwidth-vs-latency-fundamental.md)

55. [J] 面对张量流式搬运和指针追踪两类 workload，你会分别优先优化 startup latency、sustained throughput 还是 outstanding 并发能力？
   [参考正文](../../01-memory-hierarchy/03-performance/bandwidth-vs-latency-fundamental.md)

56. [F] 一次 cache miss 从 tag miss 到 refill 完成，中间通常会经过哪些状态和事务边界？
   [参考正文](../../01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)

57. [T] cache 为什么不只是减少外存访问次数，还会改变 DRAM 看到的请求粒度、顺序和并发形态？
   [参考正文](../../01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)

58. [J] 如果实测有效带宽远低于峰值，你会按什么逻辑顺序定位瓶颈，避免只盯着峰值带宽数字？
   [参考正文](../../01-memory-hierarchy/03-performance/effective-bandwidth-vs-peak.md)

59. [F] register file、cache、scratchpad、DRAM 和 HBM 分别描述系统角色、介质还是接口？如何避免把不同分类维度直接当作同类选项？
   [参考正文](../../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md)

60. [T] SRAM 的访问成本主要受当前端口/bank 冲突影响，而 DRAM 强依赖 open-row 短历史；这个差异如何改变 workload 映射策略？
   [参考正文](../../01-memory-hierarchy/02-access-paths/sram-vs-dram-access-pattern.md)

61. [J] 多 channel 或 NUMA 扩大了总资源，为什么单个任务如果线程和页面放置不匹配，可能不变快甚至变慢？
   [参考正文](../../01-memory-hierarchy/02-access-paths/numa-multi-channel-multi-socket.md)

62. [J] 对 MCU、CPU、GPU、NPU 四类系统，你如何先识别失败模式，再推导各自更合理的存储层次组合？
   [参考正文](../../06-system-integration/why-systems-choose-different-memory.md)

</ol>

---

## 08-packaging-integration（5 题）

<ol start="63" markdown>

63. [F] DIMM/SODIMM 的可插拔形态可能带来哪些容量扩展和维护收益？电气路径、信号完整性和速率约束为何要依据具体拓扑比较？
   [参考正文](../../06-system-integration/packaging/dimm-sodimm-traditional-forms.md)

64. [T] PoP 与 MCP 的定义有何不同？比较具体 LPDDR 封装或模块时，近距集成、可维护性和扩容如何取舍？
   [参考正文](../../06-system-integration/packaging/pop-mcp-mobile-integration.md)

65. [J] HBM stack 内部的垂直互连与计算芯片到 stack 的连接各解决什么问题？比较具体封装时，TSV、base die、interposer 或 bridge 的作用是什么？
   [参考正文](../../06-system-integration/hbm-vs-lpddr-for-npu.md#path)

66. [F] HBM 的高成本应如何从 DRAM stack、KGD/test、interposer、封装良率、热设计和供应链协同这些环节拆解？
   [参考正文](../../06-system-integration/hbm-vs-lpddr-for-npu.md#yield)

67. [T] CXL memory expansion、near-memory compute 和先进封装分别在改变哪一层内存边界，为什么它们不是互相替代的同类方案？
   [参考正文](../../06-system-integration/future-packaging-cxl-near-memory.md)

</ol>

---

## 09-ai-chip-memory-architecture（8 题）

<ol start="68" markdown>

68. [F] 对具有多级片上存储的 NPU，为什么要先核对实际 buffer、连接和管理方式，而不能仅凭 L0/L1/L2 名称推断拓扑？
   [参考正文](../../01-memory-hierarchy/04-npu-case/npu-memory-hierarchy.md#paths)

69. [T] 在搬运受限的 NPU 工作负载中，数据流、buffer 大小、DMA 节拍和外存路线如何影响搬运？何时还应优先检查计算瓶颈？
   [参考正文](../../01-memory-hierarchy/04-npu-case/npu-memory-hierarchy.md#traffic)

70. [J] 设计 weight buffer 时，你如何从权重复用距离、tile blocking、PE 分发几何和读带宽反推容量与 bank 组织？
   [参考正文](../../01-memory-hierarchy/04-npu-case/npu-memory-hierarchy.md#supply)

71. [T] activation double buffering 在什么条件下真正隐藏 refill，在什么条件下只是多占了一份 SRAM 但仍然 stall？
   [参考正文](../../01-memory-hierarchy/04-npu-case/activation-buffer-and-double-buffering.md)

72. [F] NPU 的片上带宽预算为什么必须拆成 weight、activation、psum、refill 和 drain 多类流量，而不能只报一个总 SRAM 带宽？
   [参考正文](../../01-memory-hierarchy/04-npu-case/on-chip-bandwidth-budget.md)

73. [T] 判断一个 NPU 是否 memory-bound 时，为什么要继续定位瓶颈是在外存、NoC 分发、本地 SRAM bank，还是 psum read-modify-write 回路？
   [参考正文](../../01-memory-hierarchy/03-performance/memory-bound-vs-compute-bound.md)

74. [J] 面对云端大模型推理和边缘 NPU 两种产品目标，你会如何在 HBM 与 LPDDR 之间做外存路线判断？
   [参考正文](../../06-system-integration/hbm-vs-lpddr-for-npu.md)

75. [J] 如果产品选择 LPDDR 且测得外带宽不足，片上容量、tiling、复用和 DMA overlap 有哪些可能的改善方式？为什么不能假设它们总能补足带宽缺口？
   [参考正文](../../06-system-integration/hbm-vs-lpddr-for-npu.md)

</ol>

---

## 跨 wiki 综合题（5 题）

<ol start="76" markdown>

76. [J] DRAM controller 接到 AXI 总线时，如何处理 QoS 透传、read/write ordering、outstanding transaction 与 write-drain 策略之间的冲突？
   [BUS outstanding 与排序](../../../interconnect/BUS/03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[RAM write drain](../../04-dram-controller/write-buffer-write-drain.md)

77. [J] 多个 NPU tile 通过 NoC 共享 HBM 时，NoC 的 burst 聚合、拥塞和 response path 会如何改变 MC 看到的 row/bank 流量形状？
   [NOC 流量](../../../interconnect/NOC/05-system-integration/traffic-patterns-and-characterization.md)、[RAM 控制器模型](../../04-dram-controller/mc-modeling-for-simulation.md)

78. [J] 在 NPU double buffering 中，DMA refill 应如何同时对齐 DRAM 访问局部性和片上消费节拍？
   [DMA 双缓冲](../../../microarchitecture/05-dma/04-programming-model/tiling-double-buffering.md)、[RAM activation buffer](../../01-memory-hierarchy/04-npu-case/activation-buffer-and-double-buffering.md)

79. [J] HBM 的 interposer 路由、PDN/SI 和热约束可能如何影响持续带宽？package test 与良率又如何影响成本或可供货性，为什么不能直接把它们当作带宽损失？
   [FAB 封装信号完整性](../../../chip-development/FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md)、[RAM HBM 成本](../../06-system-integration/hbm-vs-lpddr-for-npu.md#yield)

80. [J] 从 RAM 视角看，DRAM-PIM 与 SRAM-CIM 在数据位置、刷新/保持、外围计算开销和上层 memory hierarchy 边界上有什么本质差异？
   [CIM DRAM-PIM](../../../microarchitecture/08-in-memory-computing/02-memory-technologies/dram-pim-foundation.md)、[CIM SRAM-CIM](../../../microarchitecture/08-in-memory-computing/02-memory-technologies/sram-cim-foundation.md)


</ol>

## 可靠性与 HBF 补充题（2 题）

<ol start="81" markdown>

81. [T] 某 SRAM 使用 ECC 时，为什么初始化、部分写入和错误注入必须结合具体实现检查？未经初始化的校验位可能带来什么问题？
   [参考正文](../../02-sram/foundations/sram-reliability-ecc-mbist-repair.md)

82. [J] 在 HBM 与 HBF 组成的系统中，选择哪些数据放在 HBF 时，应如何比较访问粒度、写入与更新、并发、恢复和应用容忍度？
   [参考正文](../../05-hbf/07-workload-and-modeling.md) · [写入与可靠性](../../05-hbf/06-write-and-reliability.md)

</ol>

HBF 的专项练习与资料见 [HBF 术语、资料与自测](../../05-hbf/09-reference.md)。
