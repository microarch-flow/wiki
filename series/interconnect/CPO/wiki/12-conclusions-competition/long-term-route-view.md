# 长期主线与次主线判断

上级：[12 研究结论与竞争观察框架](./README.md)

相关：[CPO 分类框架](../01-overview/taxonomy.md)、[路线对比表](../02-industry/route-comparison.md)

## 主线判断：更深度的光电靠近集成是长期方向

长期看，更深度的 optical I/O 前移是高概率趋势。  
原因不是市场宣传，而是系统物理边界越来越明确：

- 长高速电通道越来越贵
- 面板密度越来越紧
- AI / HPC 的总带宽需求越来越大

所以“不再把所有光电转换都留在前面板”是长期方向。

## 但主线不等于单一形态

长期主线更可能是一个连续谱，而不是一个唯一答案：

- 更高端 pluggable 继续演进
- NPO / OBO 作为过渡或折中路线存在
- CPO 在高带宽密度场景更强
- chiplet optical I/O 可能在更广泛的 package-level system 中扩展

## 我当前更看好的主线

### 主线 A：AI / switch 场景中的平台化 CPO

代表逻辑：

- Broadcom
- NVIDIA

截至 2025-05-15，Broadcom [公告](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-third-generation-co-packaged-optics-cpo)对 TH5-Bailly 使用 volume-production 表述；NVIDIA 的 [2025-03-18 公告](https://nvidianews.nvidia.com/news/nvidia-spectrum-x-co-packaged-optics-networking-switches-ai-factories)描述平台目标和当时计划。两者不构成相同量纲的部署排名。

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

长期主线不是“所有东西都会变成同一种 CPO”，而是“光电转换会持续向 package 和 compute 更靠近，但会以多种集成深度并存的方式演进”。
