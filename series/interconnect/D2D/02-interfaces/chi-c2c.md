# AMBA CHI C2C：一致性消息怎样跨越芯粒？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

当两个芯粒参与同一个缓存一致性系统时，跨越芯粒边界的不只有读取请求和数据，也可能有查询缓存状态的 snoop 和对应响应。AMBA CHI Chip-to-Chip（CHI C2C）规定怎样把 CHI 消息组织成适合跨芯片传输的形式，再交给选定的承载接口。

本文的具体封包以 [Arm CHI C2C Architecture Specification，Issue A](https://documentation-service.arm.com/static/65cb95b0c2052a35156cea71) 为准。它既可用于封装内芯粒，也可用于其他芯片间连接；本文只讨论封装内案例。

## 先看一次跨芯粒 snoop

这是**构造案例**。假设芯粒 A 和 B 处于已建立的一致性域；两端的 CHI C2C 接口和所选承载链路均已就绪。某个地址的 Home 节点位于 B，A 的一个缓存持有该缓存行的最新修改数据。

| 步骤 | 系统中发生的事 |
| --- | --- |
| 1. 发起 | B 上的请求方读取该地址，B 的 Home 节点根据当前一致性状态处理请求。 |
| 2. 查询 | 在本例中，Home 需要向 A 发出 snoop，以取得该缓存行的最新数据。snoop 经过 B 的 CHI C2C 接口跨越封装。 |
| 3. 返回 | A 的缓存按请求处理，并通过返回路径提供数据及所需的状态信息。B 的接口将收到的消息交给本地一致性逻辑。 |
| 4. 完成 | Home 和请求方按所选协议完成必要的状态处理，B 的请求方才能取得有效数据。 |

这是为了展示边界而简化的路径，不指定具体 CHI 操作码或所有消息。实际是否需要 snoop、数据从哪里返回，以及缓存状态怎样变化，取决于请求类型、初始状态和具体实现。链路收到 snoop 也不等于整个读取已经完成。

## 消息怎样经过接口

在一个使用共享跨芯粒连接的实现中，可以按下面的职责理解路径：

1. **本地协议逻辑**产生请求、响应、snoop 或数据等消息，并维护相应事务与一致性状态。
2. **CHI C2C 协议和封包逻辑**将需要跨越边界的消息转换并放入容器；接收端再将容器拆回消息。
3. **所选链路与 PHY**负责承载容器和传输信号；对端收到后，将消息交给本地协议逻辑。

Issue A 将消息分为 REQ、RSP、SNP、DAT 和 MISC 类别；MISC 用于接口初始化等用途。共享连接可以在一个容器内组织多个消息。规范也描述了为消息类别使用独立连接的方式，因此不是所有 CHI C2C 连接都必须使用本文的共享容器方式。[Issue A，第 B2 章](https://documentation-service.arm.com/static/65cb95b0c2052a35156cea71)

## 一个容器有多大

以 Issue A 的 **Format X** 为例，一个容器为 **256 byte**：其中 6 byte 为链路头，10 byte 为协议头，另有 12 个各 20 byte 的消息位置。

这些消息位置可以承载不同类别的消息，也可能有未使用的空间；消息本身还有字段。因此，**240 byte 的消息位置不等于每个容器都交付 240 byte 的应用数据**。一个消息也不必独占一个容器。格式和填充规则详见 [Issue A，第 B3 章](https://documentation-service.arm.com/static/65cb95b0c2052a35156cea71)。

Arm 说明该格式与指定的 UCIe 256-byte Latency Optimized Mode 相容；UCIe 联盟也描述了用 UCIe 1.1 streaming flit 承载 CHI 的方法。要形成实际连接，双方仍须支持相容的版本、格式和配置。[UCIe streaming 说明](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay)

## 为什么还要管流控与完成

请求、snoop、响应和数据可能共享承载资源。如果发送端持续发送，而接收端没有空间，系统需要阻止消息丢失，并让完成已有事务所需的消息继续前进。Issue A 使用按消息类别管理的 credit 等机制处理这些要求；这不表示只要加上 credit，任意实现就自动不会死锁。[Issue A，第 B5 章](https://documentation-service.arm.com/static/65cb95b0c2052a35156cea71)

CHI C2C 的消息组织也不自动指定底层链路的所有可靠性功能。CRC、重放等是否存在，取决于选定的承载模式和实现。即使链路确认已经收到容器，系统仍要处理其中的 snoop、数据和一致性状态，才能判断本例读取是否完成。

Arm 已发布 [CHI C2C Issue B](https://developer.arm.com/community/arm-community-blogs/b/soc-design-and-simulation-blog/posts/from-complexity-to-simplicity-scaling-and-future-proofing-chiplets-with-amba-chi-c2c-property-negotiation)。本文的格式和数字只对应 Issue A；采用其他版本时，应重新核对格式、能力协商和事务要求。

## 接下来怎么读

- [一致性与内存互连](../../COHERENCE/README.md)：理解缓存副本、权限和一致性域。
- [UCIe 1.1 读取案例](../ucie-pcie-read.md)：比较 PCIe 读取的 Completion 与链路交付。
- [芯粒互操作与启动](../03-system-design/interoperability-and-bring-up.md)：看链路和系统需要哪些共同配置。
- [NoC：跨 die 网关与排队](../../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：分析有限缓冲、回压和片上网络的关系。
