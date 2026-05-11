# Timeout、Fault 与 Hang 定位框架

上级：[05 性能与调试](./README.md)

相关：[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)、[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)

## 这页在回答什么问题

当系统表现为“卡住了”，应该先把它分成哪几类，而不是一上来就全量看波形。

## 三类问题先分开

### Timeout

系统最终有返回，但超出了预期时间。  
通常意味着：

- 某处排队很长
- 某个 slave 很慢
- response path 受阻

### Fault

系统明确返回了错误。  
常见来源：

- decode error
- slave error
- permission fault
- IOMMU/SMMU translation fault

### Hang

系统既没有成功，也没有明确报错，而是一直不前进。  
这通常更危险，常见原因包括：

- 死锁式 backpressure
- 某条通道等待永远不会来的握手
- 中间桥接层吞掉了返回

## 为什么要先做这个分类

因为三类问题的定位起点不同：

- timeout 先看谁慢
- fault 先看谁报错
- hang 先看哪里没有 forward progress

## 继续阅读

- 如果你已经确定是 `fault`：先看 [AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)
- 如果你怀疑是 `IOMMU / permission` 一类 fault：看 [IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
- 如果你已经打开波形：看 [AXI Waveform Debug 方法](./axi-waveform-debug-method.md)
- 如果你想把现象收敛成可复盘记录：看 [BUS 故障复盘模板](../07-reference/bus-debug-postmortem-template.md)

## 一句话理解

把“卡住”先拆成 timeout、fault、hang，是建立系统化总线调试路径的第一步。
