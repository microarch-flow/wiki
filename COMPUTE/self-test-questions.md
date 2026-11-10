# COMPUTE Wiki 自测问题列表

本表有 64 道编号题和 4 道跨章节综合题。使用方式:从头到尾过一遍,能立刻答上来的跳过,犹豫的标记下来回 wiki 查证。
所有题目不附答案。每题附有现行 wiki 的参考正文。

题目分层标记:[F] = 事实回忆,[T] = 理解迁移,[J] = 架构判断力。

> 分别说明资源、工作量、边界和单位。查阅 [计算与通信指标](./wiki/01-overview/compute-communication-ratio.md)。

---

## 01-overview(7 题)

1. [F] 算术强度、有效吞吐、面积和能耗各使用什么单位？比较前为什么要固定工作量和统计边界？
   [参考正文](./wiki/01-overview/compute-communication-ratio.md)

2. [T] RF、阵列和片外存储边界分别统计哪些字节？同一字节穿过多个边界时，为什么不能把这些计数的和叫作片外流量？
   [参考正文](./wiki/01-overview/compute-communication-ratio.md)

3. [J] 比较 Strassen 与直接矩阵乘时，哪些运算、数据移动、临时存储和数值误差前提可能改变结论？
   [参考正文](./wiki/01-overview/compute-communication-ratio.md)

4. [F] 假设三路 8:1、p 位 mux 的成本代理各为 8p，乘法器核心代理为 4p，两项代理之比是多少？为什么这不是实芯片面积份额？
   [参考正文](./wiki/01-overview/problem-statement.md)

5. [T] 一个阵列峰值 MAC/s 很高但任务吞吐低，你会从哪些供数、利用率和时序条件查起？
   [参考正文](./wiki/01-overview/problem-statement.md)

6. [J] 如何比较具有不同选择网络和本地存储的两个 datapath？为何不能直接用门数代理之比推断 MAC/byte 或能耗？
   [参考正文](./wiki/01-overview/problem-statement.md)

7. [F] COMPUTE、RAM、NOC、DMA、FAB 分别提供哪些信息？建模时如何标明它们共同涉及的资源边界？
   [参考正文](./wiki/01-overview/taxonomy-and-roadmap.md)

---

## 02-datapath-foundations（14 题）

8. [F] 矩阵乘的计算中乘法和累加如何组合？MAC 的输入、输出和累加状态是什么？
   [参考正文](./wiki/02-datapath-foundations/multiply-accumulate-from-gates.md)

9. [T] 两个无符号 4 bit 最大乘积相加时，需要多少位才能精确保存？8 bit 溢出与舍入有何不同？
   [参考正文](./wiki/02-datapath-foundations/multiply-accumulate-from-gates.md)

10. [F] 一个 full adder 的输入、输出分别是什么？它与一个多位加法器有何区别？
   [参考正文](./wiki/02-datapath-foundations/multiply-accumulate-from-gates.md)

11. [J] 乘法器部分积数量能说明什么，不能直接说明什么？压缩器数量为何不是 p×q 的恒等式？
   [参考正文](./wiki/02-datapath-foundations/multiply-accumulate-from-gates.md)

12. [T] carry-save 为什么能推迟跨列进位传播？压缩树为何通常先输出两行，再由末级进位传播加法器产生结果？
   [参考正文](./wiki/02-datapath-foundations/dadda-and-adder-trees.md)

13. [J] Wallace 与 Dadda 压缩树在归约调度和硬件成本方面如何比较？比较时需固定哪些条件？
   [参考正文](./wiki/02-datapath-foundations/dadda-and-adder-trees.md)

14. [J] ripple、CLA 和 prefix 进位结构可能如何影响面积与路径延迟？怎样判断其中一条路径是否限制时钟？
   [参考正文](./wiki/02-datapath-foundations/dadda-and-adder-trees.md)

15. [F] 在生成全部部分积的整数乘法结构中，p×q 表示什么？双操作数位宽减半时，这个代理如何变化？
   [参考正文](./wiki/02-datapath-foundations/quadratic-bitwidth-scaling.md)

16. [T] 为什么不能从整数部分积数量直接推导 FP4 相对 FP8 的产品吞吐或面积比？
   [参考正文](./wiki/02-datapath-foundations/quadratic-bitwidth-scaling.md)

17. [J] 浮点乘加除了尾数乘法，还需要哪些处理？累加精度为何不能忽略？
   [参考正文](./wiki/02-datapath-foundations/number-formats-for-ai.md)

18. [T] FP16 与 bf16 的 S/E/M 字段如何分配？它们在 1 上方的相邻可表示数间隔及指数范围有何区别？
   [参考正文](./wiki/02-datapath-foundations/number-formats-for-ai.md)

19. [J] OCP MXFP4 的 32 元素块分别包含哪些元素字段和共享 scale？无对齐填充时，与裸 FP4、裸 FP8 各需多少字节？
   [参考正文](./wiki/02-datapath-foundations/number-formats-for-ai.md)

20. [J] 同为 FP8，OCP E4M3 与 E5M2 在 1 附近的间隔、有限范围和 Inf/NaN 支持有何不同？性能比较还需什么条件？
   [参考正文](./wiki/02-datapath-foundations/number-formats-for-ai.md)

21. [F] n:1、p 位 mux 的输入、选择信号和输出是什么？其实际面积还取决于哪些实现因素？
   [参考正文](./wiki/02-datapath-foundations/mux-and-data-movement-cost.md)

---

## 03-systolic-array(11 题)

22. [F] 在 3 行、2 列阵列上完成一个长度为 3 的矩阵向量乘，共有多少次 MAC？指定阵列边界和数据位宽后，如何计算 MAC/byte？
   [参考正文](./wiki/03-systolic-array/why-systolic-array.md)

23. [T] PE 并行度、局部数据复用与阵列有效吞吐分别是什么？为什么增加 PE 数不保证任务加速？
   [参考正文](./wiki/03-systolic-array/why-systolic-array.md)

24. [J] systolic array 的权重本地驻留与 CIM 的计算位置有何区别？如何按实际 cell、array path 和算术单元判断？
   [参考正文](./wiki/03-systolic-array/why-systolic-array.md)

25. [F] weight-stationary 与 output-stationary 分别倾向让哪个张量驻留？还需要统计哪些数据跨边界移动？
   [参考正文](./wiki/03-systolic-array/dataflow-taxonomy.md)

26. [J] 对深 reduction、高精度部分和的 GEMM，如何比较 weight- 与 output-stationary 的流量、容量和归约代价？
   [参考正文](./wiki/03-systolic-array/dataflow-taxonomy.md)

27. [J] 为什么 dataflow 的选择不能单独保证高吞吐？batch、阵列填充、权重驻留和带宽分别可能产生什么影响？
   [参考正文](./wiki/03-systolic-array/dataflow-taxonomy.md)

28. [T] 卷积的 sliding window 可以形成哪些输入、权重和部分和的复用？row-stationary 如何尝试利用它们？
   [参考正文](./wiki/03-systolic-array/dataflow-taxonomy.md)

29. [F] 为什么首块冷权重和换 tile 时的加载需要计时间、能量和带宽？窄通道的潜在收益是什么？
   [参考正文](./wiki/03-systolic-array/weight-loading-and-trickle-feed.md)

30. [T] 每拍注入 x 个权重且 y 行同步移位时，灌满需要多少拍？为什么不能在这些拍之后再重复加 y−1 拍？
   [参考正文](./wiki/03-systolic-array/weight-loading-and-trickle-feed.md)

31. [J] 单 bank 与双 bank 分别需要满足哪些条件才能加载下一 tile？如果加载长于当前计算，等待如何产生？
   [参考正文](./wiki/03-systolic-array/weight-loading-and-trickle-feed.md)

32. [J] 比较 64×64 与 128×128 阵列时，RF 面积固定的摊销假设、供数需求、填充和真实利用率应如何分别检查？
   [参考正文](./wiki/03-systolic-array/array-sizing-tradeoff.md)

---

## 04-clocking-and-pipeline(11 题)

33. [F] 同步寄存器何时采样？为什么时钟沿不表示整片芯片每拍都暂停？
   [参考正文](./wiki/04-clocking-and-pipeline/global-clock-synchronization.md)

34. [T] 同一时钟域反馈路径完整 setup 要求为 1.0 ns、前馈路径为 1.4 ns；假设没有更慢路径，周期和频率上限如何计算？
   [参考正文](./wiki/04-clocking-and-pipeline/global-clock-synchronization.md)

35. [J] setup 与 hold 各检查最大还是最小路径延迟？PVT、时钟偏斜和 uncertainty 应如何进入时序判断？
   [参考正文](./wiki/04-clocking-and-pipeline/global-clock-synchronization.md)

36. [F] 同一工艺下，逻辑、布线、时钟树与工作点为何可能使不同设计的频率上限不同？
   [参考正文](./wiki/04-clocking-and-pipeline/global-clock-synchronization.md)

37. [T] 前馈路径插入寄存器后，周期、事务 latency、II、面积和功耗可能如何变化？为何频率不一定翻倍？
   [参考正文](./wiki/04-clocking-and-pipeline/pipeline-register-insertion.md)

38. [J] 哪些功能依赖、寄存器和布线开销会限制继续切分流水级？跨时钟域还要单独检查什么？
   [参考正文](./wiki/04-clocking-and-pipeline/pipeline-register-insertion.md)

39. [F] 在累加器反馈路径上直接插入一拍，会如何改变状态递推？为何要重新验证计算语义？
   [参考正文](./wiki/04-clocking-and-pipeline/feedback-loop-clock-constraint.md)

40. [J] 缩短反馈路径、交错累加和改变归约树各需付出什么代价？浮点或饱和运算重排还要验证什么？
   [参考正文](./wiki/04-clocking-and-pipeline/feedback-loop-clock-constraint.md)

41. [T] 累加位宽如何同时影响数值范围与路径实现？时钟域的频率是否只由反馈路径决定？
   [参考正文](./wiki/04-clocking-and-pipeline/feedback-loop-clock-constraint.md)

42. [J] 单位面积吞吐与总吞吐分别如何计算？提高频率时，面积、有效工作量和 II 变化为何也要评估？
   [参考正文](./wiki/04-clocking-and-pipeline/frequency-is-not-throughput.md)

43. [T] 改变频率或 batch 时，如何按具体实现测量延迟和吞吐？为何不能预先断定二者的 Pareto 位置？
   [参考正文](./wiki/04-clocking-and-pipeline/frequency-is-not-throughput.md)

---

## 05-fpga-vs-asic(5 题)

44. [F] FPGA 与 ASIC 的选择涉及哪些一次性成本、单位成本、产量及更新需求？为什么不能套固定报价？
   [参考正文](./wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md)

45. [T] 可配置互连和 LUT 的配置分别控制什么？FPGA 中还有哪些可影响映射的硬块？
   [参考正文](./wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md)

46. [F] 4 输入 LUT 的真值表有多少个输出位？输入如何选出当前函数值？
   [参考正文](./wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md)

47. [J] 一个 AND 函数的门级表达与 LUT 真值表能说明什么结构差异？为什么不能从它们的抽象元件数推出统一面积或功耗倍数？
   [参考正文](./wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md)

48. [J] 若已知两种实现各自的 NRE 与单位成本，怎样求产量交点？还应比较哪些性能、功耗和生命周期因素？
   [参考正文](./wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md)

---

## 06-memory-discipline(5 题)

49. [F] cache 的命中与服务时间可能依赖哪些初始状态、地址流、替换和仲裁规则？
   [参考正文](./wiki/06-memory-discipline/cache-vs-scratchpad.md)

50. [T] scratchpad 由软件显式放置数据；为什么地址已知仍不能保证整笔访问的完成时间？
   [参考正文](./wiki/06-memory-discipline/cache-vs-scratchpad.md)

51. [J] 单 bank、单读端口每拍接纳一次，两个请求周期 0 同时到达，服务延迟一拍。不同仲裁选择如何影响各自完成时刻？
   [参考正文](./wiki/06-memory-discipline/cache-vs-scratchpad.md)

52. [J] 什么 workload 特征可能使显式 scratchpad 管理有利？容量不足、动态访问或争用可能带来什么代价？
   [参考正文](./wiki/06-memory-discipline/cache-vs-scratchpad.md)

53. [T] 确定性模拟 cache 和 scratchpad 分别需要哪些状态、事件与资源规则？何时才使用有前提的统计近似？
   [参考正文](./wiki/06-memory-discipline/cache-vs-scratchpad.md)

---

## 07-chip-organization(8 题)

54. [F] 比较 CPU 与 GPU 的资源组织时，应列出哪些控制、算术、寄存器和存储资源？为什么不能假定通用面积占比？
   [参考正文](./wiki/07-chip-organization/cpu-vs-gpu-core-area.md)

55. [T] 分支预测试图隐藏什么依赖或等待？其收益和代价为何取决于工作负载与具体实现？
   [参考正文](./wiki/07-chip-organization/cpu-vs-gpu-core-area.md)

56. [J] 专用计算结构如何改变可支持的工作、资源配置和软件映射？如何在相同工作量下比较，而非假定某类资源没有价值？
   [参考正文](./wiki/07-chip-organization/cpu-vs-gpu-core-area.md)

57. [F] 功率和能量的单位分别是什么？动态功率的简化模型中，活动率、电容、电压和频率怎样关联？
   [参考正文](./wiki/07-chip-organization/brain-vs-chip-power.md)

58. [J] 固定电压、同一任务、相同有效翻转次数下，频率减半并使时间翻倍时，动态功率和动态任务能量如何变化？
   [参考正文](./wiki/07-chip-organization/brain-vs-chip-power.md)

59. [J] 若运行时间增加而静态功率不变，静态任务能量怎样变化？时钟门控、DVFS 和外围行为为何可能改变估计？
   [参考正文](./wiki/07-chip-organization/brain-vs-chip-power.md)

60. [T] 比较大共享阵列与多个局部阵列时，供数、归约、外围复制和利用率分别应检查什么？
   [参考正文](./wiki/07-chip-organization/gpu-as-tiled-tpu.md)

61. [J] 可切分阵列可能适配哪些工作块？需要如何验证额外互连、分区、切换与带宽代价？
   [参考正文](./wiki/07-chip-organization/gpu-as-tiled-tpu.md)

---

## 08-modeling-for-archax（3 题）

62. [J] 如何分别计算阵列、RF 和片外存储边界的 MAC/byte？跨多个边界计数为何不能直接视为单个片外流量？
   [参考正文](./wiki/08-modeling-for-archax/modeling-insights.md)

63. [T] 将资源、连接、事件和能力用于模型设计时，哪些内容属于建议，哪些必须通过目标实现验证？
   [参考正文](./wiki/08-modeling-for-archax/modeling-insights.md)

64. [J] 同一时钟域前馈和反馈路径怎样共同约束频率？为什么还要分别记录 hold、事务延迟与 II？
   [参考正文](./wiki/08-modeling-for-archax/modeling-insights.md)

---

## 跨章节综合题（4 题）

- **A.** [J] 对同一个工作量，如何分别估算 datapath 面积、阵列边界 MAC/byte 和单位面积吞吐？这些指标为什么不能互相替代？
  参考：[mux 面积代理](./wiki/02-datapath-foundations/mux-and-data-movement-cost.md)、[阵列边界例子](./wiki/03-systolic-array/why-systolic-array.md)、[吞吐](./wiki/04-clocking-and-pipeline/frequency-is-not-throughput.md)。

- **B.** [J] 对一个 MXFP4 矩阵任务，如何同时统计块 scale、尾块填充、权重加载、数据复用和结果输出？
  参考：[数字格式](./wiki/02-datapath-foundations/number-formats-for-ai.md)、[权重加载](./wiki/03-systolic-array/weight-loading-and-trickle-feed.md)。

- **C.** [T] 为什么显式 scratchpad 放置与一个通过 setup 的时钟约束，仍不足以证明每个请求的完成时间？
  参考：[存储争用](./wiki/06-memory-discipline/cache-vs-scratchpad.md)、[时钟路径](./wiki/04-clocking-and-pipeline/global-clock-synchronization.md)。

- **D.** [J] 同一字节依次跨 RF、阵列和外存边界时，如何分别计数、选择统计窗口并避免将层间计数误当片外流量？
  参考：[计算与通信指标](./wiki/01-overview/compute-communication-ratio.md)、[建模建议](./wiki/08-modeling-for-archax/modeling-insights.md)。
