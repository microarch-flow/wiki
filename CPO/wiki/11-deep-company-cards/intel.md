# Intel 深卡

上级：[11 重点公司深卡](./README.md)

相关：[Intel：硅光平台型 CPO 观察框架](../02-industry/company-cards/intel-silicon-photonics.md)

## 它控制哪一段

Intel 在 CPO 生态里的核心位置，是 `volume-proven silicon photonics platform + OCI chiplet 路线方`。

它控制的关键包括：

- 高量产成熟度的 silicon photonics 平台
- PIC 与 on-chip laser 集成能力
- 面向 compute-side optical I/O 的 `OCI` 路线

这意味着 Intel 的价值，不只是“理解硅光”，而是“把硅光做成已有量产历史的平台能力”。

## 为什么现在值得跟踪

截至 `2026-05-04` 的 Intel 官方 Silicon Photonics 页面，Intel 明确公开了三层能力：

- `Optical Compute Interconnect (OCI)`
- `High-Speed Photonics Components`
- `High Volume-proven Silicon Photonics Platform`

其中最关键的公开信号包括：

- OCI chiplet 第一代支持 `4 Tbps` 双向带宽
- 官方表述其可与 `CPU / GPU / IPU / SoC` 共封装
- 官方强调已累计出货 `800 万+ PIC` 与 `3200 万+ on-chip lasers`

这说明 Intel 的路线不是纯概念演示，而是试图把现有量产硅光平台延伸到更深度的 package optical I/O。

## 它的公开技术路线

Intel 当前最值得跟踪的公开路线是：

- 继续强化高量产成熟度的 silicon photonics 平台
- 通过 `OCI chiplet` 把 optical I/O 前移到 compute package
- 采用集成 `DWDM lasers + SOA + PIC + EIC` 的方式，强调无需 external laser

这一点和 Ayar Labs 的 remote light source 路线形成了非常清晰的对照。

所以研究 Intel 时，关键不是问“它会不会做 CPO”，而是问：

- `integrated laser + OCI chiplet` 这条路线能否成为长期主线之一

## 它的公开合作与生态关系

截至当前公开材料，Intel 在本套 wiki 中更重要的不是密集的生态伙伴名单，而是：

- 自有 silicon photonics platform
- 与下一代 compute package 的共封装适配表述
- 在 hyperscale networking 中已有的量产经验

Intel 的优势更多来自平台和工艺积累，而不是“生态展示最热闹”。

## 它的商业模式和客户入口

Intel 的客户入口主要在：

- data center networking optics
- compute platform interconnect
- silicon photonics component and platform supply

这意味着它既可能继续是：

- pluggable optics 时代的重要 silicon photonics 平台方

也可能演进成：

- compute-side OCI / package optical I/O 的关键路线方

## 它的最大风险点

- integrated laser 路线在热、可靠性和 package-level adoption 上是否比 remote laser 更有长期优势，仍需观察
- Intel 在更广 CPO 主平台竞争里的话语权，不等于其在硅光平台上的话语权会自动转化
- 如果主流平台由其他公司定义，Intel 可能更强于“能力供给”，未必总是最强于“平台 adoption 入口”

## 你接下来最该看的观察指标

1. Intel 是否继续把 `OCI chiplet` 从 demo 往更明确产品化推进
2. 官方是否出现更多与 next-gen compute package 深度绑定的信号
3. `integrated laser` 路线是否继续被强化，而不是转向 external laser 折中

## 一句话总结

Intel 在 CPO 里的最大看点，是它是否能把“已验证的大规模硅光平台能力”进一步转化成 compute-side optical I/O 的长期主线。
