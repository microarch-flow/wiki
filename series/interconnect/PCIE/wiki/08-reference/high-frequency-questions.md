# PCIE 高频问题

上级：[08 术语与检查清单](./README.md)

相关：[PCIe 建模参数与公式速查](./pcie-modeling-params.md)

## 为什么 write 常比 read 更容易跑满

普通 Memory Read 是 non-posted，依赖事务 Completion，容易被最终返回的往返延迟和在途深度限制。普通 Memory Write 是 posted，无需等待逐笔事务 Completion；但要连续发送，还须有持续的上游数据供给、足够 credit、可用链路及下游服务能力，也可能受仲裁和拥塞限制。稳态读吞吐受 `平均在途数 × 每请求平均字节 / 平均完整 RTT` 等资源共同约束。

## BAR 和 DMA 地址有什么区别

BAR 定义设备暴露的目标资源窗口，主机常用 MMIO 访问它。DMA 地址是平台提供给发起设备访问已映射资源的地址：常见路径的目标是主机内存；在拓扑、平台和驱动支持的 P2P 路径中，也可以是对端设备允许访问的 BAR 资源。目标窗口与请求者所用地址及翻译不能假定数值相同，见 [P2P 与拓扑约束](../07-advanced-topics/p2p-switch-topology-constraints.md)。

## 为什么设备明明支持 DMA，却还要看 IOMMU

因为“能访问”不等于“应该被允许任意访问”，还要考虑翻译、隔离和虚拟化。

## 为什么 MSI-X 常和 queue 一起讨论

因为高性能设备通常用 queue 承载任务，用 MSI-X 通知主机推进完成处理。

## 为什么看起来是 PCIE 问题，最后却落到 host memory

因为 host-device 路径的尾部常常连着 IOMMU、DDR、NUMA 和 CPU 软件栈，链路不是唯一瓶颈。

## 建模高频问题

下面是建性能模型时最常要查的数，完整表见 [PCIe 建模参数与公式速查](./pcie-modeling-params.md)。

### 某个 Gen × lane 的名义带宽是多少

每 lane 单向有效带宽：Gen3 ~985 MB/s、Gen4 ~1.97 GB/s、Gen5 ~3.94 GB/s，乘 lane 数。例：Gen5 x16 ≈ 63 GB/s。这一列已扣编码开销，不要再乘一次。

### MPS 到底影响多少带宽

MPS 是上限，实际 payload 可以更小。只在 Non-Flit 模式的示例假设中，若每包非 payload 占用 24 B，且实际有效数据为 128 B，则效率为 `128/(128+24) ≈ 84.2%`。实际包格式、DLLP、重传及链路模式会改变效率；不要重复计算已经包含的开销。

### read 要多少并发才能灌满链路

`所需 outstanding ≥ ceil(目标有效吞吐 × 平均 RTT / 每请求平均有效字节)`。假设 Gen4 x8 的目标 `12.8 GB/s`、RTT `1 µs`、每请求 `512 B`，需要 25 个。目标还必须低于链路有效带宽；更高 RTT 或较小请求会增加需要的并发。

### Tag 上限是多少

5-bit 通常最多 32，Extended Tag 已使能时最多 256。10-bit Tag 已使能并且目标支持时，针对单个 completer 最多 768；实际还受 requester 的槽数、缓冲、目标能力及 Tag 分配限制。10-bit 字段有 1024 个位模式，不等于 1024 个可用于单目标的请求。

### 一个 read 会被拆成几个 completion

不能只由 RCB 算出。MRRS 限制请求长度，MPS 限制数据包长度，RCB 限制允许的拆分位置；实际分包还取决于地址和 completer。对齐的 256 B read，在 MRRS≥256、MPS=256、RCB=64 的条件下，可以是一个 256 B CplD，也可以是四个 64 B CplD。
