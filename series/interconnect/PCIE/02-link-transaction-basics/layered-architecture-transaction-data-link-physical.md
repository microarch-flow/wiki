---
title: "PCIe 三层架构：事务、逐跳可靠性与物理链路"
---

<div id="分层架构transaction-data-link-physical" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# PCIe 三层架构：事务、逐跳可靠性与物理链路

上级：[链路、分层与事务基础](README.md)

同一次读取需要表达访问目标、可靠传过每一跳，并把比特送到介质上。PCIe 将这些职责分开。分层有助于找到故障观察点，但不意味着各层的性能互不影响。

## Transaction Layer 关心什么

事务层接收设备或主机接口提交的访问，形成 TLP，携带类型、地址、长度、请求身份、Tag 和属性。接收端解释 TLP；对于需要返回的请求，生成对应 Completion。

事务层还执行适用的排序规则，并通过基于信用的流控管理 TLP 接收缓冲使用。信用检查回答“接收端能否容纳这类包”，不是“事务是否已完成”。[AMD PG054](https://docs.amd.com/r/en-US/pg054-7series-pcie/Transaction-Layer)明确列出了事务排序和信用流控职责。

## Data Link Layer 关心什么

传统 Non-Flit 模式下，数据链路层为相邻端口间的 TLP 传输维护序号、LCRC、ACK/NAK 和重放状态。发送端保留未被确认的包；遇到适用的重放条件时，按协议重发。链路失效仍可能需要上层恢复，不能把逐跳可靠性理解为任意故障下都保证成功。

DLLP 在此模式下承载 ACK/NAK、流控更新等控制信息。**流控管理的职责与控制信息的传递载体是两回事。** 不能因为信用更新由 DLLP 传递，就把所有流控判断都归入数据链路层。

Flit Mode 改变了传输组织及可靠性保护粒度。旧模式的“每个 TLP 一套 framing/LCRC”和 DLLP 开销模型不能直接搬过去。

## Physical Layer 关心什么

物理层把链路数据转换为各 lane 上的信号，并处理适用的编码、对齐、训练、速率及宽度协商等功能。协议 PHY 与具体 SerDes 电路之间还有实现边界，详见 [PHY、SerDes 与协议](../../SERDES/01-overview/phy-serdes-protocol.md)。

链路尚未就绪时，事务不能按正常路径传送；进入 L0 也不证明所有温度、通道和长期误码条件都合格。

<div id="为什么分层对体系结构有价值" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 用一次读取分开三个观察点

假设 EP 经 Switch 读取主机内存。EP 先取得请求发送条件并发出 Memory Read。每跳独立处理接收与链路确认；主机侧随后返回一个或多个 CplD。EP 收齐所需数据后，才正常结束该读请求。

| 观察 | 能证明什么 | 不能证明什么 |
| --- | --- | --- |
| 链路训练成功 | 该链路达到相应运行状态 | BAR、映射或目标服务正确 |
| 该跳 ACK 到达 | 该跳对应传输已被确认 | 最终目标已经完成读取 |
| 最终成功 CplD 收齐 | 该笔读取所需数据已返回 | 设备的软件命令已执行完毕 |

下一篇[一次 PCIe 读取](tlp-dllp-completion-basics.md)继续追踪事务身份；[信用与重放](credit-flow-control-and-replay.md)解释等待和资源释放。传统协议栈示例可参见 [Altera PCIe 协议栈](https://docs.altera.com/r/docs/683093/current/pci-express-protocol-stack)。
