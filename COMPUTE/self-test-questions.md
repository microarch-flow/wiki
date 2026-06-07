# COMPUTE Wiki 自测问题列表

总共 64 题。使用方式:从头到尾过一遍,能立刻答上来的跳过,犹豫的标记下来回 wiki 查证。
所有题目不附答案,每题指明对应的 wiki 文件名,查不出来时去源文件确认。

题目分层标记:[F] = 事实回忆,[T] = 理解迁移,[J] = 架构判断力。

> 贯穿全表的一根线:几乎每道题最终都能归到一个问题——**这个机制把"有用计算 / 数据搬运"这个比值往哪个方向推?** 答不出主线位置的,就是没真懂。纲领见 `01-overview/compute-communication-ratio.md`。

---

## 01-overview(7 题)

1. [F] 为什么 COMPUTE 域衡量算力单元好坏用的是一个**比值**而不是绝对算力(FLOP)?分子和分母各是什么?
   `01-overview/compute-communication-ratio.md`

2. [T] 同一个 trade-off 在比特精度、datapath、systolic array、pipeline、FPGA/ASIC、顶层布局六个层级各出现一次。任意给你一层,你能说出它的"分子项""分母项"和"抬比值的手段"吗?
   `01-overview/compute-communication-ratio.md`

3. [J] 为什么 Strassen 算法(把矩阵乘的乘法数从 O(n³) 降到 O(n^2.81))从不用于 AI?给出两层原因,并说明它为何是本域主线的最纯反证。
   `01-overview/compute-communication-ratio.md`

4. [F] 在一个 8-entry RF + 一个 MAC 的裸 datapath 上,数据搬运门数和计算门数的比例大约是多少?这个数从哪来?
   `01-overview/problem-statement.md`

5. [T] 有人说"AI 加速器快是因为乘法器更多更强"。你会用哪几个"砍分母"的例子反驳这个说法?
   `01-overview/problem-statement.md`

6. [J] 为什么通用 CPU 躲不掉那 24p 的灵活性税,而 AI 负载能系统性地把它砍掉?哪两个 workload 结构性特征是前提?
   `01-overview/problem-statement.md`

7. [F] 为什么 COMPUTE 域的"分母"恰好是 RAM/NOC/DMA/FAB 各域的主体?这对建模时的职责切分意味着什么?
   `01-overview/taxonomy-and-roadmap.md`

---

## 02-datapath-foundations(13 题)

8. [F] 为什么 MAC(而非单独的乘法或加法)是 AI 芯片的天然原语?它是从什么结构里"长出来"的?
   `02-datapath-foundations/multiply-accumulate-from-gates.md`

9. [T] "累加要高精度"有两个**独立**的理由,数值范围只是其一。另一个是什么?为什么它更本质?
   `02-datapath-foundations/multiply-accumulate-from-gates.md`

10. [F] 一个 full adder 是几进几出?它"不是软件里的 32-bit 加法器",那它本质在做什么?
   `02-datapath-foundations/multiply-accumulate-from-gates.md`

11. [J] `full adder 数 = p×q` 这个代数闭合很优雅,但它是精确恒等式还是首阶估计?为什么这个区分对建模诚实性重要?
   `02-datapath-foundations/multiply-accumulate-from-gates.md`

12. [T] 为什么压缩树要用 carry-save 而不是逐列等进位传播?这把加法树的延迟从什么量级压到什么量级?
   `02-datapath-foundations/dadda-and-adder-trees.md`

13. [J] Wallace 和 Dadda 都把比特山压到高度 2,关键路径层数相同。那它们到底差在哪?什么场景你会选 Dadda?
   `02-datapath-foundations/dadda-and-adder-trees.md`

14. [J] 压缩树最后那个 vector-merge 加法器(final CPA)的进位结构(ripple/CLA/Kogge-Stone)什么时候是面积问题,什么时候升级成频率上限问题?
   `02-datapath-foundations/dadda-and-adder-trees.md`

15. [F] 乘法器面积为什么 ∝ 位宽² 而非 ∝ 位宽?位宽减半,面积降到几分之几?
   `02-datapath-foundations/quadratic-bitwidth-scaling.md`

16. [T] Nvidia 在 B300 之前按"位宽减半→FLOP 翻倍"标 spec。为什么说这个线性假设其实偏保守?B300 改标成多少?
   `02-datapath-foundations/quadratic-bitwidth-scaling.md`

17. [J] 浮点为什么拿不到完整的 4× 二次缩放收益?列出至少两个不随 mantissa 位宽二次缩小的项。
   `02-datapath-foundations/number-formats-for-ai.md`

18. [T] FP16 和 bf16 都是 16 位,行为却差很远。bf16 把位押在哪、砍在哪?这服从了训练负载的什么数值特性?
   `02-datapath-foundations/number-formats-for-ai.md`

19. [J] MX(microscaling)格式的价值"很大一部分是搬运账,不只是算力账"。共享 exponent 如何同时拨动主线的分子和分母两端?
   `02-datapath-foundations/number-formats-for-ai.md`

20. [J] "FP4 算力 = 2× FP8"为什么不是一个干净的物理常数?把这个 k 拆成三个来源。
   `02-datapath-foundations/number-formats-for-ai.md`

21. [F] "选第 3 号寄存器"在硬件上是什么电路?一个 n 输入、p 位的 mux 成本大约几个门?
   `02-datapath-foundations/mux-and-data-movement-cost.md`

---

## 03-systolic-array(11 题)

22. [F] systolic array 相对裸 datapath,compute 涨多少、communication 涨多少?净赚的"y 倍"是什么的量级?
   `03-systolic-array/why-systolic-array.md`

23. [T] 有人说 systolic array 的优势是"PE 多、并行度高"。为什么这是表象?真正的优势是什么?
   `03-systolic-array/why-systolic-array.md`

24. [J] systolic array 的权重就地驻留看起来很像存内计算。它和 CIM 的边界精确在哪一句话上?
   `03-systolic-array/why-systolic-array.md`

25. [F] weight-stationary、output-stationary 各自让哪个张量驻留、消除哪个张量的搬运?
   `03-systolic-array/dataflow-taxonomy.md`

26. [J] 一个 reduction 维度很深、部分和精度很高的 GEMM,你倾向 weight- 还是 output-stationary?为什么?
   `03-systolic-array/dataflow-taxonomy.md`

27. [J] 为什么说"选对 dataflow 就能保证高比值"是错的?小 batch / decode 场景下瓶颈退回到哪里,此时换 dataflow 为什么无济于事?
   `03-systolic-array/dataflow-taxonomy.md`

28. [T] 卷积的 sliding window 让相邻输出共享大量输入。哪种 dataflow 专为榨取这种三重局部性设计?
   `03-systolic-array/dataflow-taxonomy.md`

29. [F] 权重载入为什么"只在乎窄,不在乎慢"?优化目标是带宽还是延迟,为什么?
   `03-systolic-array/weight-loading-and-trickle-feed.md`

30. [T] trickle-feed 如何用 y 个周期、x 宽的通道,灌满一个 x×y 的阵列?它用什么换了什么?
   `03-systolic-array/weight-loading-and-trickle-feed.md`

31. [J] "配置流 vs 数据流"是两种语义完全不同的数据移动。把权重载入按稳态流建模会犯什么错?MoE 频繁切权重时这个区分为什么会失效?
   `03-systolic-array/weight-loading-and-trickle-feed.md`

32. [J] 为什么阵列不是越大越好?给出"大阵列摊薄 RF"和"小矩阵 PE 空转"这一对反向力,说明最优点为何在 Pareto 前沿而非端点。
   `03-systolic-array/array-sizing-tradeoff.md`

---

## 04-clocking-and-pipeline(11 题)

33. [F] 芯片为什么用全局时钟同步而不用软件式的 mutex?时钟周期由什么决定?
   `04-clocking-and-pipeline/global-clock-synchronization.md`

34. [T] 把 2 GHz 的周期翻译成门深:TSMC 基本门 ~10ps,0.5ns 大约是多少个门延迟的预算?为什么实际每周期只塞 10–30 门?
   `04-clocking-and-pipeline/global-clock-synchronization.md`

35. [J] 时序为什么"不是赌一个概率"?25% margin 的工程含义是什么?唯一真要算概率的边缘情况是什么?
   `04-clocking-and-pipeline/global-clock-synchronization.md`

36. [F] 为什么同一工艺节点的两颗芯片可以有不同时钟频率?频率到底由什么决定?
   `04-clocking-and-pipeline/global-clock-synchronization.md`

37. [T] 从中间切一团逻辑云、插一个 register,为什么频率能翻倍?代价是什么?这是一笔怎样的交易?
   `04-clocking-and-pipeline/pipeline-register-insertion.md`

38. [J] "插 register 提频"在两种情况下失效。它们分别是什么?哪一个是 trade-off、哪一个是硬约束?
   `04-clocking-and-pipeline/pipeline-register-insertion.md`

39. [F] 在一个累加器(running sum)的反馈环中间插 register,会发生什么?为什么这是正确性问题而非性能问题?
   `04-clocking-and-pipeline/feedback-loop-clock-constraint.md`

40. [J] 反馈环不能插 register,那它还能怎么提频?为什么这把压力传回到了 final CPA 的进位结构选择?
   `04-clocking-and-pipeline/feedback-loop-clock-constraint.md`

41. [T] 累加精度 `acc_bits` 同时进入哪两个模型?为什么"高精度累加"在频率维度有隐藏代价?
   `04-clocking-and-pipeline/feedback-loop-clock-constraint.md`

42. [J] 一个 register + 一个 AND 门的极小环能跑 5–6 GHz。为什么这恰恰是低吞吐?把"吞吐 = 面积效率 × 频率"展开解释。
   `04-clocking-and-pipeline/frequency-is-not-throughput.md`

43. [T] "频率推到极致"和"batch 压到 1"为什么是同一张力的两个面孔?它们都落在延迟-吞吐平面的哪个角?
   `04-clocking-and-pipeline/frequency-is-not-throughput.md`

---

## 05-fpga-vs-asic(5 题)

44. [F] FPGA 第一颗成本和 ASIC 一次 tape-out 的量级各是多少?FPGA 存在的唯一理由是什么?
   `05-fpga-vs-asic/lut-mux-and-10x-overhead.md`

45. [T] "muxes all the way down" 是什么意思?配置一块 FPGA 本质上是在配置什么?
   `05-fpga-vs-asic/lut-mux-and-10x-overhead.md`

46. [F] 一个 4 输入 LUT 本质是一个怎样的 mux?为什么 4 输入是 sweet spot,而不是越多越好?
   `05-fpga-vs-asic/lut-mux-and-10x-overhead.md`

47. [J] 四路 AND 在 ASIC 上 3 个门、在 FPGA 上 ~32 个门。这 ~10× 的根本来源是什么?(不是"工艺差"或"时钟慢")
   `05-fpga-vs-asic/lut-mux-and-10x-overhead.md`

48. [J] 给定一个 workload 的改动频率和量产规模,你如何用 $10k / $3000万 两个 NRE 算出"ASIC 才划算"的量产门槛?
   `05-fpga-vs-asic/lut-mux-and-10x-overhead.md`

---

## 06-memory-discipline(5 题)

49. [F] 为什么 cache 是 CPU 运行时间非确定性的最大来源?命中与否取决于哪些运行时因素?
   `06-memory-discipline/cache-vs-scratchpad.md`

50. [T] scratchpad 如何用"两条不同的指令"获得确定性延迟?这把"数据放置决策"从运行时搬到了什么时候?
   `06-memory-discipline/cache-vs-scratchpad.md`

51. [J] 为什么说"确定性是更简单的起点,非确定性是 CPU 主动加进去的"?这对理解 Groq 全静态架构意味着什么?
   `06-memory-discipline/cache-vs-scratchpad.md`

52. [J] 为什么 AI 加速器适合 scratchpad(设计局部性)而 CPU 通用负载适合 cache(赌局部性)?分界线在哪个 workload 特征上?
   `06-memory-discipline/cache-vs-scratchpad.md`

53. [T] `ScratchpadAccess` 和 `CacheAccess` 在仿真里为什么必须走不同代码路径?各自需要哪些状态变量?哪些属于 RAM 域职责不该在 COMPUTE 模型里重复实现?
   `06-memory-discipline/cache-vs-scratchpad.md`

---

## 07-chip-organization(8 题)

54. [F] CPU core 比 GPU core 大,真正的大头不是 cache/RF/ALU,而是什么?GPU 有对应物吗?
   `07-chip-organization/cpu-vs-gpu-core-area.md`

55. [T] branch predictor 在解决什么物理矛盾?(提示:~5ns 取指 vs GHz 时钟)为什么 AI 负载能砍掉它几乎无损?
   `07-chip-organization/cpu-vs-gpu-core-area.md`

56. [J] 把 CPU→GPU/TPU 的专门化总结成一个统一逻辑。它砍掉了哪三类"AI 不需要的分母"?
   `07-chip-organization/cpu-vs-gpu-core-area.md`

57. [F] 芯片能耗的主体是动态功耗还是静态功耗?一个 bit 的能耗主要发生在什么时刻?
   `07-chip-organization/brain-vs-chip-power.md`

58. [J] 把 GPU 从 GHz 降到 MHz,能不能拿到脑那样的能效?降频省的是"总能量"还是"单次运算能效"?为什么这是两回事?
   `07-chip-organization/brain-vs-chip-power.md`

59. [J] "空转几乎不耗能"这个论证在什么工艺节点会失效?为什么先进节点的 leakage 会侵蚀降频的能效收益?
   `07-chip-organization/brain-vs-chip-power.md`

60. [T] "GPU = 一堆平铺的小 TPU" 这个等价怎么理解?SM 里的什么部件类比 TPU 的 MXU?
   `07-chip-organization/gpu-as-tiled-tpu.md`

61. [J] 粗粒度 TPU 用大阵列摊薄了 RF,代价是什么新瓶颈?细粒度 GPU 在 SM 内便宜,代价又是什么?splittable systolic array 想在这张表里得到什么?
   `07-chip-organization/gpu-as-tiled-tpu.md`

---

## 08-modeling-for-archax(4 题)

62. [J] 为什么计算/通信比应做成"可在任意聚合粒度(PE/array/core/chip)求值的派生量",而不只在顶层算一次?给一个 PE 粒度高、chip 粒度低的例子。
   `08-modeling-for-archax/modeling-insights.md`

63. [T] 把 7 条建模启示分别归到 archax 的哪个抽象落点(Execution IR / Capability / microarch M1 / Interaction / Topology-S1)?哪两条都落在 Interaction?
   `08-modeling-for-archax/modeling-insights.md`

64. [J] 时钟/流水层大多可在 M2 之下折叠,但有一个必须保留的例外。它是什么?为什么把反馈环当前馈处理会高估频率上限?
   `08-modeling-for-archax/modeling-insights.md`

---

## 跨章节综合题(自检主线是否真的贯通)

> 以下题目不挂单一文件,答不出来说明主线还没串成一条线。

- **A.** [J] 从一个逻辑门(p×q)到整片芯片的跨单元带宽,"大粒度摊薄固定成本"这个论点出现了至少三次。把这三级递进按顺序说出来。
  (`02 mux-cost` → `03 array-sizing` → `07 gpu-as-tiled-tpu`)

- **B.** [J] 全域共有三类"抬比值的根本动作":降低分子单位成本、放大粒度摊薄分母、把分母从运行时随机变确定。各举一个具体机制。
  (`01 compute-communication-ratio` §3)

- **C.** [T] 列出全表里所有被 ⚠️ 标注的常见误解,逐一说出"误解是什么、真相是什么"。
  (散落各篇的 ⚠️ 小节)

- **D.** [J] `bytes_moved`、`theoretical_macs`、`reuse_rate` 这三个量,如果只定义一次、在 Topology 每个聚合节点递归求值,如何天然实现"计算/通信比是任意粒度可求的派生量"?
  (`08 modeling-insights` 文末实现建议)
