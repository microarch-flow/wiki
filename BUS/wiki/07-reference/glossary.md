# 术语表

上级：[07 术语与检查清单](./README.md)

相关：[BUS 一页版总览](./bus-one-page.md)

## 基础角色

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| BUS | 片上事务互连层，覆盖 shared bus、bus matrix、crossbar、分层互连和 bridge 组合 | 不按“一根线”建模，要按 transaction path 和 service point 建模 |
| Fabric | 互连结构的宽泛统称，可包含 decoder、arbiter、buffer、bridge、adapter、crossbar | 需要拆出共享点、队列和返回路径 |
| Master / Initiator | 发起读写请求的一侧，例如 CPU、DMA、debug master | 记录发起能力、ID、outstanding、QoS、属性 |
| Slave / Target | 接收请求并返回数据、状态或错误的一侧，例如 SRAM、DDR controller、peripheral | 记录 service time、错误行为、backpressure 和 response |
| Agent | 跨协议或系统语境下的参与者统称 | 用于不想绑定 master/slave 命名的场景 |

本 wiki 正文优先使用 `master` 和 `slave`，在跨协议或更抽象语境里补充 `initiator` / `target`。

## 事务与顺序

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| Transaction | 一次从 request 到 response/error/completion 的完整访问行为 | 需要闭环到 slot release 或软件可见完成 |
| Beat | 一次 data channel 上的有效传输单位 | 与 bus width、byte lane、burst length 相关 |
| Burst | 多个 beat 组成的一组连续或规则访问 | 记录长度、大小、边界、拆分和合并 |
| Outstanding | 已发出但尚未完成的事务数量 | 受 master slot、ID、slave slot、return path 限制 |
| Ordering | 多个访问之间必须保持的可见顺序 | 区分同 ID、不同 ID、MMIO、barrier、completion 顺序 |
| Completion | 硬件任务完成后对软件或上游可见的记录、状态或事件 | 不等同于协议级 response |
| Write Response | 协议级写事务完成返回，例如 AXI `B` channel | 与 software completion record 分层建模 |

## 流控与共享

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| Arbitration | 多个请求竞争同一共享资源时的选择规则 | 记录策略、grant、wait、QoS 和 starvation bound |
| Backpressure | 下游无法接收或完成时向上游传播的节流 | 要追 request path 和 response path 两个方向 |
| Head-of-Line Blocking | 队头事务阻塞后续本可独立执行的事务 | 取决于队列按 master、target、ID 还是 channel 划分 |
| QoS | 用 priority、weight、deadline、limit 等机制分配服务能力 | 不是消除争用，而是改变等待分布 |
| Hotspot | 多个流量集中竞争同一 target、queue、controller 或 return path | 需要 per-target/per-master 指标 |

## 互连组件

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| Decoder | 根据地址和属性选择目标或错误路径 | 记录 address window、decode miss、default slave |
| Arbiter | 从多个候选请求中选择服务对象 | 记录仲裁点位置和 grant 条件 |
| Crossbar | 多输入多输出的并发连接组织 | 不等于无阻塞，仍受目标端口和 return path 限制 |
| Bridge | 在协议、位宽、时钟域或属性之间做转换 | 记录能力收缩、错误映射、buffer 和 completion 条件 |
| CDC | Clock Domain Crossing，跨时钟域传输和同步结构 | 记录 FIFO/handshake、reset、满空和额外延迟 |
| Width Adaptation | 不同数据位宽之间拆分、拼接、byte lane 重组 | 关注 WSTRB、partial access、MMIO side effect |
| Register Slice | 插入寄存器打断时序路径的互连组件 | 会改变 latency 和 backpressure 位置 |

## 协议与访问语义

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| MMIO | 通过内存映射地址访问设备寄存器 | 与普通 memory 分开建模，关注 side effect 和顺序 |
| Normal Memory | 面向数据存取和性能优化的内存访问对象 | 关注 cache、coherence、burst、locality |
| Cacheability | 访问能否进入 cache hierarchy 或受 cache 策略影响 | DMA、completion、MMIO 必须分开 |
| Shareability | 访问是否参与共享域和一致性语义 | 影响 CPU/DMA/NoC 可见性 |
| Barrier | 约束访问顺序和可见点的机制 | 不等于 cache clean/invalidate |
| Doorbell | 软件或上游通知设备有新任务的控制写 | 必须晚于 descriptor 可见 |
| Side Effect | 读写寄存器会改变设备状态 | debug read、polling、width adapter 都要谨慎 |

## 路径与调试

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| Request Path | 从 master 发出请求到 target 接收的路径 | 包含 decode、route、arbiter、bridge |
| Response Path | target 返回数据、状态或错误到 master 的路径 | outstanding 释放常卡在这里 |
| Return Path | Response Path 的同义别名 | 本 wiki 优先使用 Response Path |
| Control Plane | 配置、状态、doorbell、debug、boot、管理路径 | 关注正确性和软件可见性 |
| Data Plane | 大吞吐数据搬运路径 | 关注 bandwidth、burst、outstanding、QoS |
| Observability | counter、trace、错误状态和关键事件的可观测能力 | 必须覆盖 request、service、response、completion |
| Transaction Ledger | 调试时维护的事务账本 | 记录 request fire、ID、beat、response、slot release |

## 错误与异常

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| Decode Error | 地址没有命中合法目标或权限窗口 | 要有 default slave 或 error response |
| Slave Error | 目标接收访问后主动报告失败 | 与 decode error 区分来源 |
| Timeout | 等待超过阈值后由某层生成收尾事件 | 记录 timeout wrapper 和下游原始等待 |
| Fault | 访问被明确判定错误，例如 permission、translation、protocol fault | 记录原始 fault source 和映射 |
| Hang | 事务既不成功也不报错，失去 forward progress | 需要 last progress、outstanding age、resource release |
| Error Mapping | bridge/fabric 把下游错误转换成上游 response | 不能丢失错误来源 |

## 系统组件

| 术语 | 定义 | 建模关注点 |
| --- | --- | --- |
| IOMMU / SMMU | DMA path 上的地址翻译与权限检查组件 | 记录 stream ID、IOVA、context、fault、page walk |
| DDR Controller | 把 AXI/BUS transaction 调度为 DRAM command 的控制器 | 记录 queue、row/bank、scheduler、turnaround、return path |
| NoC | 面向大规模节点和数据交换的网络式片上互连 | 与 BUS 的边界在 NI/DMA/bridge/control register |
| Interrupt Controller | 汇聚和分发中断事件的组件 | 与 status、completion、clear/EOI 一起建模 |
| Debug Master | 用于调试访问的特殊 master | 关注权限、低功耗、reset、side effect 和干扰 |

## 建模启示

术语表不是命名表，而是模型边界表。每个术语都应该能回答：它是 Resource、Topology、Interaction 还是 Capability；它在哪里排队、在哪里转换、在哪里完成、在哪里报错；它的软件可见结果是什么。

建模时不要只保存协议字段名。更有用的是事件和状态：`request_accept`、`decode_miss`、`arbiter_grant`、`backpressure_assert`、`bridge_convert`、`response_return`、`fault_recorded`、`timeout_fire`、`completion_visible`、`resource_release`。
