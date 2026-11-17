# 长期主线与次主线判断

上级：[12 研究结论与竞争观察框架](./README.md)

相关：[CPO 分类框架](../01-overview/taxonomy.md)、[路线对比表](../02-industry/route-comparison.md)

## 主线判断：更深度的光电靠近集成是长期方向

将 optical I/O 靠近主芯片是一种值得持续跟踪的系统选择。以下是研究假设，不是对未来份额的预测：

- 长高速电通道越来越贵
- 面板密度越来越紧
- AI / HPC 的总带宽需求越来越大

这些约束可能使部分系统采用更近的光电转换；具体方案仍需与持续演进的可插拔模块及电互连按相同边界比较。

## 但主线不等于单一形态

长期主线更可能是一个连续谱，而不是一个唯一答案：

- 更高端 pluggable 继续演进
- NPO / OBO 可作为不同系统的长期或阶段性选择
- CPO 可能适用于部分受带宽密度或电通道约束的场景
- chiplet optical I/O 可能在更广泛的 package-level system 中扩展

## 我当前更看好的主线

### 主线 A：AI / switch 场景中的平台化 CPO

代表逻辑：

- Broadcom
- NVIDIA

Broadcom 对 TH5-Bailly 给出量产声明，并在 2025-10-08 声明 TH6-Davisson 出货；NVIDIA 在 2026-05-31 声明 Spectrum-X Ethernet Photonics 进入生产。日期和来源见[公司来源表](../18-sources-and-updates/company-ecosystem-sources.md)。这些厂商声明不能构成客户现场端口数排名。

### 主线 B：package optical I/O 子系统化

代表逻辑：

- Ayar Labs 一类路线

这条线的潜力在于，它可能不只服务交换机，还可能进入更广义的加速器和 scale-up fabric。

## 其他可并存的选项

包括：

- 更近的 near-package optics
- 更强的 pluggable + coherent / high-speed evolution
- 可选的 external laser 和 serviceability 设计

光源位置与光电转换位置互相独立：平台化 CPO 也可用外置激光。是否便于维护取决于可替换单元、供光和分光路径；不能由光源位置直接决定链速或商业顺序。

## 一句话判断

多种集成位置可能并存；是否继续向封装内靠近，应以接口、功耗、制造和客户维护数据持续检验。
