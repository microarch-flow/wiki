# 术语表

上级：[09 参考资料与研究模板](./README.md)

## 基础术语

- `DMA`：Direct Memory Access，数据移动执行机制
- `descriptor`：描述一次或一组 DMA 任务的数据结构
- `scatter-gather`：处理离散物理段的传输方式
- `burst`：总线或互连上的一段连续事务粒度
- `outstanding`：已发出但尚未完成的事务数量
- `completion`：任务完成通知或完成记录
- `doorbell`：软件通知硬件有新任务的触发机制
- `coherent DMA`：与 CPU cache 自动保持一致的 DMA 模式
- `IOMMU/SMMU`：为 I/O 设备提供地址翻译和隔离的单元
- `double buffering`：通过双缓冲组织传输和计算重叠

## 一句话理解

DMA 的术语体系，核心围绕 `任务描述、事务并发、完成语义、系统一致性` 四类概念展开。
