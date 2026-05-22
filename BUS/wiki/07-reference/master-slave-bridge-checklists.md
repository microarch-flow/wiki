# Master/Slave/Bridge 设计清单

上级：[07 术语与检查清单](./README.md)

相关：[BUS 设计检查清单](./bus-design-checklist.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)

## 使用方式

这份清单按角色检查。Master、slave、bridge 可以各自局部正确，但组合后仍可能出现 response 不回、错误被吞、回压扩散、ordering 被破坏。评审时要确认三类角色对同一笔 transaction 的完成条件一致。

## Master 侧

| 检查项 | 要回答的问题 |
| --- | --- |
| 发起能力 | master 能发多少 outstanding，是否按 read/write、ID、channel 区分 |
| ID 分配 | ID 是否映射到 queue/channel/task，是否引入不必要保序 |
| burst 生成 | AxLEN/AxSIZE/AxBURST 是否考虑 4KB 边界、对齐和目标能力 |
| attribute | cacheability、shareability、secure、QoS 是否来自正确的软件/硬件配置 |
| backpressure | READY 低时 master 是否保持 payload 稳定，是否有 retry/timeout |
| response 处理 | R/B response 是否匹配 ID，错误是否能传给软件或内部状态机 |
| 流量分类 | descriptor、data、writeback、debug/control 是否能区分 QoS 和观测 |
| recovery | response 长时间不回时，是否能 timeout、abort、reset 或上报 |

Master 的关键责任是“不乱发”和“能收尾”。发起更深 outstanding 可以提升吞吐，但也要求更强的 ID 管理、错误恢复和 response path 观测。

## Slave 侧

| 检查项 | 要回答的问题 |
| --- | --- |
| 地址窗口 | decode 命中范围、alias、权限和非法地址行为是否定义 |
| 接收承诺 | 接收 request 后是否一定能返回 data/response/error/timeout |
| service time | 慢路径、wait state、PREADY/HREADY、controller queue 是否有上界或 timeout |
| partial access | narrow transfer、byte strobe、unaligned access 是否支持或明确报错 |
| side effect | read-clear、write-one-to-clear、FIFO pop、command write 是否定义 |
| low power/reset | clock off、reset asserted、power off、isolation 状态下访问如何响应 |
| error response | decode/slave/internal/ECC 等错误如何编码和释放资源 |
| observability | 能否记录 last request、error source、busy/wait、max latency |

Slave 的关键责任是“接了就要闭环”。如果某些状态下不能服务访问，就要在接收前 backpressure、在边界拦截，或在 timeout/error 路径闭环。

## Bridge 侧

| 检查项 | 要回答的问题 |
| --- | --- |
| 协议转换 | 上游 transaction 到下游 transaction 是否一一对应，还是拆分/聚合 |
| ordering | 拆分、合并、ID remap 后，原本 ordering 是否保持 |
| CDC | 异步 FIFO/handshake、reset crossing、满空状态是否定义 |
| width adaptation | byte lane、WSTRB、read-modify-write、MMIO side effect 是否正确 |
| burst handling | burst 是否被拆分、截断、拒绝或转换为 single access |
| error mapping | 下游 PSLVERR/SLVERR/timeout 如何映射到上游 response |
| resource release | 子事务错误或 timeout 后，bridge slot 是否释放 |
| backpressure | bridge 满时反压到哪个 channel，是否影响无关目标 |
| observability | 是否有 accept、downstream issue、child done、response release 事件 |

Bridge 的关键责任是“转换语义而不丢语义”。它不是胶水逻辑，而是协议能力、时钟节奏、位宽粒度、错误和完成条件的转换边界。

## 组合检查

| 组合问题 | 检查方式 |
| --- | --- |
| master 发得比 slave 能接得多 | 对比 outstanding、slave slot、bridge queue |
| slave 慢导致全局阻塞 | 看队列按 master/target/ID/channel 如何划分 |
| bridge 收缩能力但软件不知道 | 检查 burst/outstanding/ordering 是否在文档中降级 |
| error 返回层级不一致 | 注入 decode/slave/timeout/fault，确认软件看到的来源 |
| response path 比 request path 更早堵 | 检查 R/B FIFO、return arbiter、master READY |

## 观测点

| 角色 | 观测点 |
| --- | --- |
| Master | issue attempt、request accept、outstanding age、response match、error seen |
| Slave | request accept、service start/done、busy/wait、error source、timeout |
| Bridge | upstream accept、downstream issue、split/merge state、child response、response release |
| Shared | queue high watermark、arbiter grant、backpressure、resource release |

## 一句话理解

Master 负责正确发起并接收完成，slave 负责接收后闭环，bridge 负责转换时不丢失顺序、错误和完成语义。

## 建模启示

角色清单可以直接转成事件模型。Master 侧关注 `request_issue`、`id_allocate`、`response_match`；slave 侧关注 `request_accept`、`service_done`、`error_generate`；bridge 侧关注 `bridge_accept`、`child_txn_issue`、`child_txn_done`、`response_release`。

系统模型要检查这些事件是否能闭环：每个 accepted request 最终必须走到 data/response、error、timeout 或 abort；每个错误路径必须释放 Resource；每个 bridge 转换必须保留 Interaction 的必要顺序和 Capability 边界。
