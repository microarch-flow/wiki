# 公开 NoC 案例：AMD Versal 如何承载一次读请求？

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)

相关：[网络接口 NI](../05-system-integration/ni-network-interface-design.md)、[事务拆分、顺序与完成](../05-system-integration/transaction-ordering-and-completion.md)、[Stall 分类与归因](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)、[缓存一致性通信案例](./coherent-access-and-noc.md)

本页用 AMD Versal Adaptive SoC Programmable NoC 的公开文档，看一次 AXI 读请求如何经过网络。它是**某一产品族的实现案例**，不是所有 NoC 的通用结构，也不是性能实测。以下依据 AMD 的 PG313 v1.1 文档；具体器件、端点类型与配置可能不同。

## 先认识公开组件

| 组件 | 公开职责 |
| --- | --- |
| NMU，NoC Master Unit | 位于请求发起侧，连接 AXI 发起端与 NoC；处理跨域、地址、事务转换和注入。 |
| NPS，NoC Packet Switch | 按目的和配置转发 packet，并对输出资源进行仲裁；交换节点之间采用 credit 流控。 |
| NSU，NoC Slave Unit | 位于目标侧，将网络消息与目标接口的事务相互转换；具体版本与连接的端点有关。 |

公开的逻辑路径可以概括为：**AXI 发起端 → NMU → 一个或多个 NPS → NSU → 目标端点**。读响应再经过网络返回请求侧。路径中的具体节点数量和配置取决于器件及映射，不应从这张概括图推断一条实际物理布线路径。[AMD：NoC Master Unit](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Master-Unit)；[NoC Packet Switch](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Packet-Switch)；[NoC Slave Unit](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Slave-Unit)

## 一次读请求经过什么

以 PG313 描述的典型读事务为例：

1. AXI 发起端向 NMU 提交读请求。NMU 处理应用侧与 NoC 侧的跨时钟及速率匹配，根据地址查找目标，并按所选配置转换和拆分请求。
2. NMU 为读请求分配内部跟踪信息，形成 NoC packet；VC 映射、仲裁和注入控制决定请求如何进入网络。
3. 一个或多个 NPS 根据目的和路由配置转发请求。目的 NSU 接收并转换请求，交给连接的目标端点。
4. 目标返回数据后，响应经 NSU 和网络回到 NMU。NMU 的读重排缓冲按适用的 AXI 顺序规则向发起端交付响应。

这是对公开典型路径的概括。拆分方式、缓冲条目、时钟和可用功能需要按具体 NMU／NSU 版本核对；不能将某一实例的数值当成 NoC 的通用参数。网络到达、AXI 数据交付和上层任务完成也是不同的观察事件。[AMD：Read Transactions](https://docs.amd.com/r/en-US/pg313-network-on-chip/Read-Transactions)；[AMD：NoC Master Unit](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Master-Unit)

## 怎样使用公开监控信息

PG313 说明 NoC 的 NMU、NSU、NPS 和内存控制器相关位置提供性能监控；NMU／NSU 的不同方向分别有监控。具体计数器、启用方式及适用范围以所用器件和工具版本为准。[AMD：NoC Performance Monitoring](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Performance-Monitoring)

例如，调查读完成时间上升时，可以先记录发起端请求、NMU 受理、网络相关计数、NSU 侧活动和目标服务的可用观测，再对齐相同流量类别与时间窗口。若发起端等待而某条链路利用率低，仍需检查注入限制、下游许可、目的端和依赖；低链路利用率本身不能定位原因。不同位置的计数对象可能不同，不能直接把请求数和数据字节数相减。

## 已知和未知的边界

上面的组件职责和读路径来自公开文档。本文没有给出某块板卡的实测流量、特定请求的实际路由、完整内部 RTL 或端到端延迟保证；这些不能由逻辑组件图推导。若要评价一个系统，仍需固定器件、端点、地址映射、时钟、流量和测量边界，再取得相应配置与观测数据。
