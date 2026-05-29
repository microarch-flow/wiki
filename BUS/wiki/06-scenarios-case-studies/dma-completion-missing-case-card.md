# DMA Completion 丢失案例卡

上级：[06 典型系统与案例](./README.md)

相关：[DMA Descriptor Fetch、Data Move 与 Writeback](../04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)、[Doorbell、Completion 与 Interrupt Flow](../04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)、[AXI 与 DMA 的系统接口](../04-microarchitecture-integration/axi-dma-system-interface.md)、[AXI 属性、Cacheability 与 Barrier](../04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)

## 现象

这是经典的**"货送到了但签收单没回来"**问题：DMA 数据面看起来已经搬完——源和目的 buffer 数据正确，DMA 内部状态也显示 task done。但软件就是收不到"已完成"的通知，或者通知偶发丢失，driver 等待超时。

核心分界就像快递物流：**包裹到达≠签收确认**。签收确认需要一整条链闭合：快递员填回执（writeback）、回执传到系统（cache/coherence 可见性）、系统更新状态（status 更新）、给你发短信（interrupt/polling）、你确认收货（clear/EOI）。任何一环断了，你就一直在等"已送达"通知。

## 典型路径

```text
CPU prepares descriptor
  -> doorbell/start
  -> DMA descriptor fetch
  -> DMA data read/write
  -> DMA write completion record / status
  -> interrupt or polling visible
  -> CPU ISR/driver consumes completion
```

| 阶段 | 期望事件 | 丢失风险 |
| --- | --- | --- |
| T0 | DMA data move 完成 | 数据完成但 writeback 尚未发生 |
| T1 | DMA 发出 completion write | writeback port 被 data write 堵住 |
| T2 | completion write response 返回 | B response 不回，slot 不释放 |
| T3 | completion 对 CPU 可见 | non-coherent cache 未 invalidate |
| T4 | device/assert interrupt | interrupt 早到、未到或被 mask |
| T5 | CPU 读 completion/status | 读旧缓存、read side effect、状态未稳定 |
| T6 | CPU clear/EOI | clear 顺序错误导致重复或丢事件 |

## 根因矩阵

| 根因 | 可见症状 | 分类 |
| --- | --- | --- |
| completion writeback 未发出 | DMA done 但 memory 无 completion | DMA 内部状态机问题 |
| writeback 与 data write 共路被排队 | completion 偶发延迟很长 | 性能长尾 |
| completion write fault | fault/error status 存在 | fault |
| CPU cache 仍有旧 completion | memory 已写，软件读旧值 | 可见性错误 |
| interrupt 早于 completion visible | ISR 读到空队列 | ordering 错误 |
| interrupt 被 mask 或 pending 丢失 | polling 可见 completion，但 ISR 不来 | interrupt path 问题 |
| clear/EOI 顺序错误 | 重复中断或丢新 completion | 软件/寄存器语义问题 |
| queue pointer 更新顺序错误 | completion record 存在但 driver 不消费 | queue metadata 错误 |

这些根因分布在不同路径。只看 DMA data port 无法解释 completion 丢失；只看 interrupt 也无法证明 completion 已经对 CPU 可见。

## 排查顺序

| 步骤 | 问题 | 观察点 |
| --- | --- | --- |
| 1 | 数据搬运是否真的完成 | data read/write response、DMA internal done |
| 2 | completion write 是否发出 | writeback AW/W 或等价 trace |
| 3 | completion write 是否收到 response | B response、writeback slot release |
| 4 | completion 是否对 CPU 可见 | memory snoop、cache invalidate、coherent read |
| 5 | interrupt 是否在 completion 可见后触发 | interrupt assert timestamp |
| 6 | CPU 是否正确读取和清理 | ISR read、clear/EOI write、queue pointer |
| 7 | error path 是否释放资源 | fault status、DMA channel slot |

这个顺序先区分“硬件没写 completion”和“软件没看见 completion”。这两个问题的修复方向完全不同。

## 例子：Interrupt 早于 Completion 可见

| 阶段 | 事件 | 结果 |
| --- | --- | --- |
| T0 | DMA data write 完成 | 数据面完成 |
| T1 | DMA 写 completion record | writeback 进入 interconnect |
| T2 | DMA 立即 assert interrupt | CPU 被唤醒 |
| T3 | CPU ISR 读取 completion queue | completion write 尚未对 CPU 可见 |
| T4 | ISR 认为没有 completion | 软件可能睡回去或报错 |
| T5 | completion record 稍后可见 | 没有新的 interrupt，表现为丢 completion |

修复点不是“多发一次 interrupt”这么简单，而是建立 ordering：completion visible 必须先于 interrupt assert，或者 ISR 必须有可靠的 retry/polling 规则。

## 例子：Non-Coherent Completion Buffer

| 阶段 | 事件 | 风险 |
| --- | --- | --- |
| T0 | DMA 写 completion memory | memory 已有新值 |
| T1 | CPU ISR 读 completion | CPU cache 中仍是旧 cache line |
| T2 | driver 判断无 completion | 任务被误判为未完成 |
| T3 | CPU 后续 invalidate 后看到 completion | completion 看似“迟到” |

这个例子说明 completion 丢失可能没有任何 BUS error。硬件完成了写，软件读的是旧缓存副本。

## 观测点

| 观测点 | 要记录 |
| --- | --- |
| DMA data path | data read/write done、response error |
| writeback path | completion AW/W/B、writeback queue depth |
| memory/coherence | completion visible timestamp、cache invalidation |
| interrupt path | interrupt assert、pending、mask、delivery latency |
| ISR/software | completion read、queue consumer update、clear/EOI |
| error path | writeback fault、translation fault、timeout |

观测点要覆盖从 data done 到 software consumed 的整条链。只有 data path counter 无法证明 completion 是否可见。

## 修复与设计边界

| 修复方向 | 适用问题 | 注意点 |
| --- | --- | --- |
| completion writeback 独立 port/QoS | writeback 被 data write 拖住 | 增加接口和权限配置 |
| completion-before-interrupt ordering | interrupt 早到 | 需要硬件状态机保证或明确 barrier |
| coherent completion buffer | CPU cache 可见性问题 | 成本和一致性域要明确 |
| non-coherent invalidate/clean 规则 | 非一致性 DMA | driver 契约必须严格 |
| error completion | fault/timeout 后软件等待 | 错误也要释放 DMA slot |
| interrupt retry/polling fallback | interrupt 丢失或 mask | 避免无声停止 |

好的 completion 设计要把 success 和 error 都闭环。数据面失败也要给软件一个可见结果，否则 driver 只能等待超时。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| 数据已经搬完就说明任务完成 | 软件可见完成还依赖 writeback、cache、interrupt/status |
| interrupt 到了就说明 completion 已可读 | interrupt 只是通知，必须晚于 completion 可见 |
| completion 小，不会被堵 | 共用 write path 时，小 completion 也会排队 |
| coherent 系统不需要顺序约束 | coherence 不替代 completion-before-interrupt 的 ordering |

## 一句话理解

DMA completion 是 `writeback + 可见性 + 通知 + 清理` 的联合结果，任何一环断开，软件都会看到“任务没完成”。

## 建模启示

这个案例要把 data done 和 software-visible done 分成两个状态。Resource 包括 DMA writeback port、completion buffer、cache/coherence path、interrupt controller、status register 和 queue metadata；Topology 决定 completion 经过哪条 write path 和 interrupt path；Interaction 包括 writeback、completion visibility、interrupt assert、ISR read 和 clear/EOI；Capability 包括 coherent/non-coherent 契约、error completion、ordering 和 observability。

事件模型建议显式表达 `dma_data_done`、`completion_write_issue`、`completion_write_response`、`completion_visible_to_cpu`、`interrupt_assert`、`isr_completion_read`、`interrupt_clear_done`、`dma_slot_release`。这些事件能区分数据面完成、完成记录写出、CPU 可见和软件消费四个不同阶段。
