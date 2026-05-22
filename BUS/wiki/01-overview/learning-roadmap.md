# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[BUS Wiki 首页](../README.md)、[知识地图](../SUMMARY.md)、[按目标学习 BUS](./goal-oriented-navigation.md)

## 这页在回答什么问题

如果要系统掌握 BUS，为什么学习顺序应该按概念依赖推进，而不是平均阅读 AXI、AHB、APB、TileLink 这些协议名。

## 路线图和目标导航的分工

这页给默认学习闭环：按概念依赖从问题定义读到系统分析。它回答“先学什么，后学什么，为什么这个顺序不会把因果关系读反”。

[按目标学习 BUS](./goal-oriented-navigation.md) 用来跳读。等你已经知道自己是在做 RTL 适配、SoC bring-up、DMA 性能分析、故障复盘或方案评审，再按目标路径裁剪阅读范围。

## 第一层：先建立问题边界

起点是 [BUS 在解决什么问题](./problem-statement.md) 和 [BUS 分类框架](./taxonomy.md)。这两页不是前言，而是后面所有判断的坐标系：BUS 是共享资源上的事务组织层，分类时要看系统角色、拓扑、事务能力、顺序模型和共享语义。

接着读 [BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)。这一步的目标不是背定义，而是建立边界判断：什么时候点到点连接足够，什么时候共享 BUS 的可控复杂度更合适，什么时候全局仲裁和布线已经逼近上限，需要 NoC 这类更分布式的组织。

第一轮不要急着读 TileLink、coherent interconnect 或完整 DDR/IOMMU 路径。它们很重要，但会把问题从“BUS 在组织什么”提前拉到“某类高级系统如何扩展 BUS 语义”，容易打散主线。

## 第二层：事务语义先于协议机制

真正进入 BUS 细节时，先读 [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)。一次 BUS 访问不是“地址加数据”，而是 request 被接受、数据阶段推进、response 返回、顺序约束生效的生命周期。

然后读 [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)。多个 transaction 共享资源时，性能和正确性问题会落在谁先走、谁必须等、下游如何反压上。没有这一层，AXI outstanding、APB 简化、bridge FIFO、QoS 和 timeout 都会像孤立特性。

[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md) 可以作为这一层的扩展阅读。它回答理论带宽为什么不等于有效吞吐，以及 burst 为什么既能摊薄开销，也会改变占路时间和尾延迟。

## 第三层：把协议看成设计取舍的落点

到这里再读 [AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)。协议不是新旧排序，而是不同约束的落点：APB 收缩并发换简单控制面，AHB/AHB-Lite 保持中等复杂度和较强顺序性，AXI 用通道拆分和 outstanding 换吞吐与并发。

第一轮只需要再读两篇 AXI 核心机制：[AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md) 和 [AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)。它们回答 AXI 为什么复杂、复杂度换来了什么、哪些状态必须被实现和建模。

Burst、WSTRB、response error、AHB/APB 深化、TileLink、coherence 都应放到第二轮。第一轮的目标不是穷尽协议细节，而是能解释“为什么协议要把事务拆开，以及拆开之后系统付出了什么代价”。

## 第四层：把协议放回系统路径

协议机制只有放回真实路径里才会暴露代价。一个 AXI master 到 DDR controller 的路径，不只是“发 AXI read”；中间可能经过 decoder、arbiter、crossbar、bridge、CDC、width adapter、IOMMU/SMMU、memory controller queue 和 return path。每一层都可能改变 latency、bandwidth、ordering 和 error 语义。

第一轮系统阅读只需要抓两篇：[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md) 和 [CPU、DMA、外设与内存之间的总线路径](../04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)。前者把 fabric 拆成 decoder、arbiter、mux/crossbar、FIFO、bridge 等建模对象；后者把 BUS 放回 CPU、DMA、peripheral、memory 的完整路径。

当你开始追具体问题，再进入 bridge/CDC、DMA、IOMMU、DDR、doorbell/completion 等专题。这样读的 trade-off 是第一轮不会覆盖所有细节，但能先建立“哪里排队、哪里回压、哪里改变顺序、哪里产生错误”的系统视角。

## 第五层：用性能调试和案例校验

最后读 [带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)。这时性能指标不会再是孤立数字，而能回到 transaction lifecycle、仲裁位置、buffer 深度和返回路径上解释。

再读一个案例即可收束第一轮：[AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)。案例不是替代理论的捷径，而是检验你能不能把路径、事务、仲裁、回压、错误和软件可见性串起来。

如果你的目标是故障定位，再转到 [Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md) 和 [AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)。如果你的目标是 AI 芯片互连选型，再看 [MCU / SoC / AI 芯片中的 BUS 对照](../06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md) 和 [AI 芯片里的 BUS vs NoC](../06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)。

## 最小闭环

1. [BUS 在解决什么问题](./problem-statement.md)
2. [BUS 分类框架](./taxonomy.md)
3. [BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)
4. [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)
5. [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)
6. [AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)
7. [AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)
8. [AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)
9. [互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)
10. [CPU、DMA、外设与内存之间的总线路径](../04-microarchitecture-integration/dma-cpu-peripheral-memory-path.md)
11. [带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)
12. [AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 一句话理解

学习 BUS 的有效顺序不是平均阅读协议名，而是沿着“共享资源问题、事务拆分、仲裁与回压、协议取舍、系统路径、性能案例”这条概念依赖链推进。

## 建模启示

这条路线图对应一条建模递进路径。第一层只需要把系统抽象成 master、target 和共享路径；第二层开始显式建模 transaction lifecycle，包括 request accepted、target service、response generated、response consumed；第三层引入协议能力差异，例如 burst、outstanding、读写通道分离和顺序规则；第四层把 bridge、CDC、IOMMU、DDR controller 和 return path 放进路径模型；第五层才讨论 counters、trace、waveform 和 case study。

如果只关心早期性能估算，可以在第一层和第二层停下，把协议细节折叠成服务时间、并发度、队列和 backpressure。只要进入 AXI 级机制或调试定位，就必须继续保留 ID、burst、response、ordering、bridge buffer 和错误路径。学习顺序和建模粒度必须一致：概念还没拆清时，不要急着给模型填协议字段；模型已经要解释长尾延迟和 hang 时，也不能再用单一平均延迟事件替代 transaction lifecycle。
