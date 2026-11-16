# 系统事务如何跨越 BUS 与 NoC？

上级：[05 端点与系统集成](./README.md)

相关：[共享总线、Crossbar 与 NoC](../01-overview/bus-vs-noc-vs-crossbar.md)、[网络接口 NI](./ni-network-interface-design.md)、[事务拆分、顺序与完成](./transaction-ordering-and-completion.md)

<span id="noc-vs-bus-revisited"></span><span id="这页在回答什么问题"></span>软件提交一次任务后，控制接口、DMA、网络和目的端怎样接住彼此？分析这个问题时，要分别标出任务被接纳、数据到达、事务响应和软件观察到完成的时刻。

## 协议与网络可以组合

<span id="在-overview-里只回答了抽象区别"></span><span id="bus-更像控制骨架"></span><span id="noc-更像数据平面"></span>事务协议规定请求、响应及其顺序等语义；NoC 描述端点、交换资源和链路如何连接并传输消息。两者可以组合：AXI 请求可以由网络接口转换后经过 NoC，控制消息也可以通过网络承载。

一个芯片可以为低速寄存器和大数据搬运安排不同路径，也可以让它们共享部分网络。是否分离由带宽、时序、面积和可诊断性共同决定，不能仅凭“BUS”或“NoC”的名字判断。

## 一次任务经过哪些边界

<span id="真正关键的是交界处"></span>以下是**构造例**：软件将描述符放在内存中，通过 MMIO doorbell 通知 DMA；DMA 经 NI 和 NoC 读取、搬运数据，并按设备契约报告完成。其他设备可以采用不同流程。

| 阶段 | 事件 | 还不能推断什么 |
| --- | --- | --- |
| 提交 | 软件准备描述符，并按平台与设备规则交接可见性和所有权。 | 设备已经读取描述符。 |
| 启动 | doorbell 写被接口接纳；DMA 之后接收命令。 | 所有数据请求已经发出。 |
| 传输 | NI 封装请求，网络将其送往目标；返回消息经 NI 交付。 | 软件已经看到任务完成。 |
| 完成 | 设备按契约发布状态或通知；软件按适用规则读取结果。 | 通知本身能代替所有缓存同步或错误检查。 |

<span id="为什么这对-deterministic-npu-更敏感"></span>若计划要求固定的完成时间，还需要限制命令接纳、网络服务和目的端处理；固定路径本身不能保证 doorbell、DMA 和软件通知都在固定时间完成。

## 怎样定位边界问题

<span id="什么时候应该继续用-bus-思维"></span>若 doorbell 已被接纳但命令没有启动，检查命令队列、描述符可见性和设备状态。若网络包已到达但任务未完成，继续检查目标接收、响应匹配、错误与 completion 条件。

<span id="什么时候必须切到-noc-思维"></span>若请求或响应长期等待，再检查注入、路径共享、credit 和接收端。不同层的计数应使用同一时间窗口；链路利用率低本身不能定位根因。

<span id="建模启示"></span>模型可记录 `doorbell_accept`、`command_accept`、`packet_inject`、`response_deliver` 和 `completion_visible`。这些是观察点示例，不规定所有设备的实现顺序。具体缓存交接和中断闭环见 [BUS：Doorbell、Completion 与 Interrupt](../../BUS/04-microarchitecture-integration/doorbell-completion-interrupt-flow.md) 和 [DMA 一致性](../../../microarchitecture/DMA/wiki/02-fundamentals/noncoherent-vs-coherent-dma.md)。

<span id="一句话理解"></span>系统任务跨越多个接口；每个接口的接纳和完成只说明其契约规定的事件。
