# Ayar Labs 深卡

上级：[11 重点公司深卡](./README.md)

相关：[Ayar Labs / Alchip / TSMC 主线](../10-company-ecosystem/partnership-map.md)

## 它控制哪一段

Ayar Labs 的核心位置是 `optical I/O chiplet + external light source 路线定义者`。

它控制的关键不是交换平台，而是：

- TeraPHY optical I/O chiplet
- SuperNova light source
- optical I/O subsystem 架构

## 为什么现在值得跟踪

Ayar Labs 是当前公开路线里最鲜明地把：

- chiplet optical I/O
- remote/external light source
- package-level optical interconnect

组合成清晰产品叙事的公司之一。

截至 `2025-09-11` Alchip 官方新闻稿和 Ayar Labs 官方产品页，这条路线已经和：

- TSMC COUPE
- UCIe
- AI accelerator packaging

这些关键词绑得非常紧。

## 它的公开技术路线

公开材料显示，Ayar Labs 的路线核心是：

- TeraPHY：光 I/O chiplet
- SuperNova：multi-wavelength remote light source

这条路线的逻辑是：

- 把 optical I/O 做成可被 package 接纳的 chiplet
- 把热敏感的光源尽量从最热封装域拿出去

这比传统“做一个更高级光模块”的逻辑更像下一代系统 I/O 子系统。

## 它的公开合作关系

截至公开官方材料，可以明确看到的关键关系包括：

- Alchip：design and packaging collaboration
- TSMC：COUPE / SoIC / advanced packaging ecosystem
- AMD：投资关系，且截至 `2025-05-28` AMD 也在加强 photonics 能力
- NVIDIA、Intel、GlobalFoundries 等投资/生态背景在 Ayar Labs 官方公开材料中可见

这里最重要的不是“名单好看”，而是说明 Ayar Labs 的路线与主平台生态存在明确耦合。

## 它的商业模式和客户入口

Ayar Labs 的商业模式更像：

- 提供 optical I/O chiplet 子系统
- 进入 AI accelerator、switch、XPU fabric 等高性能封装场景

它的客户入口不一定像 Broadcom 或 NVIDIA 那样直接控制整个平台，但它有机会成为下一代 package I/O 的关键部件提供者。

## 它的最大风险点

- 对主平台厂商和 advanced packaging 生态依赖很强
- 如果客户不接受新的 package I/O 复杂度，adoption 会慢
- 需要证明的不只是链路能跑，而是 volume manufacturability 和 long-term reliability

## 你接下来最该看的观察指标

1. 是否出现更多量产级 customer announcement
2. 是否继续与 TSMC / Alchip 等生态深入绑定
3. 是否从 AI accelerator 延伸到更广的 scale-up / scale-out 互连场景

## 一句话总结

Ayar Labs 的关键价值，是把 photonics 不再定义成模块，而是定义成 package-level I/O 子系统。
