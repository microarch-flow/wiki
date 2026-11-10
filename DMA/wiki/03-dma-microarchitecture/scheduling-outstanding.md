# 调度、Outstanding 与回包组织

上级：[03 DMA 引擎微架构](./README.md)

相关：[DMA 与 NoC](../05-system-integration/dma-and-noc.md)、[指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)、[BUS：AXI Channel、ID 与 Outstanding](../../../BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding.md)

## 这页在回答什么问题

为什么很多 DMA 的上限不是由理论带宽决定，而是由 request 注入节奏、outstanding 窗口和回包组织方式决定；以及为什么“把请求尽量发满”经常不是正确策略。

## Outstanding 不是越大越好，而是用来换 latency hiding

`outstanding` 指的是已经发出、但尚未完成闭环的 in-flight 事务数。它存在的根本原因很直接：memory 和互连都有非零 latency，如果 DMA 每等一笔回完再发下一笔，就会一直在空等。于是 DMA 用 outstanding 窗口把多个未完成事务挂在系统里，用空间和状态复杂度去换 latency hiding。

可以把 outstanding 想成餐馆里同时发出去、还没回桌的点菜单数。发得太少，后厨一闲下来前台就断单；发得太多，出餐口和传菜口会挤成一团。这个类比的边界是：真实 DMA 的“菜单”并不是独立同质项，事务还有 read/write 区别、地址相关性、返回路径耦合和 completion 闭环，所以不能拿它推出简单的线性规律。

## 真正的难点是 request 和 response 必须一起看

很多分析只盯 request injection，这往往不够。不同协议的请求、数据、响应和资源释放形成不同的偏序；不能把它们画成通用的 `request → response → data_commit → completion → slot_release`。

AXI4 读：AR 握手后返回 R beat。每个成功接收的 beat 可以分别写入目标或 response buffer；最后一个 R beat 不必早于之前 beat 的落位。AXI4 写：AW 与 W 可先后或交错握手；AW 和最后 W beat 均被接收后才允许生成 B。部分写数据可在 B 前处理。B 完成该接口的写响应，不单独保证 DRAM 落位或 CPU cache 可见。

PCIe Memory Read 等待一个或多个带数据的 Completion；posted Memory Write 不返回对应的事务 Completion。链路 ACK、发送缓存释放、目标可见性和 DMA completion 是不同事件。DMA 的完成条件由设备契约指定，不能凭一个协议响应推定所有数据可供 CPU 使用。

例如 AXI 读的 R beat 0 已写入 SRAM，但 beat 1 仍在返回；response buffer 可因 beat 0 消费而释放一个槽，读 outstanding 通常要等最后 R beat 握手才释放。completion queue 和 descriptor 槽则由各自契约释放。具体事件和偏序见 [模型数据结构与事件规范](../06-performance-modeling/model-schema.md#规范事件与偏序canonical-event-taxonomy)。

## 调度器至少在决定三件事

DMA 调度不是“先来先服务”这么简单。只要系统有多任务、多通道、多方向流量，调度器至少要决定三件事：

- 先发谁：不同 queue、channel、priority 如何仲裁
- 发多猛：outstanding 窗口和信用控制怎么设
- 何时收敛：什么时候主动节流，避免把 return path 或目的端打爆

常见策略包括 round-robin、fixed priority、age-based、credit throttle、token bucket。它们没有普适最优解，只有针对不同系统目标的 trade-off。延迟敏感控制流希望尽快通过，高吞吐 bulk DMA 希望尽量维持 steady-state，AI 供数系统则常常希望 refill 和 writeback 都别压死关键 response。

## 回包组织为什么经常比发包更难

如果系统只支持严格顺序返回，DMA 设计会简单很多，但吞吐往往也会被拖低。只要系统允许 ID、多 bank 并发、乱序返回或多源 response 混合，DMA 就必须显式组织回包：

- 哪个 response 属于哪个 descriptor 或 subrequest
- 数据何时算真正落位
- 部分完成能不能提前推进
- completion 是否必须保持某种顺序可见

这就是为什么很多 DMA 引擎里会长出 `reorder buffer`、`completion table`、`inflight scoreboard`。它们做的事并不华丽，但没有这些状态，DMA 既打不满带宽，也很难保证正确 completion。

## 什么时候会看到“平均不错、尾巴很差”

如果系统表现为平均带宽不低，但 completion 尾延迟很差、热点周期性出现、偶发 pipeline 断供，优先怀疑 DMA 的调度和回包组织，而不是先怀疑链路规格不够。典型原因包括：

- outstanding 太小，隐藏不了外部 memory latency
- outstanding 太大，return path 周期性堆积
- writeback/completion 路径与 bulk data 共用瓶颈端口
- 优先级策略让关键小流量长期被 bulk 流压住

这些现象和 [RAM wiki 的 row locality / controller policy](../../../RAM/wiki/06-memory-controller/command-scheduling-fr-fcfs.md) 会形成直接耦合。DMA 看到的是“为什么回得慢”，DRAM controller 看到的是“为什么这些请求被这样排”。

## 常见误解

常见误解：`outstanding 窗口越大越好`。实际上超过系统能消化的点后，只会把排队和尾延迟后移。

常见误解：`DMA 性能瓶颈在发不出去`。实际上很多系统真正卡在 response return、destination ejection 或 completion release。

常见误解：`乱序返回只是协议细节`。实际上它直接决定 DMA 是否需要 reorder/completion 组织结构。

## 一句话理解

DMA 的性能不是把请求尽量发满，而是把 `发请求、收回包、写完成、释放资源` 组织成能持续前进的并发形状。

## 建模启示

这一页是性能模型的核心。event-driven 仿真里至少应显式追踪 `outstanding_count`、`oldest_inflight_age`、`response_queue_occupancy`、`completion_backlog` 四类状态。

至少记录 descriptor 受理、按协议区分的请求与数据握手、目标域的 data commit、DMA completion，以及带 `resource_kind` 的独立资源释放事件。posted write 不产生 read-style completion，不能把 `response_arrive` 设为每个子事务的必经事件。

模型可以按目标折叠事件，但必须先证明折叠不会改变所关心的依赖和可见性。要分析 tail latency、软件 timeout 或 hang，就需要分别记录设备承诺的传输完成点、completion 可见点、所需 cache 同步和 consumer-ready；这些边界是否存在严格顺序取决于设备与软件契约。
