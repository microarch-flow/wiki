# BUS 设计检查清单

上级：[07 术语与检查清单](./README.md)

## 功能层

- master 和 slave 的角色是否明确
- 地址空间是否完整且无冲突
- error / timeout 路径是否定义清楚
- 顺序模型是否和软件预期一致

## 性能层

- 共享热点会落在哪些 slave
- burst 长度是否会拖慢小请求
- 是否存在长期饿死的低优先级流量
- bridge / CDC 是否形成隐藏瓶颈

## 可集成层

- 是否需要 AXI/AHB/APB 之间的桥接
- 位宽和时钟域变化是否统一处理
- 是否为 DMA、CPU、debug 预留了合理接入点

## 可调试层

- 是否有仲裁等待计数
- 是否有 FIFO occupancy / timeout 计数
- 是否能区分 request stall 和 response stall
- 是否能定位是 master 侧堵还是 slave 侧堵

## 延伸阅读

- [Master/Slave/Bridge 设计清单](./master-slave-bridge-checklists.md)
- [DDR/IOMMU/Debug 集成清单](./ddr-iommu-debug-checklists.md)
- [BUS 高频问题](./high-frequency-questions.md)

## 一句话理解

BUS 设计最容易漏掉的，不是“协议字段没写全”，而是 `顺序、桥接、争用、观测点` 没提前想清楚。
