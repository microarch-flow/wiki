# CIM、PIM、NMC：先看计算位置，再说明术语口径

<span class="micro-legacy-anchor" id="cimpimnmc-的严格区分"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>


上级：[问题、术语与分类](./README.md)

同一个缩写在不同论文中可能覆盖不同范围。判断方案时，先记录**计算在哪里、存储阵列是否参与求值**，再注明采用哪一套命名。不能仅凭标题中的 in-memory 就确定物理机制。


<span class="micro-legacy-anchor" id="本-wiki-的三条定义"></span>
<span class="micro-legacy-anchor" id="判定表"></span>

## 本专题采用的工作定义

| 本专题简称 | 计算位置与机制 | 要核对的证据 |
| --- | --- | --- |
| CIM | cell 或阵列访问路径直接参与部分求值 | wordline 激活、bitline、sense path 如何形成逻辑或数值结果 |
| PIM | memory die/bank 内加入与 cell 分离的处理单元 | 处理单元位置、局部存储访问、指令或命令接口 |
| NMC | memory die 外、靠近存储的处理逻辑 | base die、logic die、封装、模块或控制器侧的实际数据路径 |

这些是本专题用于缩小比较范围的工作定义，不是行业统一的互斥分类。[Mutlu 等的 A Modern Primer on Processing in Memory](https://arxiv.org/abs/2012.03112)（2025 年修订版）使用更广义的 PIM，讨论 processing-using-memory 与 processing-near-memory，包括利用存储结构和把逻辑放在存储附近的方案。引用该类文献时保留原术语，并补充位置和机制，不判定其命名错误。

## 两个不能省略的物理问题

第一，计算与存储 cell 是否在同一 die？若是，还要继续问：计算在独立处理单元内，还是借助阵列读写结构完成？若不是，需要记录距离由什么连接表示，例如 die 间接口、封装互连或内存通道。

第二，阵列到底参与了哪一步？普通 SRAM 读取权重后交给旁边 MAC，不因距离短就变成本文口径的 CIM。多行读出参与 bitwise、popcount、电流或电荷累积，则需要分析该阵列的求值机制。局部 accumulator 可以属于宏的结果路径，但单独存在 accumulator 不足以证明 array-native 计算。


<span class="micro-legacy-anchor" id="边界案例怎么判"></span>

## 边界案例

- **HBM base die 上的计算**：若独立于 memory die，本文记为 NMC；其他文献可使用广义 PIM。必须说明具体器件的计算位置，不能由 HBM 这个名称推断。
- **DRAM 内部机制**：RowClone 的行复制与 Ambit 的布尔逻辑是不同操作；前者主要改变数据移动路径，后者利用阵列感测求值。不要把二者都写成通用矩阵乘。
- **UPMEM**：[原始系统论文](https://www.usenix.org/system/files/atc21-nider.pdf)描述与 DRAM 集成的 DPU 及 MRAM/WRAM 数据移动。这里按独立处理单元记录为 PIM；DIMM 是交付形态，不是计算位置。
- **厂商平台**：同一平台可能组合 memory-die CU、host 控制器和近存逻辑。公司卡应分别标明各部分，避免把整个平台压成一个没有边界的标签。


<span class="micro-legacy-anchor" id="为什么这个区分重要"></span>

## 分类不能代替性能比较

位置更近可能减少某段移动，也可能引入转换、外围、校准、编程与同步成本。比较时还需统一数值精度、运算定义、工作负载、统计窗口和系统层级。

阵列宏的 TOPS/W 与整系统 token latency 回答不同问题。先说明证据覆盖到 cell、macro、chip 还是 system，再判断能否支持目标结论。[整体分类](./taxonomy.md)提供记录维度；[存储介质与求值方式](./two-axes-memory-and-paradigm.md)解释物理实现的两个坐标。


<span class="micro-legacy-anchor" id="本-wiki-的命名纪律"></span>
<span class="micro-legacy-anchor" id="常见误解"></span>

## 引用资料时怎样命名

先写来源自己的名称，再写可核实的位置与机制，最后给出本文归类。计算位置不明确时写“待核实”，不要从公司名、文件名前缀或 marketing 图推导。文件名中的旧前缀保留用于链接兼容，不作为技术结论。
