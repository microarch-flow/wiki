# Ultra Ethernet 与 UET：新的传输怎样与以太网配合？

上级：[系统集成与新协议](README.md)

Ultra Ethernet 涉及软件接口、端点传输、拥塞与链路增强。UET 是其中的传输协议，不能直接称作 RoCE 的新版本。理解它时，应先看分层职责，再核对具体 profile 和设备实现。

## 以 1.1 固定讨论范围

官方于 2026 年 10 月 12 日发布 UE 1.1。相对 1.0.3，更新包括 UE verbs 映射、Unified Local、网内集体通信及拥塞信号等。版本变化由[发布说明](https://ultraethernet.org/wp-content/uploads/sites/20/2026/10/20261026-3711-UE-Specification-1.1-release-notes.pdf)确认，不能把早期仅面向 scale-out 的概括直接沿用到 1.1。

## UET 内部怎样分工

| 子层 | 主要职责 |
| --- | --- |
| SES：语义子层 | 表达消息和远端访问等操作，衔接上层语义 |
| PDS：包交付子层 | 按所选模式提供包交付、可靠性和排序 |
| CMS：拥塞管理子层 | 组织拥塞信号、反馈与发送控制 |
| TSS：传输安全子层 | 提供所支持并启用的安全能力 |

PDS 支持不同交付模式，为多路径和包分散提供条件。这不意味着所有操作都可以任意乱序；操作语义和所选交付模式仍需匹配。软件接口支持也不等于应用无需配置就会使用新路径。[UE 1.1 第 2、3 章](https://ultraethernet.org/wp-content/uploads/sites/20/2026/10/UE-Specification-1.1.pdf)

## Profile 是互通判断的一部分

1.1 定义 Unified Local、AI Base、AI Full 和 HPC 四种 profile。Unified Local 面向本地 scale-up 场景，强调小型访问及线上效率。端点互通要求支持共同的 profile，并使用兼容的能力集合；安全等可选功能不能当作每个实现都具有的能力。规范第 3.3 节给出了要求矩阵。

以 IP/UDP 承载的路径与使用 UFH 的路径也应分别说明，不能把某一种头部大小套到所有 UE 流量。第 5 章涉及的链路增强，与应用完成语义仍属不同职责。

## 怎样评价一个实现

先记录规范版本、profile、可选功能、软件接口和实际设备，再问它能执行哪些操作、如何通知完成、怎样处理重排与拥塞。最后才比较指定负载下的性能。

反例：两张卡都标注支持 UE，但没有共同启用的 profile 或所需软件支持，不能只根据品牌描述断言应用互通。另一反例是把网内归约的通信量收益直接写成任务加速比；端点计算、网络竞争及不支持的算子仍需分析。

本页不宣布任何产品通过互操作认证。集体通信算法及卸载边界继续阅读[通信映射与卸载](../../SCALEUP/04-software-and-collectives/collective-mapping-and-offload.md)，具体支持和性能需要设备资料与实验。
