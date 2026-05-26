# NI Network Interface Design

上级：[05 System Integration](./README.md)

相关：[Packet Flit Phit Hierarchy](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)、[Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)、[DMA Engine NOC Interaction](./dma-engine-noc-interaction.md)

## 这页在回答什么问题

这页回答：为什么 `NI` 不是 NoC 旁边一个“顺手加上的适配器”，而是系统语义和网络语义真正接缝所在。

## NI 的位置

`NI` 是 endpoint 和 NoC 之间的协议边界。它一边面对的是：

- tile 的 load/store 或 stream 语义
- DMA descriptor 和 command queue
- local SRAM / scratchpad 接口

另一边面对的是：

- packet / flit
- credit / backpressure
- source id / destination id / message class

所以 NI 做的不是“简单收发”，而是把两套完全不同的抽象翻译成对方能理解的形式。

## 它通常负责什么

典型职责包括：

- request / response packetization
- flit reassembly
- injection FIFO 与 ejection FIFO
- 本地 flow classification
- address decode 或 route id 生成
- 与 DMA、tile pipeline、local memory 的握手

这决定了一个非常重要的事实：NoC 看见的 traffic 形状，常常先由 NI 决定，而不是由 router 决定。

## 为什么 NI 会成为真实瓶颈

很多分析会默认 endpoint 可以按链路峰值持续注入或持续消费。真实情况通常不是这样。

NI 至少受下面三类约束：

- 注入侧：本地端口宽度、packet header 开销、credit stall
- 接收侧：reassembly buffer、ejection FIFO、本地消费速率
- 语义侧：一个上层事务可能拆成多 packet，也可能要求按一定顺序交付

因此“链路带宽 32 GB/s”不等于“tile 能稳定以 32 GB/s 发和收”。

## 注入带宽不是理论链路带宽

NI 的理论注入上限通常近似于：

```text
injection_peak ≈ link_width × frequency
```

但有效注入带宽还会被这些因素压低：

- packet 头尾开销
- packet 边界带来的气泡
- credit 等待
- 上层事务发起粒度不足
- outstanding request 太少导致 NI 闲等返回

所以工程上更有意义的量是 `effective injection rate`，而不是单看 link width。

## 接收侧往往更容易被忽略

NoC 把 packet 送到目的地，不代表系统已经完成消费。目的端 NI 还要：

- 接住 flit
- 拼成完整消息
- 根据 message class 送往 local SRAM、register file、DMA response queue 或 stream FIFO

如果目的端 local memory 或 queue 吃不动，ejection 会被拖慢，credit 回不去，最终表现成上游网络 stall。

这也是为什么很多“网络利用率不高但系统吞吐上不去”的问题，根因其实在 NI 之后。

## 它和顺序语义的关系

NoC 内部通常只保证较局部的有序性，例如：

- 同一条 VC 上的串行前进
- 同一路径资源下的 FIFO 风格行为

而上层事务可能要求：

- 某些 response 必须可重组
- 某些 command 必须在前一条完成后再交付
- 某些 completion 必须对软件或 runtime 可见

这些语义大多由 NI 或其邻近控制逻辑负责兜底，而不是由 router 负责理解。

## deterministic NPU 为什么更依赖 NI 设计

在 deterministic NPU 里，很多系统行为希望可静态推断。这会让 NI 承担更多“边界整形”职责，例如：

- 把静态 route id 附在 packet 上
- 按 traffic class 选择不同 VC 或网络
- 保持主数据流与 control/completion 的接口边界

换句话说，NI 是很多 deterministic 设计意图落到硬件上的第一站。

## NI 和 BUS 的边界

从 BUS 视角看，NI 往往还暴露：

- 配置寄存器
- command queue
- status / completion
- error / timeout 可见性

这说明 NI 不只是 NoC 边界，也是 BUS-control 和 NoC-data 的系统边界对象。设计不好时，问题会表现为：

- 软件门铃写了，但网络没真正启动
- 网络内部完成了，但 completion 没回到软件可见边界

## 常见误区

- 认为 NI 只是“切包器”
- 认为只要 NoC 无丢包，NI 就不会成为问题
- 认为注入和弹出对称，建模一个就够

更准确的说法是：

- NI 决定事务如何变成可运行的 packet 流
- 无丢包只说明网络可靠，不说明 endpoint 能持续接住和交付数据
- 注入和弹出常常受完全不同的局部资源限制

## 一句话理解

NI 是系统语义进入 NoC 的闸门，也是 NoC 结果回到系统语义的出口；很多“网络问题”其实先是 NI 问题。

## 建模启示

建模 NI 时，最少要有：

- injection FIFO
- ejection FIFO
- packetization / reassembly 开销
- class 到 VC / network 的映射
- 与 local memory 或 DMA queue 的消费速率

如果模型进一步考虑 deterministic 行为，还应显式加入：

- route id 或目的 node 解析
- completion visible 的边界
- ejection blocked 的原因分类

否则你只能模拟“包有没有到 router”，模拟不了“系统有没有真正用上这些包”。
