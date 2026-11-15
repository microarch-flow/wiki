# 存储系统集成与选型

上级：[存储系统](../README.md)

## 本专题回答什么问题

器件接口、计算需求和物理实现如何组合成一个可用的存储系统？本专题从工作负载和产品约束出发，讨论模块、封装、外存选型及扩展路径。它关注系统层面的选择，不把接口名称当作性能、功耗或成本的完整答案。

先确认比较对象：同一工作负载、容量、吞吐和时延目标下，候选系统如何连接内存，软件如何使用数据，以及实现、测试和维护需要付出什么代价。不同配置可能得到不同结论。

## 阅读顺序

1. [不同计算系统如何选择存储层次](./why-systems-choose-different-memory.md)：从 MCU、CPU、GPU、NPU 的需求出发，不按处理器类别硬编码答案。
2. [存储模块、封装与集成](./packaging/README.md)：依次了解 DIMM/SODIMM、PoP/MCP、HBM 互连与成本。
3. [NPU 外存选型：HBM 与 LPDDR](./hbm-vs-lpddr-for-npu.md)：用容量、流量和产品约束比较候选方案。
4. [存储扩展与近存计算](./future-packaging-cxl-near-memory.md)：区分 CXL 接口、计算位置和封装集成。

只想比较 NPU 外存，可先读第 3 篇，再按需回看第 2 篇。研究多级内存和计算卸载时，可直接读第 4 篇。

## 与相邻专题的分工

- [存储层次与系统角色](../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md)解释各层的职责和数据交接；[NPU 数据路径](../01-memory-hierarchy/04-npu-case/README.md)解释片上缓冲、搬运和复用。
- [DRAM 命令与接口](../03-dram/protocols/README.md)解释器件接口与协议；本专题讨论这些接口如何在板级和封装级实现。
- [峰值、实际与有效带宽](../01-memory-hierarchy/03-performance/effective-bandwidth-vs-peak.md)定义测量口径。本专题用这些口径评估选型。
- [HBF 高带宽闪存](../05-hbf/README.md)研究 NAND、接口及软件协作。HBF 和 HBM 的存储介质及访问语义不同，不能仅因都采用堆叠或宽接口而等同。
- [FAB 的 HBM 封装案例](../../chip-development/FAB/wiki/04-back-end-packaging/hbm-as-case-study/README.md)进一步解释制造、测试和实现。
