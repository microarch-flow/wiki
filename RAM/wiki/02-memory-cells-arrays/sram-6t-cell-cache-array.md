# SRAM 6T 单元与 Cache 阵列

上级：[02 存储单元与阵列结构](./README.md)

相关：[SRAM vs DRAM 对照](./sram-vs-dram.md)、[从 SRAM 到 HBM 的系统分层](../04-system-architecture/cache-dram-hbm-system-view.md)

## SRAM 单元是什么

SRAM 的典型基本单元是 `6T`：

- `4 个晶体管` 组成两个交叉耦合反相器，用来稳定保存状态
- `2 个访问晶体管` 控制读写接入

它不是靠电容暂存电荷，而是靠晶体管构成的双稳态回路维持 `0/1`。

## 为什么 SRAM 不需要刷新

只要供电存在，交叉耦合结构就能持续保持状态，因此：

- 不需要像 DRAM 那样周期 refresh
- 读写路径更直接
- 更适合作为低延迟工作存储

这也是 `Static RAM` 里“Static”的含义。

## 为什么 SRAM 快

SRAM 适合做 CPU / GPU / AI 加速器片上缓存，根本原因在于：

- 访问不需要 activate / precharge 这种行级动作
- 不依赖微弱电荷感测
- 可直接按照地址读写阵列
- 常与计算逻辑同 die 集成，物理距离短

所以 SRAM 的价值不只是“单元快”，而是它能支持更短的系统访问路径。

## 为什么 SRAM 贵

SRAM 的主要代价在面积：

- 单 bit 需要更多晶体管
- 单元面积明显大于 DRAM
- 容量一扩大，die 面积和成本迅速上升

因此 SRAM 适合做：

- register file
- L1 / L2 / L3 cache
- on-chip scratchpad

但不适合承担通用 GB 级主存角色。

## SRAM 阵列在系统里的真实意义

从架构角度看，SRAM 不是“比 DRAM 快一点的存储器”，而是：

- 用面积换低延迟
- 用容量限制换带宽确定性
- 用片上集成换功耗和时序可控性

这也是为什么现代系统始终保持“少量 SRAM + 大量 DRAM/HBM”的分层。

## 一句话理解

SRAM 的本质是 `用更多晶体管面积，换不刷新、低延迟、可直接寻址的片上工作存储`。
