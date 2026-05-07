# RAM 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[DRAM 家族对照：DDR / LPDDR / GDDR / HBM](../03-ddr-protocol-families/ddr-lpddr-gddr-hbm-comparison.md)

## 为什么先做分类

学习 RAM 时，最容易把下面几种对象混为一谈：

- 存储单元
- 阵列组织
- 接口协议
- 产品家族
- 系统位置
- 封装形态

更稳妥的方式是按正交维度拆开。

## 维度一：按存储单元分

- `SRAM`：6T 或变体单元，不刷新，速度快
- `DRAM`：1T1C 单元，需要刷新，密度高

重点：

单元结构决定面积、速度、是否刷新，以及它更适合做 cache 还是 main memory。

## 维度二：按阵列与访问方式分

- SRAM 阵列：按地址直接读写
- DRAM 阵列：按 `bank -> row -> column` 组织，先激活行再读列

重点：

DRAM 的行缓冲和页命中，是理解实际延迟和带宽的关键。

## 维度三：按接口和标准分

- DDR
- LPDDR
- GDDR
- HBM

重点：

这些名字大多不是新的存储物理原理，而是针对不同系统目标做出的 DRAM 接口和封装路线分化。

## 维度四：按系统角色分

- register file / L1 / L2 / L3：通常是 SRAM
- main memory：通常是 DDR / LPDDR
- graphics / accelerator memory：通常是 GDDR / HBM
- local scratchpad / on-chip SRAM：AI 加速器常见

重点：

系统位置决定“更看重延迟、带宽还是容量”。

## 维度五：按封装形态分

- DIMM
- PoP / MCP
- package-on-substrate
- 2.5D interposer
- 3D stack

重点：

封装不只是装配问题，而是直接决定互连长度、I/O 密度和每比特能耗。

## 一句话记忆法

先问“数据存在哪里”，再问“怎么访问”，再问“怎么对外传输”，最后问“它在系统里扮演什么角色、以什么封装出现”。
