# UCIe.mem：计算芯粒怎样访问封装内存？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

内存控制器不一定要放在计算芯粒上。系统也可以将控制器放到独立的逻辑芯粒，再用封装内链路传递读取和写入请求。

UCIe 4.0 引入 **UCIe.mem**。本文依据联盟公开资料，解释计算 SoC 到 memory logic die 的职责划分，并用构造读取说明数据路径。本文不定义协议字段、完整错误处理或具体器件配置。[UCIe 4.0 白皮书，第 2–3 页](https://www.uciexpress.org/_files/ugd/0c1418_55e50874214047c3b5474016aa5a4784.pdf)

## 控制器和存储器在哪里

联盟白皮书给出的参考架构，可按下面的功能路径理解：

> 计算 SoC → UCIe 链路 → 内存逻辑 die 中的控制器 → 对应内存接口 → HBM 或 LPDDR

计算侧与内存逻辑 die 通过 UCIe 链路交换具有内存语义的请求和响应；内存控制器负责与其连接的内存配合。白皮书的参考架构使用 UCIe-S 或 UCIe-A 连接逻辑 die，并列出 HBM、LPDDR 等内存类型。图中的箭头表示访问方向，不代表每种器件都采用相同封装、容量或拓扑。

两段连接有不同职责：UCIe.mem 组织跨芯粒的内存请求和响应；控制器到存储器的另一段连接要符合所用内存器件的接口要求。不能把 UCIe 链路视为 HBM 堆栈内部连接，也不能仅凭封装中有 HBM 就断定使用了 UCIe.mem。

## 一次读取怎样经过两段路径

假设计算芯粒 A 要读取 64 B，内存逻辑 die B 负责该地址所对应的内存。双方支持相容的 UCIe 4.0 和 UCIe.mem 配置，链路与地址映射已经就绪。假设所需数据不由其他缓存直接满足。

1. **A 发出请求。** A 的访问逻辑将读取交给 UCIe.mem 路径，并保存足够的上下文，以便关联返回结果。
2. **B 接收请求。** 请求经 UCIe PHY 和承载路径到达 B，再交给 B 的内存控制器。
3. **控制器访问内存。** B 按其所连接器件的接口规则读取数据；这一步发生在 UCIe 链路之后。
4. **结果返回 A。** B 将数据和所需响应经 UCIe.mem 路径送回；A 按系统要求匹配并交付结果。

这是**构造的功能过程**，不是规范报文跟踪。实际请求、响应和数据怎样编码、是否分段、如何处理错误及何时完成，应以具体规范版本和实现为准。B 收到请求也不等于 A 已收到并完成读取。

## 链路带宽和内存服务怎样配合

假设在某个稳定读取场景中，B → A 的 UCIe 路径最多能交付 **64 GB/s 有效数据**，B 的内存控制器及其后方内存最多能为这些读取提供 **48 GB/s**。只考虑这两个资源时，A 的持续读取吞吐上界为：

> **min（64，48）= 48 GB/s**

两个数字都是为计算而设的假设，不是 UCIe.mem 或 HBM 的规格。这里分别给出同一方向、同一数据口径的有效速率；实际吞吐还可能受到请求并发、排队、其他流量和端点处理能力限制。48 GB/s 是这个简化模型的上界，不保证系统一定达到它。[跨芯粒读取的有效性能](../03-system-design/effective-bandwidth-and-latency.md)

联盟发布说明给出 UCIe.mem **最高 93.75% 的数据效率**，并给出按 die 边缘长度计算的带宽密度。这些是指定口径下的接口指标，不是任意应用的实测效率或完整内存子系统吞吐。[UCIe 4.0 发布说明](https://www.uciexpress.org/_files/ugd/0c1418_970201e6ba294a0fa690ae864082fc46.pdf)

## 与 BoW、CXL 和管理访问有什么不同

| 名称 | 主要观察边界 |
| --- | --- |
| UCIe.mem | 本文讨论 UCIe 4.0 中，计算 SoC 与内存逻辑 die 之间的内存语义连接。 |
| BoW Memory Addendum | 描述 BoW 物理接口的内存用例，既有控制器芯粒参考路径，也有存储芯粒参考路径；上层事务规则仍需另行确定。 |
| CXL.mem | CXL 的内存访问协议；具体主机、设备、承载和配置需按所用系统确定。名称相似不表示它与 UCIe.mem 是同一协议。 |
| UCIe Memory Access Protocol | 可用于 UCIe 管理架构中的寄存器访问；它与本文面向内存资源的 UCIe.mem 是不同名称和用途。 |

UCIe 联盟曾介绍用 CXL.mem 提供内存语义的使用方式；UCIe 4.0 白皮书另外介绍 UCIe.mem。选用哪条路径及双方能否互通，仍需核对协议、版本和实现，不能仅凭都带有“mem”判断。[UCIe 联盟问答](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap)；[UCIe 2.0 管理白皮书](https://www.uciexpress.org/_files/ugd/0c1418_b6481ec611e24c6e91f1beb743b0c860.pdf)

## 接下来怎么读

- [BoW 存储接口](./bow-memory.md)：比较控制器芯粒和存储芯粒的 BoW 参考路径。
- [跨芯粒读取的有效性能](../03-system-design/effective-bandwidth-and-latency.md)：继续分析承载开销、在途窗口与目标服务。
- [UCIe 1.1 读取案例](../ucie-pcie-read.md)：比较另一种使用 PCIe 事务的跨芯粒读取。
- [UCIe 2.0 测试访问与管理](../03-system-design/ucie-dfx-test-access.md)：看管理访问与测试逻辑的职责。
- [HBM 的堆叠与封装内互连](../../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)：区分堆栈内部和计算侧连接。
- [CXL 内存访问](../../COHERENCE/cxl-host-memory.md)：了解 CXL 设备内存访问的系统边界。
