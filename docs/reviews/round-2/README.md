# 九专题逐篇评审

评审以第二轮开始时的工作区为基线，覆盖九个现行专题目录中的全部 Markdown。逐篇记录概念、设计动机，以及会改变模型行为的条件。对研究资料和导航页，记录其能提供的证据或阅读用途。

第一列链接指向当前正文。末列先记原文诊断。标明“独立复核”的文字说明验收时所查的具体行为。“已修订”表示本轮编辑过该页。“保留”表示本轮保持原文。专题页数包含章节入口和索引。

| 专题 | 逐篇评审 | 本轮修订 | 保留 |
|---|---:|---:|---:|
| [存储单元与控制器（RAM）](RAM.md) | 78 | 60 | 18 |
| [计算数据通路（COMPUTE）](COMPUTE.md) | 31 | 9 | 22 |
| [片上总线（BUS）](BUS.md) | 67 | 37 | 30 |
| [片上网络（NOC）](NOC.md) | 77 | 49 | 28 |
| [直接存储器访问（DMA）](DMA.md) | 57 | 22 | 35 |
| [PCI Express（PCIE）](PCIE.md) | 47 | 27 | 20 |
| [存内计算（CIM）](CIM.md) | 82 | 59 | 23 |
| [共封装光学（CPO）](CPO.md) | 101 | 47 | 54 |
| [制造、封装与测试（FAB）](FAB.md) | 82 | 40 | 42 |
| **合计** | **622** | **350** | **272** |

508 篇文章中修订 325 篇，114 篇目录和章节入口中修订 25 篇。初审列入修订 339 页，复核补修 11 页。

Astra Max 与 6.1 Sol Max 负责初审，6.1 Terra Max 修订正文。独立验收逐一比对修订前文本、初审依据和修订后的正文，对返工页再次核对。另从各专题初审保留的技术文章中各抽一篇。其中 DDR4 时序页在抽查后补修。

阅读教材请从[学习入口](../../../README.md)开始。上一轮有各专题的[基线问题与判例](../2026-11-09-topic-review.md)。

## 可复验的例子

- [一次 GEMM 的 NoC 流量](../../../series/interconnect/NOC/wiki/07-evaluation-methodology/from-workload-to-traffic-trace.md)给出可运行的 Python。4×4 个输出块各做 4 个 K 步，得到 64 个计算事件、48 个传输事件和 3 个屏障。按文中的多播树与本地写回规则，逻辑有效载荷为 96 MiB，跨网络注入的有效载荷为 88 MiB。沿树的每条边分别计数，得到 240 MiB·hop。三种统计使用不同的观察边界。
- [SRAM 端口仲裁](../../../series/storage/RAM/wiki/02-sram-foundations/single-port-dual-port-multi-port.md)可用两个 1RW bank 检查。若每 4 B 轮换一个 bank，同拍到达字节地址 0 和 8 时只能接收一个请求。改为 0 和 4，在没有其他争用且两个端口都可用时，可以同时接收。
- [PCIe 读延迟](../../../series/interconnect/PCIE/wiki/04-data-path-dma-interrupts/pcie-read-completion-latency.md)把 RTT 的终点放在完整读数据返回。若每次有效数据为 512 B，平均 RTT 为 1 µs，目标为 12.8 GB/s，稳态平均需要 25 笔在途请求。是否能达到目标，还取决于实际请求供给、返回带宽和缓冲。
- [DDR4 的外部读命令与首数据](../../../series/storage/RAM/wiki/05-dram-protocol-families/timing-parameters-trcd-trp-tras.md)给出命令/地址奇偶校验的反例。器件示例中，附加延迟 AL 为 0、CAS 延迟 CL 为 11 拍，启用 4 拍的奇偶校验延迟 PL 后，首数据延迟为 15 拍。若模型仍按 11 拍返回，读数据会提前 4 拍。
- [CPO 封装论文卡](../../../series/interconnect/CPO/wiki/08-research/paper-cards/packaging-integration-papers.md)区分同一研究中的两种证据。50 µm 间距对应实测试件，每个 PIC 有 12 个通道。小于 25 µm 的可行性来自模型和波导原型。只有前者能作为该试件的实测几何条件。
