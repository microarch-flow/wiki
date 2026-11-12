# NVIDIA 深卡

上级：[11 重点公司深卡](./README.md)

相关：[NVIDIA：AI 网络牵引型 CPO 观察框架](../02-industry/company-cards/nvidia-ai-network-cpo.md)

## 它控制哪一段

NVIDIA 在 CPO 生态里的核心位置，是 `AI 系统需求牵引方 + 网络平台主导方`。

它最强的不是单独某个光学器件，而是：

- AI 工厂规模需求
- scale-up / scale-out 网络定义
- GPU 与 network fabric 协同

这使它在 CPO 里的权重，更多来自“系统问题有多痛”，而不是“某个单点器件有多强”。

## 为什么现在值得跟踪

NVIDIA 在 [2025-03-18 公告](https://nvidianews.nvidia.com/news/nvidia-spectrum-x-co-packaged-optics-networking-switches-ai-factories)发布 `Spectrum-X Photonics` 和 `Quantum-X Photonics`，并列出生态伙伴。

这说明它已经不再只是笼统谈 photonics，而是在公开定义：

- 哪些平台会用
- 哪些生态伙伴参与
- 这条路线服务的就是 AI factory 级系统

## 它的公开技术路线

从官方公开材料看，NVIDIA 的重点不是传统“交换机模块升级”，而是：

- Spectrum-X Photonics 面向 Ethernet；Quantum-X Photonics 面向 InfiniBand
- 百万 GPU AI factory 是厂商提出的平台规模目标，不等于已部署集群

任务收益取决于实际部署的拓扑、可用端口、协议和负载；公告本身不能确定任务时延。

## 它的公开合作关系

在 `2025-03-18` 官方材料中，NVIDIA 公开点名的伙伴包括：

- TSMC
- Coherent
- Corning
- Foxconn
- Lumentum
- SENKO
- SPIL
- Sumitomo Electric
- Fabrinet

这组名单的意义很强，因为它横跨了：

- manufacturing
- optics / laser
- connector / fiber
- packaging / assembly

说明 NVIDIA 的路径是整生态协同，而不是孤立产品。

## 它的商业模式和客户入口

NVIDIA 的客户入口是：

- AI infrastructure buyers
- hyperscalers
- 构建大规模 AI 集群的系统客户

这使它的 adoption 逻辑和一般数据中心网络不完全相同。  
只要系统收益足够大，它就更有可能推动更复杂的集成方式。

## 它的最大风险点

- 路线复杂度极高，对多家伙伴协同要求很高
- 如果现场可维护性或量产爬坡不顺，会拖慢部署
- 这条路线高度依赖 AI factory 级场景成立，不一定普适

## 你接下来最该看的观察指标

1. 是否有更多公开客户部署信号
2. NVIDIA 是否持续强化 photonics 作为 AI factory 核心组成的表述
3. 生态伙伴是否继续扩大，还是开始收敛到更稳定的供货结构

## 一句话总结

NVIDIA 在 CPO 里的意义，是把 photonics 从“网络技术路线”上升成“AI 工厂系统扩展路线”。
