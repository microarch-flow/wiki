# 术语表

上级：[09 参考资料与研究模板](./README.md)

## 基础术语

- `DMA`：Direct Memory Access，数据移动执行机制
- `DMA engine`：具体执行数据搬运的硬件块
- `DMA controller`：更偏控制、编排和多通道管理的 DMA 硬件单元
- `DMA IP`：可作为产品/IP 交付或集成的一类 DMA 实现
- `descriptor`：描述一次或一组 DMA 任务的数据结构
- `scatter-gather`：处理离散物理段的传输方式
- `burst`：总线或互连上的一段连续事务粒度
- `outstanding`：已发出但尚未完成的事务数量
- `completion`：任务完成通知或完成记录
- `doorbell`：软件通知硬件有新任务的触发机制
- `queue / ring`：软件或硬件用于组织 DMA 提交的顺序容器
- `linked list`：通过 next pointer 串起多个 descriptor 的提交方式
- `cyclic`：循环缓冲或循环搬运模式
- `coherent DMA`：与 CPU cache 自动保持一致的 DMA 模式
- `non-coherent DMA`：需要软件显式处理 cache 可见性的 DMA 模式
- `cache-coherent DMA`：`coherent DMA` 的更明确写法
- `IOMMU/SMMU`：为 I/O 设备提供地址翻译和隔离的单元
- `double buffering`：通过双缓冲组织传输和计算重叠
- `QoS`：对 DMA 流量做优先级、公平性或限速控制的机制
- `reorder`：为了提升吞吐而允许返回或处理顺序与发出顺序不同
- `polling`：软件主动轮询 DMA 状态，而不是等中断
- `observability`：通过计数器、trace、状态寄存器等观察 DMA 内部行为的能力
- `virtualization`：让 DMA 面向多 VM、多地址空间或多安全域工作
- `tail latency`：尾部慢请求或慢完成的延迟表现
- `local memory`：tile/cluster/engine 邻近的 SRAM、scratchpad 或本地缓冲

## 一条统一口径

本 wiki 里会同时出现：

- `DMA`：系统角色或数据移动机制
- `DMA engine / controller`：具体硬件块
- `DMA IP`：产品/集成视角下的一类实现

读上下文时最好先分清楚当前说的是哪一层。

## 一句话理解

DMA 的术语体系，核心围绕 `任务描述、事务并发、完成语义、系统一致性` 四类概念展开。
