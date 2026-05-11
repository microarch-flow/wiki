# AXI 到 DDR Controller 的路径

上级：[04 微架构与系统集成](./README.md)

相关：[RAM 控制器、并行度与页策略](../../../RAM/wiki/04-system-architecture/controller-parallelism-page-policy.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)

## 这页在回答什么问题

为什么 AXI 一侧看起来“请求发得很顺”，到 DDR 一侧却可能完全变成另一种性能形态。

## 从 AXI 到 DDR 不只是协议直通

中间通常至少还隔着：

- interconnect 仲裁
- address remap / decode
- memory controller request queue
- read/write scheduler
- DDR command timing 约束

所以 AXI 的一个 read burst，到了 DDR 侧未必还是“直接连续完成”的体验。

## Memory controller 在重新解释请求

控制器会关心：

- 请求落在哪个 channel / bank / row
- 当前读写队列的混合情况
- 是否值得合并或重排
- 是否会引发 row conflict

这意味着 AXI master 看到的 latency，很多时候是 memory controller 调度策略的投影。

## 一个重要边界

AXI 关注的是事务流和返回流。  
DDR controller 关注的是命令序列和阵列资源。

两者之间不是一一对应关系，而是：

- 多个 AXI 请求可能映射到同一 row
- 一个 AXI burst 可能被拆成多个 DRAM 命令片段
- 返回路径可能因为队列和写读切换出现抖动

## 继续阅读

- 如果你在追 `DMA 如何把 AXI 请求送进内存`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `为什么读写混合时体验发飘`：看 [Read/Write Combine 与 Bus Turnaround](./read-write-combine-turnaround.md)
- 如果你在追 `为什么 DDR 吞吐不差但 AXI 返回不稳`：看 [Row Locality、Return Path 与 AXI 体验](./row-locality-return-path-axi-experience.md)

## 一句话理解

AXI 到 DDR 的路径，本质上是“通用事务流”进入“强物理约束调度器”的转换过程。
