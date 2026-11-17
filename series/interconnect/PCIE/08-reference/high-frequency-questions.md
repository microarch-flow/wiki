# PCIe 高频问题

上级：[查阅、建模与检查清单](README.md)

本页提供短答和推导入口；数字应以链接正文中的模式与条件为准。

## 为什么 write 常比 read 更容易跑满

普通写不等待逐笔事务 Completion；读需要有限的在途窗口覆盖完整返回时间。但写仍受数据供给、信用和接收服务约束，不能保证一定更快。见[读延迟与并发](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)。

## BAR 和 DMA 地址有什么区别

BAR 描述目标资源窗口；DMA 地址供设备发起访问。P2P 的目标也可以是对端 BAR。CPU 虚拟、物理和总线地址的转换见[地址视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)。

## 为什么设备明明支持 DMA，却还要看 IOMMU

DMA 能力不等于访问已授权。映射、域、权限及翻译模式决定目标是否可达；miss 与 fault 也有不同结果。见 [IOMMU](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)。

## 为什么 MSI-X 常和 queue 一起讨论

队列保存工作和结果，MSI-X 提示软件处理。向量与队列可以多对一，中断可以合并；具体命令是否完成仍看 CQE。见[队列与通知](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)。

## 为什么看起来是 PCIe 问题，最后却落到 host memory

DMA 服务经过翻译、主机内存及软件路径。链路空闲也可能是在等待这些模块。见[瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)。

## 建模高频问题

### 某个 Gen × lane 的名义带宽是多少

先注明单向还是双向、原始还是编码后、Non-Flit 还是 Flit。只扣编码的容量不能称为应用有效吞吐。[速率表](pcie-modeling-params.md#链路速率和计数边界)集中维护数值。

### MPS 到底影响多少带宽

它只给出载荷上限。实际包更小时，不能按 MPS 计算效率；开销还取决于类型与模式。[包长模型](pcie-modeling-params.md#non-flit-mode按真实-tlp-大小估算)给出可替换假设。

### read 要多少并发才能灌满链路

给定目标、完整 RTT 与实际请求长度，可以求容量下界；它不是达到吞吐的充分条件。推导和 25 笔请求算例见[读并发](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)。

### Tag 上限是多少

看请求模式、使能、目标支持和实现资源，不能把字段位数直接转换成所有设备的可用槽数。[Tag 表](pcie-modeling-params.md#read-吞吐与-tag)区分协议能力与 IP 容量。

### 一个 read 会被拆成几个 completion

不能只用 RCB 相除。先确定合法请求边界，再结合地址、MPS、RCB 和 Completer 策略计算。[分包示例](pcie-modeling-params.md#completion-的边界大小与分包)说明一包与多包都合法的情形。
