# 存内与近存计算

<span class="micro-legacy-anchor" id="cim-wiki"></span>
<span class="micro-legacy-anchor" id="这份-wiki-在回答什么问题"></span>
<span class="micro-legacy-anchor" id="全-wiki-的两个锚点"></span>
<span class="micro-legacy-anchor" id="从哪里开始"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>


本专题讨论计算进入存储阵列、memory die 或存储附近之后，数据路径、数值误差、软件接口和系统成本怎样变化。CIM、PIM、NMC 的含义随文献而异，先核对位置与机制，再说明采用的口径。

## 入口与边界

从《[同一个点积，挪到存储旁边或阵列里面怎么算？](./01-overview/cim-pim-nmc-taxonomy.md)》开始。跟着两个权重看它们走到哪个运算单元，再判断哪一段搬运发生了变化。[介质与求值方式](./01-overview/two-axes-memory-and-paradigm.md)负责物理坐标；[路线矩阵](./02-memory-technologies/memory-tech-comparison-matrix.md)负责查阅。公司和论文是机制的证据与案例，不是另一套平行分类。

想看阵列怎样动手算，先沿[一列 SRAM 的两行读出](./02-memory-technologies/sram-cim-foundation.md)找出一个逻辑位，再沿[另一种 SRAM 的电荷共享和数字读出](./02-memory-technologies/sram-cim-deep-dive.md)跟踪一个部分和。

如果权重仍由 DRAM 正常读出，谁来做乘加？先跟踪[一对 bank 旁的处理单元](./02-memory-technologies/dram-pim-foundation.md)，再看[不同组的局部结果怎样合成主机需要的答案](./02-memory-technologies/dram-pim-deep-dive.md)。


<span class="micro-legacy-anchor" id="十章地图"></span>

## 阅读顺序

1. [问题、术语与分类](./01-overview/README.md)
2. [存储介质与计算路径](./02-memory-technologies/README.md)
3. [阵列求值与信号转换](./03-compute-paradigms/README.md)
4. [电路、外围与计算宏](./04-circuit-and-macro/README.md)
5. [架构与系统集成](./05-architecture-and-system/README.md)
6. [编译、量化与运行时](./06-software-stack/README.md)
7. [工作负载与映射](./07-workloads/README.md)
8. [产业、产品与公司案例](./08-industry-and-products/README.md)
9. [研究进展与论文案例](./09-research-frontier/README.md)
10. [查阅资料与研究模板](./10-reference/README.md)

## 如何使用产业与研究资料

公司卡保留资料日期、产品对象与公开证据；论文卡说明机制、实验条件和范围。产品状态以卡片标注的证据日期为准；宏级峰值与整系统结果分别比较。待核实的数据保留标记。

全部文章见[知识地图](./SUMMARY.md)。普通 PE 的权重驻留与阵列路径求值的区别，可对照[systolic 逐拍例子](../04-parallel-execution/why-systolic-array.md)。
