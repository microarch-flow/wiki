# 功耗、能量与面积建模：性能收益需要付出什么？

<span id="power-area-modeling"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[07 Evaluation Methodology](./README.md)

相关：[路由器面积与功耗](../02-router-microarchitecture/router-power-area-tradeoff.md)、[拓扑与物理实现](../03-topology/topology-physical-realization.md)、[架构探索与实验设计](./architecture-exploration-loop.md)

<span id="这页在回答什么问题"></span><span id="性能最优不等于可实现"></span>比较网络时，除了完成时间和吞吐，还要检查实现需要多少面积、能量、功率及布线资源。本篇关注**全网计数和工作负载**；单个 router 的结构关系见第二章。

## 先确定成本边界

<span id="noc-的面积和功耗大头通常在哪里"></span>按实际实现列出 router 的 buffer、crossbar、allocator 和控制，链路及驱动、可能的流水寄存器，以及 NI。不同设计的主要成本可能不同。时钟、空闲活动和泄漏也应按所选边界计入；跨 die PHY 若属于比较范围，要单独列明。

逻辑 bit 数、网络连边数和线长是有用的输入，但不是直接测得的硅面积。存储宏、端口、布局、工艺、电压和目标频率都会影响实现。成本表应保证各项不重不漏：若 buffer 成本已经包含各 VC 的存储，就不能再次把相同存储作为独立 VC 面积加进去。

## 从操作次数估算能量

<span id="为什么这一页要和-workload-一起看"></span>对每种操作 i，令 N<sub>i</sub> 是观察窗口内的次数，E<sub>i</sub> 是对应假设下每次操作的动态能量：

> E<sub>dynamic</sub> = Σ(N<sub>i</sub> × E<sub>i</sub>)；P<sub>average</sub> = (E<sub>dynamic</sub> + E<sub>leakage</sub>) / 窗口时长。

例如只为演示单位，假设 200 次 buffer 读写各 2 pJ、100 次 crossbar 穿越各 1 pJ、100 次链路传输各 3 pJ、100 次控制操作各 0.5 pJ。动态能量为 **850 pJ**。若另假设窗口 10 ns、泄漏功率恒为 10 mW，则泄漏能量为 100 pJ，总能量为 950 pJ，平均功率为 **95 mW**。本例省略其他时钟和空闲动态能量；数值只是构造假设，不是器件参数。

统计多播时，要根据实际复制点分别计算源注入、各边传输及各次 buffer/crossbar 操作。数据值和翻转率也可能改变单次动态能量；一次 flow 的逻辑 payload 不能直接当作全网操作次数。

## 改变参数时，哪些条件一起变化

<span id="常见的一阶-trade-off"></span>

| 变化 | 可能的收益 | 需要同时检查 |
| --- | --- | --- |
| <span id="加深-buffer"></span>加深 buffer | 吸收部分突发或信用往返等待 | 存储组织、读写活动和下游服务；不能消除持续过载。 |
| <span id="增加-vc"></span>增加 VC | 允许独立排队，可能缓解 HOL | 总容量固定还是每 VC 深度固定，以及仲裁和隔离规则。 |
| <span id="提高-radix"></span>增加端口 | 为某些拓扑提供更多直接连接 | crossbar、仲裁、线长和频率；端口更多本身不保证 hop 变少。 |
| <span id="加宽-link"></span>加宽链路 | 在接口和频率允许时提高原始传输能力 | 内部 flit 是否变化、每拍能发多少、编码开销和目的端速率。 |

固定每拍一次传输且频率不变时，W bit 物理链路的原始位速率为 W×f；有效 payload 速率还取决于包格式和空拍。若链路加宽导致频率或接口规则变化，不能直接按位宽比例推断吞吐。

## 从粗估到可比较的结果

<span id="什么时候需要粗模型就够"></span>早期可以使用明确标注的相对成本或范围筛选候选。比较时固定活动统计方式及功耗边界，分别展示性能、面积和能量，再检查受预算约束的非支配方案。不同成本模型可能改变排序。

[ORION 2.0 原论文](https://dspace.mit.edu/entities/publication/3b64a184-2f8c-4a20-8e5f-74e6a80f478f)介绍了互连的功耗和面积模型；[CACTI](https://github.com/HewlettPackard/cacti)提供存储和互连等估算能力。它们的输出依赖模型版本和输入，不能直接当作具体芯片的实测结果。

<span id="一句话理解"></span><span id="建模启示"></span>记录工作负载产生了多少次操作，再用适用的实现数据估算成本；性能改善是否值得，应与实际预算和模型不确定性一起判断。
