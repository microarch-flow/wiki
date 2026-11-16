# 网络接口 NI：事务怎样进入和离开 NoC？

上级：[05 端点与系统集成](../SUMMARY.md#05-system-integration)；原章节：[05 端点与系统集成](./README.md)

相关：[Packet、Flit 与 Phit](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)、[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)、[跨时钟域、复位与流控](./clock-domains-and-reset.md)、[事务拆分、顺序与完成](./transaction-ordering-and-completion.md)

<span id="ni-network-interface-design"></span><span id="这页在回答什么问题"></span>网络接口（Network Interface，NI）连接端点接口和网络传输资源。它需要把输入转换为网络可发送的消息，也需要接住网络返回，并按端点契约交付。具体功能可以分布在 NI、桥、DMA 或其他相邻模块中。

## 从请求到返回

<span id="ni-的位置"></span><span id="它通常负责什么"></span>以一次读取为例，发起端给出地址、长度、标识及属性。NI 或相邻逻辑确定目的端，按实现支持的规则生成请求消息；目的端接纳请求后，数据和状态返回，接收逻辑再交给原发起者。

| 边界 | 输入 | 可能需要的状态或处理 |
| --- | --- | --- |
| 注入 | 地址、长度、数据或流接口 | 目的选择、分片、消息类别、注入队列。 |
| 网络 | packet/flit、发送许可或反压 | 按接口契约发送；等待可用缓冲和仲裁。 |
| 接收 | 返回数据、状态及匹配信息 | 接收队列、重排或重组、端点握手。 |

不是每种 NI 都需要完整事务重组；流式接口也可能逐 beat 交付。[AMD Versal NMU](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Master-Unit) 是一个具体实现，包含 AXI 转换、地址查找和读响应重排。

## 原始带宽与有效数据

<span id="为什么-ni-会成为真实瓶颈"></span><span id="注入带宽不是理论链路带宽"></span>假设单向端口宽 128 bit，时钟为 1 GHz，每拍传输一个该宽度的 flit，原始容量为 16 GB/s。再假设每包由 1 个不携带数据的 header flit 和 4 个各载 16 B 数据的 flit 构成，没有额外尾 flit、空拍或反压：

> 有效数据率 = 64 B ÷ 5 拍 × 1 GHz = 12.8 GB/s。

这是构造例。实际包格式、有效字节、时钟、并行端口和空拍均可能不同。若一个 flit 需要多个 phit，不能再假设每拍发送一个 flit。[AMD 对其 NoC 封包开销的说明](https://docs.amd.com/r/en-US/pg313-network-on-chip/Packetization-Overhead)给出了不同的产品实例。

## 接收和顺序也消耗资源

<span id="接收侧往往更容易被忽略"></span>数据到达目的路由器后，还可能等待 NI 接收、重组和本地 consumer。若消费停顿且有限缓冲逐渐填满，反压可能沿资源链传回上游。传播是否到达源端取决于剩余缓冲、在途数据和后续流量。

<span id="它和顺序语义的关系"></span>接收方可能需要记录事务、片段及顺序状态。不能仅凭“同一 VC”推断所有端点事务都按所需顺序完成；具体保证取决于路由、仲裁和端点契约。分片、重复 ID 与响应顺序见[事务拆分、顺序与完成](./transaction-ordering-and-completion.md)。

<span id="deterministic-npu-为什么更依赖-ni-设计"></span>静态计划可以指定目标、类别或注入窗口，但 NI 和目的端仍须有足够的缓冲及服务机会。固定计划不代替对实际停顿和错误的处理。

## 集成时记录什么

<span id="ni-和-bus-的边界"></span><span id="常见误区"></span>配置、doorbell 或 completion 可能由 NI 邻近的控制逻辑提供，不应假设它们都是 NI 的固定内部模块。网络不因缓冲溢出而丢 flit，也不等于已经证明数据完整、事务正确或端点最终完成。

<span id="建模启示"></span>按研究目标记录输入输出握手、packetization、注入与接收容量、匹配状态、可用 credit、端点消费和错误。把**接收一个 flit**与**上层消费完成**记为不同事件。

<span id="一句话理解"></span>NI 把端点契约转换成网络操作，也把网络结果重新交付给端点；两个方向都可能受资源限制。
