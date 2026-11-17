# 嵌入式多媒体与存储/网络路径

上级：[07 工作负载与案例](./README.md)

相关：[SoC 外设与 I/O DMA](../05-system-integration/soc-peripheral-io.md)、[PCIe NIC DMA 案例卡](./pcie-nic-dma-case-card.md)、[NVMe / 存储路径中的 DMA](./nvme-storage-dma-case-card.md)

## 这页在回答什么问题

在非 AI 场景里，DMA 为什么仍然是系统流量组织的关键角色；以及多媒体、存储、网络这三类路径虽然看起来差别大，但为什么都绕不开 queue、steady-state 和完成节拍。

## 三类典型路径，其实都在回答“持续数据流怎么稳定推进”

camera / display 路径强调帧缓冲和周期稳定，最怕 underrun/overrun。storage 路径强调高并发块 I/O，最怕 queue 深度带来的 completion 抖动。network 路径强调包流 steady-state，最怕小包控制开销和中断风暴。

这三类场景的表象不同，但底层问题高度相似：

- 数据持续流入或流出，CPU 不可能逐次介入
- queue、buffer 和 completion 必须能稳定循环
- 一旦 steady-state 被打破，系统表现会迅速恶化

## 多媒体路径为什么更强调周期确定性

camera、display、audio 的 DMA 常常不是追求极限带宽，而是追求“每个周期都不能掉链子”。帧来了就得进 buffer，扫描线到了就得出数据，采样流到了就得按时送走。这里 DMA 更像节拍维持器，一旦某个窗口 missed，结果往往不是“慢一点”，而是直接花屏、掉帧或爆音。

## 存储和网络为什么更强调 queue 深度与 completion

存储和网络看起来更“吞吐导向”，但真正支撑吞吐的其实是深队列 steady-state。NVMe 没有 queue depth 就很难把 I/O 管线喂饱；NIC 没有 batching 和 moderation 就会在小包下被 descriptor/completion 压垮。

所以它们和多媒体路径的根本差别，不是“一个靠 DMA，一个不靠”，而是一个更强调周期 deadline，一个更强调 completion 驱动的深流水稳态。

## 常见误解

常见误解：`只有 AI 系统的 DMA 才值得系统级分析`。实际上 storage / network / multimedia 一样有复杂的 steady-state、completion 和 backpressure 问题。

常见误解：`多媒体 DMA 主要看平均带宽`。实际上它更常先死在周期抖动和 deadline miss。

常见误解：`网络和存储 DMA 只是把大块数据搬来搬去`。实际上 descriptor、queue、moderation 和 completion 路径经常比数据路径本身更早成为瓶颈。

## 一句话理解

即使不做 AI，凡是遇到持续数据流、实时约束和高搬运占比的系统，DMA 都会变成关键基础设施，只是每条路径最敏感的稳定性指标不同。

## 建模启示

这页适合把案例分成 `deadline-driven` 与 `deep-queue steady-state` 两类。

```text
StreamingDMAProfile {
  workload_class: multimedia | storage | network
  dominant_constraint: deadline | queue_steady_state
  completion_style
}
```

若只关心平均吞吐，可以把 multimedia 和 storage/network 混着看；若关心真实系统体验，必须把 deadline miss 与 completion backlog 分成两种不同终态。
