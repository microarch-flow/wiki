# Packet、Flit 与 Phit：网络传输分成哪些单位？

上级：[02 路由器与逐跳流控](../SUMMARY.md#02-router-microarchitecture)；原章节：[02 路由器与逐跳流控](./README.md)

相关：[转发与交换方式](./wormhole-vs-vct-vs-store-forward.md)、[路由器流水线](./router-pipeline-stages.md)

<span id="packet-flit-phit-hierarchy"></span><span id="这页在回答什么问题"></span>一次通信可以按不同粒度描述。packet 方便表达网络消息；flit 可以作为流控单位；phit 用来描述物理链路的一次传输。三个单位回答的问题不同，大小也不一定相同。

## 从事务到网络包

<span id="packet-是通信语义单位"></span>端点可以发出一次读事务，也可以发送一段 stream。网络接口根据上层协议和网络格式，把信息组织成一个或多个 packet。packet 可以包含目的地、类型、顺序信息和有效载荷；具体字段由实现定义。

一次事务不必对应一个 packet。一个请求和它的响应可能分别通过网络传输；一条较长消息也可能拆成多个 packet，接收端再按协议处理。[网络接口 NI](../05-system-integration/ni-network-interface-design.md) 讨论这种转换及事务边界。

## Flit 和 phit 分别描述什么

<span id="flit-是流控与仲裁单位"></span>flit 是 **flow control unit**：在采用 flit 级流控的模型中，它是分配缓冲或推进流控的单位。一个 packet 可以由一个或多个 flit 组成。一个常见的 wormhole 实现让首 flit 携带路由信息，后续 flit 跟随，尾 flit 标记包结束；这只是具体格式，不要求所有实现都有独立的头部和尾部 flit。

<span id="phit-是物理传输单位"></span>phit 是物理链路的一次传输单位。假设链路每拍可传一个 phit、没有空拍：128 bit flit 通过 128 bit 链路需要一个 phit；通过 64 bit 链路需要两个 phit。若接口采用不同传输速率、编码或时钟，还要按该接口的实际契约计算。

<span id="为什么必须分三层而不是两层"></span>区分三个单位，是为了分别回答：传什么消息、按什么粒度管理资源、链路需要多少次传输。不同实现可以合并某些单位；是否在模型中分别表示，取决于要研究的问题。[Dally，Virtual-Channel Flow Control](https://groups.csail.mit.edu/cag/PSRG/papers/dally-ieee92.pdf)

## 一个包怎样通过不同宽度的链路

<span id="一个具体例子64b-packet-在-128b-链路上怎么走"></span>假设线上 packet 总长为 64 B，**已经包含头尾信息和填充**；每个 flit 为 128 bit，即 16 B。发送方连续发送，链路每拍传一个 phit，忽略其他开销。

| 链路宽度 | 每包 flit 数 | 每 flit 的 phit 数 | 全包占用的传输拍数 |
| --- | --- | --- | --- |
| 128 bit | 4 | 1 | 4 |
| 64 bit | 4 | 2 | 8 |

这是单条链路的传输时间，不包括路由、排队、传播流水和接收端处理。链路出现空拍时，总时间还会增加。

如果 **64 B 指有效载荷**，而头尾信息合计另外占 8 B，且允许连续打包到 16 B flit，则需要 ⌈72 ÷ 16⌉ = 5 个 flit，最后填充 8 B。若格式要求独立的头部或尾部 flit，计算方式可能不同。单 flit 包也可以同时携带头、尾语义；是否用 HEAD_TAIL 命名由格式决定。

<span id="和-bus-世界的一个关键差别"></span>接口上的 beat 和网络里的 flit 都可描述分段传输，但它们属于各自协议或模型的单位。网络接口可以将接口传输重新打包；不能假定一个 beat 必然等于一个 flit 或 phit。

## 怎样选择模型粒度

<span id="常见误解"></span>大包可以摊薄头部开销，也可能延长某些资源的占用或等待；影响取决于交换、缓冲和仲裁。减小物理链路宽度会增加序列化次数，但不必改变内部 flit 宽度。

<span id="建模启示"></span>若只估算端点之间的数据量，可以先记录消息字节数。若要分析本章所述的逐 flit 队列和 credit，就要表示 flit 的顺序与资源占用。若链路一次传输不足一个 flit，还要表示 phit 数或等效传输拍数。只记录总字节数，不能推导逐跳排队和反压时序。

<span id="一句话理解"></span>packet、flit 和 phit 分别帮助描述网络消息、流控粒度和物理传输；它们的映射由具体实现决定。
