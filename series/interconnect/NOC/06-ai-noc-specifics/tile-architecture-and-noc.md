# Tile 怎样与 NoC 交换数据？

上级：[05 端点与系统集成](../SUMMARY.md#05-system-integration)；原章节：[06 AI NOC Specifics](./README.md)

相关：[网络接口 NI](../05-system-integration/ni-network-interface-design.md)、[NoC 与存储系统](../05-system-integration/noc-meets-memory-system.md)、[DMA 与 NoC](../05-system-integration/dma-engine-noc-interaction.md)

<span id="tile-architecture-and-noc"></span><span id="这页在回答什么问题"></span>一个 tile 既可能从网络取得数据，也可能向其他端点发送结果。计算、局部存储和 NI 共享的资源，会改变数据何时能够注入或被消费。

## Tile 的两个网络方向

<span id="tile-不是普通-endpoint"></span><span id="tile-的三个-noc-相关上限"></span>一种 tile 可以包含计算单元、局部 SRAM、调度逻辑和 NI；具体划分取决于实现。注入方向需要准备数据、读取本地资源并取得网络发送机会。接收方向需要接住数据，并将其交给 SRAM、计算单元或其他 consumer。

<span id="注入和弹出通常不对称"></span>两个方向可能使用不同端口、队列与仲裁。网络入口有空闲容量，不表示本地 SRAM 已经准备好数据；一个 flit 到达，也不表示目的计算已经消费它。

## 一个 bank 怎样造成接收反压

<span id="local-sram-直接决定流量形状"></span>下面是构造例。NI 接收 FIFO 深度为 2 flit，开始为空；每 flit 32 B。目的 SRAM 只有一个 32 B 的读写共享端口，每拍最多接纳一次操作；FIFO 中的 flit 写入 SRAM 时也使用这个端口。假设 compute 在拍 0、1、2 都占用该端口，没有旁路；上游初始只持有对应两个空槽的 credit。

| 拍 | 本地端口与接收动作 | 拍末 FIFO 占用 |
| --- | --- | --- |
| 0 | compute 使用端口；flit 0 进入 FIFO。 | 1 |
| 1 | compute 使用端口；flit 1 进入 FIFO。 | 2 |
| 2 | compute 使用端口；FIFO 无空槽，第三个 flit 不能获新的接收授权。 | 2 |
| 3 | 假设 NI 获得端口，flit 0 写入 SRAM。 | 1 |

释放槽位后，credit 还需要按接口规则返回，才能再次用于发送。表中没有假设返还延迟。若上游持续提供数据，等待可能进一步向上游传播；它不会因这个例子而必然传遍整个网络。

增加 bank 或端口可能允许 compute 和 NI 并行，但前提是两个访问映射到可独立服务的资源，且入口、出口与仲裁也有容量。一般的 bank 映射见 [SRAM bank 地址映射与冲突](../../../storage/02-sram/foundations/sram-bank-address-mapping-conflicts.md)。

## 数据放置和计算节奏

<span id="tile-to-tile-forwarding-很重要"></span>producer 可以通过网络向 consumer 直接转发结果，也可以经共享存储交换；是否支持由系统接口决定。两种路径的访问次数、缓冲和依赖不同，应结合实际数据放置比较。

更大的局部 SRAM 可能允许更多复用，但只有工作负载、分块和调度使用这部分容量时，才可能减少网络搬运。数据仍需被装入；不能仅凭 SRAM 容量推导运行期流量为零。

<span id="为什么-dsl-必须描述-tile-内部参数"></span><span id="建模启示"></span>研究端点瓶颈时，记录注入与接收队列、读写端口、bank 映射、仲裁和 consumer 就绪事件。研究复用时还需记录数据放置与计算阶段。模型可以按问题选择粒度，不必为每个问题都实现完整 tile 微架构。

<span id="一句话理解"></span>Tile 的计算和本地存储决定它何时能供给或接收网络数据；网络到达只是完整数据路径中的一个边界。
