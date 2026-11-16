# NoC 与存储系统：数据为什么会在端点等待？

上级：[05 端点与系统集成](../SUMMARY.md#05-system-integration)；原章节：[05 端点与系统集成](./README.md)

相关：[Tile 与 NoC 的接口](../06-ai-noc-specifics/tile-architecture-and-noc.md)、[DMA 与 NoC](./dma-engine-noc-interaction.md)、[Memory-centric NoC](../06-ai-noc-specifics/memory-centric-noc.md)

<span id="noc-meets-memory-system"></span><span id="这页在回答什么问题"></span>NoC 可以把请求或数据送到存储端点，但 SRAM bank、memory controller 和 consumer 仍需要接纳和服务。某处持续供给或服务不足时，有限队列可能填满，并沿支持反压的路径影响上游。

## 同一口径比较实际路径

<span id="同一单位比较容量"></span>对一条确定的单向数据流，先列出它**实际经过**的资源，再用同一时间窗口和有效数据字节比较各段能力。长期稳定时，流的吞吐不超过其中任一必经资源分配给该流的有效服务能力。

例如，本地 SRAM 到 tile 的路径不一定经过外部 memory controller；经过 controller 的返回路径也不一定使用另一个 tile 的本地 SRAM。不能把所有可能资源都机械地放进同一个取最小值公式。即使上限是 32 GB/s，也还要检查源端供给、依赖、共享竞争和排队，不能把上限当成实测吞吐。

## Bank 冲突与接收

<span id="sram-bank-冲突和-ejection"></span>假设有 B 个独立单端口 bank，本拍有 Q 个请求；每个请求独立、均匀地选择一个 bank，每个被命中的 bank 本拍最多服务一个请求，且没有历史排队。每个 bank 未被命中的概率为（1 − 1/B）^Q，因此：

> 本拍可服务请求数的期望 = B × [1 − (1 − 1/B)^Q]。

当 B = 4、Q = 3，期望为 37/16 = 2.3125 次。如果每次恰好服务 32 B，频率为 1 GHz，则按该独立分布重复采样得到的平均服务量为 74 GB/s。这不是最坏情况，也不适用于任意历史队列、步长或热点。更多映射和冲突例见 [SRAM bank 地址映射](../../../storage/02-sram/foundations/sram-bank-address-mapping-conflicts.md)。

## Payload 与 flit 使用同一单位

假设有效数据率为 64 GB/s，一个数据 flit 可携带 32 B；每包有 4 个满载数据 flit 和 1 个不载数据的 header flit，没有其他开销。数据本身相当于每秒 20 亿个 flit，连同 header 则需要每秒 25 亿个网络 flit。

在 1 GHz 网络时钟下，后者是合计 **2.5 flit/cycle** 的服务需求。若单个端口每拍只能传一个 flit，它不能独自承载该需求；可能需要多端口、更宽的传输或降低速率。这个例子不把 payload 字节误当成所有 wire 字节，也不代表特定芯片的包格式。[AMD 封包开销示例](https://docs.amd.com/r/en-US/pg313-network-on-chip/Packetization-Overhead)

## Controller 服务窗口与返回突发

<span id="hbm-与-controller-的服务窗口"></span>某种存储接口的原始带宽可由每数据线速率乘数据线数，再统一换算单位；burst 表示一次操作的传输量，不能在已按秒计的接口数据率上再次相乘。实际服务还受调度、读写切换、映射和其他请求影响。

构造例：假设 controller 可服务 600 GB/s，每笔响应 256 B，请求从占槽到释放平均 100 ns，窗口上限为 64 笔。窗口容量上限为 640 million request/s，即 163.84 GB/s；它低于假设的 controller 容量。平均时延随负载变化，其他路径也可能更早成为瓶颈。

<span id="返回突发与有限缓冲"></span>一个响应可能跨多个 beat 或 packet 返回。要评估接收缓冲，必须记录到达节奏、可消费节奏、初始占用和反馈时间。缓冲可以吸收或反压突发；没有一条适用于所有网络的固定深度公式。

<span id="建模启示"></span>保留实际路径、端口能力、地址到 bank/channel 的映射、请求槽与返回队列，并分别统计 payload、网络传输量和端点阻塞。请求/秒与字节/秒只有在明确每笔有效字节后才能换算。
