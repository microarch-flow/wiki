# UCIe 1.1 如何承载一次 PCIe 读取？

上级：[02 接口与案例](./SUMMARY.md#interfaces)

一次跨芯粒读取同时依赖上层事务、D2D 承载和封装内信号通道。本文以 UCIe 1.1 承载 PCIe 为例，说明两端需要准备什么，以及请求、数据和完成状态怎样通过这些边界。

## 先约定一次读取

下面是**构造案例**，不是产品实测。假设芯粒 A 有 PCIe Root Complex，芯粒 B 有 PCIe Endpoint。双方支持 UCIe 1.1 和相互兼容的 PCIe 承载配置，链路已经就绪，B 的设备地址窗口也已配置。

A 要从地址 `0x8000_1000` 读取一个 4 字节对齐的 32 位寄存器。假设 B 的桥将该访问映射到本地寄存器，再用 AXI 和片上网络访问它。寄存器此时返回 `0x1234_5678`。

这是一个具体系统的假设：UCIe 不要求每颗芯粒都包含 PCIe Endpoint、AXI 桥或 NoC。PCIe Root Complex 发起读取、Endpoint 返回 Completion with Data 的基本关系，可参见 [PCI-SIG 的事务示例](https://pcisig.com/sites/default/files/files/PCI_Express_Basics_Background.pdf)。

## 请求经过哪些职责边界

| 环节 | 输入、处理与输出 |
| --- | --- |
| A 的 PCIe 请求方 | 发起 Memory Read，保存匹配返回所需的状态，并交付 PCIe 读取请求。 |
| A 的 UCIe 适配器与 PHY | 按双方选定的承载格式组织数据，再由 PHY 发出经过封装通道的信号。 |
| B 的 PHY、适配器与 PCIe 端点 | 接收信号，还原并交付所承载的请求，送往 B 内部的目标。 |
| B 的桥、NoC 与寄存器 | 桥转换请求，经 NoC 访问寄存器，取得数据和访问状态。 |

返回方向再经过 B 的 PCIe 逻辑、两端 UCIe 接口，最终交给 A。UCIe 接口负责跨 die 承载；PCIe 定义本例的请求与 Completion 语义。不能把封装内 UCIe PHY 当作板级 PCIe 电链路的同义词。

## 链路就绪前要确定什么

仅有封装连接线还不够。系统需要确认两端接口及封装通道能够配合，并完成所选接口要求的初始化与训练。两端还要有共同支持的协议和传输格式，才能把期望的上层数据交给对方。

[UCIe 联盟的早期问答](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap)说明，链路初始化涉及宽度、频率和协议支持等工作参数；边带可用于训练等管理功能。[UCIe 1.1 对 streaming flit 的说明](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay)也指出，flit 格式在链路初始化时协商。

这些是应检查的条件，不是一张完整状态机。具体状态顺序、字段、可选能力及失败处理，应以采用的规范版本和实现为准。联盟说明 1.1 向后兼容 1.0；这不表示任意两颗声称支持 UCIe 的芯粒都支持同一协议、格式或物理配置。[UCIe 规范入口](https://www.uciexpress.org/specifications)

## 一次请求怎样完成

1. **A 发起请求。** A 的 PCIe 请求方发送对 `0x8000_1000` 的 4 字节 Memory Read，并保留请求身份和在途状态。A 的 UCIe 接口按选定模式将请求送往 B。
2. **B 执行读取。** B 的 UCIe 接口将请求交给 PCIe 端点。在本例中，端点通过桥发起 AXI 读，NoC 将其送至寄存器。若桥已接纳请求，但 NoC 注入队列暂时不能接收，请求就在桥内等待；有限缓冲可能进一步影响后续请求，具体回压路径取决于实现。
3. **B 返回结果。** 假设寄存器成功返回 `0x1234_5678`，B 的 PCIe 逻辑形成带数据的 Completion，经 UCIe 返回 A。
4. **A 完成读取。** A 按事务身份匹配 Completion，检查状态并收齐请求的 4 字节，然后向发起者交付结果。在这之前，请求已到达 B 并不等于读取成功。

若返回错误状态，A 按系统和协议的错误处理路径报告失败。若等待超时，A 不能仅凭超时就断定远端请求已被取消；迟到响应和在途状态如何处理，取决于实现和适用协议。PCIe Memory Read 的成功 Completion 需要返回数据；PCI-SIG 对无数据却标为成功的情况给出了[说明](https://pcisig.com/section-2311-if-end-point-returns-completion-cpl-no-data-and-successful-completion-status-memory)。

## 链路确认不等于事务完成

如果所选 UCIe 模式提供链路级确认和重放，接收端对链路数据的确认只说明该链路上的交付进度。此时 B 内部仍可能排队，寄存器也可能返回错误。A 必须等待并检查本次 PCIe Completion，才能判断读取结果。

可靠性机制要按模式判断。UCIe 联盟说明：1.1 的 streaming flit 可以使用 D2D 适配器的 CRC 检测和重放；Raw Mode 绕过包括这些机制在内的多项 UCIe 功能。使用 Raw Mode 时，需要由系统按需求在其他位置提供可靠性机制，或明确接受相应后果。这并不表示本例中的 PCIe 承载模式是 Raw Mode。[UCIe 1.1 模式说明](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay)

## 接下来怎么读

**理解本例的启动与完成**

- [一次跨芯粒通信](./01-foundations/cross-die-communication.md)：先区分接口、封装通道和读取完成。
- [UCIe 1.1 链路启动与训练](./02-interfaces/ucie-1-1-link-bring-up.md)：看本例开始前，边带、主带和 Adapter 怎样就绪。
- [芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)：区分接口匹配、链路就绪和目标功能就绪。
- [跨芯粒链路错误检测与重放](./03-system-design/link-reliability.md)：看启用重放的链路怎样检测错误并尝试恢复。
- [跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)：看事务窗口和目标服务怎样约束吞吐。
- [PCIe：事务与 Completion](../PCIE/02-link-transaction-basics/tlp-dllp-completion-basics.md)：区分链路控制、事务 Completion 和软件命令完成。

**比较其他接口**

- [UCIe-3D 垂直连接](./02-interfaces/ucie-3d.md)：比较堆叠芯粒的另一种接口路径。
- [UCIe.mem 存储访问](./02-interfaces/ucie-memory.md)：比较 UCIe 4.0 的另一种内存访问路径。
- [BoW PHY 2.0](./bow-phy.md)：从数据线、随路时钟和 slice 看另一种封装内物理接口。
- [BoW.Flexi 读取案例](./bow-flexi.md)：从 AHB 桥和数据包看另一种跨芯粒读取路径。
- [AMBA CHI C2C](./02-interfaces/chi-c2c.md)：看一致性消息怎样组织并使用相容的承载接口。

**深入系统和物理路径**

- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：继续分析网关、有限缓冲和回压。
- [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)：分析宽度、每线速率和封装通道。
- [HBM 的堆叠与封装内互连](../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)：比较 HBM 堆栈内部连接与计算侧接口。
