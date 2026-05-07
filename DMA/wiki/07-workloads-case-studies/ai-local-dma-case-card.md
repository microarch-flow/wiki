# AI Local DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AI 加速器里的 DMA](./ai-accelerator-dma.md)、[HBM 到 Tile 的数据供给链](./hbm-to-tile-data-supply-chain.md)

## 这页在回答什么问题

为什么 AI accelerator 里常会有一类“local DMA”，它和 SoC DMA、PCIe DMA 看起来相似，但优化目标明显不同。

## 典型系统位置

- cluster 或 tile 附近
- 连接 cluster SRAM、tile buffer、NoC endpoint
- 常服务固定数据流模式和编译器/runtime 计划

## 它通常在解决什么问题

- 局部 staging
- tensor tile 搬运
- refill / consume / writeback 协同

## 核心机制

- 小而高频的任务提交
- stride/2D/3D 地址生成
- 强依赖 local memory 端口和 bank 布局
- 与 compute pipeline 强同步

## 最常见瓶颈

- bank 冲突
- refill 和 compute 抢端口
- outstanding 不足导致 pipeline 断供
- writeback 回压反向拖慢下一轮

## 最值得抄走的判断

AI local DMA 不是追求“通用性最强”，而是追求 `与局部存储和数据流最匹配`。

## 一句话理解

AI local DMA 是最能体现 DMA 系统性的一类对象，因为它直接决定 compute 是否能持续吃到数据。
