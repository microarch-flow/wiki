# DDR、LPDDR、GDDR、HBM：接口家族如何比较

上级：<span id="ddrlpddrgddrhbm四种-dram-协议的-trade-off-全景图"></span>[DRAM 命令与接口](./README.md)

相关：[系统存储选型](../../06-system-integration/why-systems-choose-different-memory.md) · [DDR 代际](./ddr-generation-evolution.md)

## 这页在回答什么问题

四种 DRAM 协议的 trade-off 全景图应怎样用于系统选型？先看目标和集成约束，再核对具体器件；家族名不能代替容量、功耗或带宽规格。

## 四类接口的目标与代价

| 家族 | 常见设计目标 | 比较时要核对 |
| --- | --- | --- |
| [DDR](./ddr-generation-evolution.md) | 通用主存、容量与模块生态。 | 通道及 DIMM 数、容量、速率、控制器和板级限制。 |
| [LPDDR](./lpddr-low-power-mobile.md) | 在适用系统中兼顾工作与待机能耗。 | 工作状态、退出时间、封装或模块形态、实际负载。 |
| [GDDR](./gddr-graphics-bandwidth.md) | 在外置存储接口上提供较高带宽。 | 引脚速率、总线宽度、信号完整性、功耗与板级布局。 |
| [HBM](./hbm-stacked-wide-io.md) | 通过堆叠和宽接口提供高带宽密度。 | stack 数与代际、封装、散热、容量和成本。 |

这些是常见侧重，并非产品的排他用途。例如 LPDDR 有可拆卸模块，HBM 不同代际的接口宽度也不同。不同系统的空闲比例、并发和访问粒度会改变结果。

先排除容量、封装、可靠性或供货不满足要求的候选，再比较满足条件的候选在目标工作负载下的延迟、有效带宽、能耗与总成本。理论峰值只说明边界；[有效带宽](../../01-memory-hierarchy/03-performance/effective-bandwidth-vs-peak.md)和[系统选型](../../06-system-integration/why-systems-choose-different-memory.md)说明测量与整体路径。

## 一句话理解

接口家族提供不同设计起点；最终比较对象是符合约束的具体系统。

## 建模启示

保留每个候选的位宽、数据率、通道、容量、时序和功耗状态；用一致流量与统计窗口比较，并注明封装、温度和成本来源。
