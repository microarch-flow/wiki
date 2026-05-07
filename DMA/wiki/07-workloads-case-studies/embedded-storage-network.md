# 嵌入式多媒体与存储/网络路径

上级：[07 工作负载与案例](./README.md)

相关：[SoC 外设与 I/O DMA](../05-system-integration/soc-peripheral-io.md)

## 这页在回答什么问题

在非 AI 场景里，DMA 为什么仍然是系统流量组织的关键角色。

## 三类典型路径

- camera / display：帧缓冲连续搬运
- storage / NVMe：高吞吐块数据搬运
- network / Ethernet：包流与 ring buffer 驱动

## 它们的共同挑战

- 持续流式数据
- CPU 不能逐次介入
- 对实时性和 buffer 管理敏感

## 一句话理解

即使不做 AI，凡是遇到持续数据流、实时约束和高搬运占比的系统，DMA 都会变成关键基础设施。
