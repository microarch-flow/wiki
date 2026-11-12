# PHY、SerDes 与协议是什么关系？

上级：[全局链路](./README.md)

协议规定参与者怎样交换信息。PHY 是物理层功能及其实现的统称。SerDes 狭义上指串并转换；在器件资料中，它也常指包含时钟、驱动和接收电路的高速收发器。阅读时要先确认作者使用的是哪种范围。

## 一条具体的分层路径

以 1000BASE-X 为例，PCS 负责特定的编码及控制序列；PMA 提供串并转换和时钟恢复；再连接物理介质相关部分。这是该接口的分层例子，不要求所有接口使用相同边界。[AMD 的 1000BASE-X PCS/PMA 文档](https://docs.amd.com/r/en-US/pg138-axi-ethernet/PCS/PMA)列出了这些职责。

PCIe 还有事务层和数据链路层，分别处理请求 / 完成与逐跳链路行为。它的物理层要支持链路建立及电气传输。系统视角见[PCIe 分层架构](../../../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)。

这几个名字关注的问题不同：

| 名称 | 主要问题 | 需要核对的边界 |
| --- | --- | --- |
| 协议 | 双方传什么、何时传、如何解释 | 哪一版规范、哪些可选功能 |
| PHY | 信号怎样在指定介质上传输和恢复 | PCS、PMA、介质相关部分如何划分 |
| SerDes | 怎样进行串并转换，或广义地实现串行收发 | 文档是否把均衡、时钟及控制也算在内 |

这些层次并非三个互不相交的独立芯片。它们可以由同一芯片内部不同模块实现，也可以跨越多个器件。功能画在哪里，取决于具体系统和文档约定。

## 能发信号不等于完整支持协议

假设某收发器能以目标线速率收发比特。系统仍需核对编码、初始化、对端兼容、控制接口和协议状态机。单独满足速率并不足以证明整个产品符合协议。[TI 的 SerDes 文档](https://software-dl.ti.com/jacinto7/esd/processor-sdk-linux-am67/latest/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/SERDES/SERDES.html)也区分收发器能力与外设实际支持。

DDR 等接口同样有 PHY，但接口可以采用不同的位宽、时钟和信号方式。不能只凭“PHY”一词，就假设它与某条长距串行链路内部完全相同。

## 接下来怎么读

看[位宽、线速率、符号率与时钟怎样换算？](./rates-clocks-and-ui.md)，学会给这条路径标注时间与数据量。
