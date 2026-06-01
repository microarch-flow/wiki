# PCIE 高频问题

上级：[08 术语与检查清单](./README.md)

相关：[PCIe 建模参数与公式速查](./pcie-modeling-params.md)

## 为什么 write 常比 read 更容易跑满

因为 read 依赖 completion 返回路径，容易被往返延迟和 outstanding 深度限制。write 是 posted，发出去不等返回，只要 credit 足够就能连续发；read 是 non-posted，吞吐受 `outstanding × bytes / RTT` 封顶。

## BAR 和 DMA 地址有什么区别

BAR 是主机访问设备资源的窗口；DMA 地址是设备访问主机内存时使用的地址视角。

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

按每 TLP 固定开销 ~24 字节算，有效吞吐 = 名义带宽 × MPS/(MPS+24)：MPS=128 → ~84%，256 → ~91%，512 → ~95%。MPS 越大固定开销摊得越薄，但受路径最小公共值钳制，常见实际值 128/256。

### read 要多少并发才能灌满链路

`所需 outstanding ≥ 名义带宽 × RTT / bytes_per_request`。例：Gen4 x8（~16 GB/s）、RTT=1µs、单请求 512B，需 ~31 个并发。若 Tag 只有默认 32 个，几乎没余量，RTT 稍大就掉速。

### Tag 上限是多少

默认 5-bit = 32，Extended Tag = 256，10-bit Tag = 768/1024。这是 read 并发深度的硬上限。

### 一个 read 会被拆成几个 completion

由 MRRS（单请求上限）和 RCB（64/128 字节返回边界）决定，`ceil(request_size / completion_payload)`。每个 completion 各带一份 header 开销，拆得越碎 read 路径效率越低。
