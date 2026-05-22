# IOMMU Fault 案例卡

上级：[06 典型系统与案例](./README.md)

相关：[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)、[DMA Descriptor Fetch、Data Move 与 Writeback](../04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)、[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)、[Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)

## 现象

设备或 DMA 发起访问后，IOMMU/SMMU 报 translation fault、permission fault、context fault 或 walk fault。软件看到 DMA 任务失败、设备反复重试、fault interrupt，或者 driver 等待 completion 超时。

这个案例的关键不是“DMA 坏了”或“memory 坏了”，而是翻译层拒绝了某个带身份的 DMA 子事务。定位时要先回答：哪一个 stream/context、哪一个 IOVA、哪一类访问、发生在 descriptor fetch、data read、data write 还是 completion writeback。

## 典型路径

```text
DMA / device
  -> stream ID / context
  -> IOVA + attributes
  -> IOMMU/SMMU lookup
      -> TLB hit: permission check
      -> TLB miss: page table walk
      -> fault record / response
  -> translated PA request
  -> memory / target
```

| 阶段 | 期望事件 | Fault 风险 |
| --- | --- | --- |
| T0 | DMA 发起 request，带 stream ID/IOVA | stream ID 错或 context 缺失 |
| T1 | IOMMU context lookup | context fault |
| T2 | TLB lookup 或 page walk | translation fault / walk fault |
| T3 | permission check | read/write/secure 权限不匹配 |
| T4 | translated request 发出 | output PA 被 firewall 拒绝 |
| T5 | fault record 和 interrupt | fault 可见性或清除路径失败 |

## Fault 类型矩阵

| Fault 类型 | 发生位置 | 典型原因 | 和 memory error 的区别 |
| --- | --- | --- | --- |
| context fault | context lookup | stream ID 未配置、substream 错 | data request 尚未发往 memory |
| translation fault | page table translation | IOVA 未映射、entry invalid | memory controller 没看到原始访问 |
| permission fault | permission check | 写只读、非安全访问安全页 | 目标 memory 可能完全正常 |
| walk fault | page table walk | 页表所在地址不可访问或权限错误 | fault 发生在 page table read |
| output address fault | translated PA 检查 | PA 超出允许范围或 firewall 拒绝 | 翻译成功但输出路径非法 |

fault 的价值是给出明确错误语义。若 fault record 不完整，调试会退化成“DMA 没完成”。

## 分段归因

同一个 DMA 任务可能有多种子事务，每种子事务使用的地址和权限不同。

| 子事务 | 访问对象 | 常见 fault | 影响 |
| --- | --- | --- | --- |
| descriptor fetch | descriptor ring / queue entry | descriptor IOVA 未映射、read permission 缺失 | 任务无法启动 |
| source data read | source buffer | source buffer 未映射或权限不允许读 | data move 失败 |
| destination data write | destination buffer | write permission 缺失、buffer 生命周期结束 | partial 或 no data write |
| completion writeback | completion queue / status memory | completion buffer 未映射或写权限缺失 | 数据可能完成，但软件看不到完成 |
| page walk | page table memory | 页表自身不可访问 | 多个事务连续 fault |

排查时不能只看 fault address。要把 fault address 映射回 DMA 子事务：它是 descriptor 地址、source 地址、destination 地址、completion 地址，还是 page table walk 地址。

## 排查顺序

| 步骤 | 问题 | 观察点 |
| --- | --- | --- |
| 1 | faulting stream/context 是谁 | stream ID、device ID、substream ID |
| 2 | faulting IOVA 属于哪段 buffer | descriptor/source/destination/completion/page table |
| 3 | 访问类型是什么 | read/write、secure/non-secure、privileged、cache/shareability |
| 4 | 页表 entry 是否存在且权限匹配 | mapping、permission、valid bit |
| 5 | TLB invalidation 是否完成 | stale translation、old permission |
| 6 | fault 后 DMA 如何闭环 | error completion、interrupt、retry、slot release |
| 7 | 软件 buffer 生命周期是否仍有效 | unmap/free/reuse 与 DMA outstanding |

这个顺序把 fault 从“翻译失败”拆成身份、地址、权限、时序和完成语义。

## 例子：Descriptor Fetch Fault

| 阶段 | 事件 | 结果 |
| --- | --- | --- |
| T0 | CPU 建立 data buffer mapping | source/destination 已映射 |
| T1 | CPU 忘记映射 descriptor ring | descriptor IOVA 无 entry |
| T2 | CPU 写 doorbell 启动 DMA | DMA task active |
| T3 | DMA 发起 descriptor read | IOMMU 看到 stream ID + descriptor IOVA |
| T4 | context 存在，但 page table entry invalid | translation fault |
| T5 | DMA 没有发起 data read/write | memory controller 看不到数据事务 |
| T6 | fault interrupt 到 CPU | driver 看到 DMA 启动后 fault |

这个例子里 fault 发生在 descriptor fetch。若只看 source/destination buffer 映射，会误以为 IOMMU 配置没问题。

## 例子：Completion Writeback Fault

| 阶段 | 事件 | 结果 |
| --- | --- | --- |
| T0 | DMA 成功读源并写目的 | data move 完成 |
| T1 | completion queue 被软件提前 unmap | completion IOVA 失效 |
| T2 | DMA 写 completion record | IOMMU permission/translation fault |
| T3 | data buffer 内容正确 | 软件仍等不到 completion |
| T4 | fault status 指向 completion IOVA | 根因在 writeback 路径 |

这个例子表面像 DMA completion 丢失，真正问题是 completion writeback fault。data path 正常不能证明任务能被软件闭环。

## Fault 后的系统行为

| 行为 | 收益 | 风险 |
| --- | --- | --- |
| 写 fault record + interrupt | 软件可诊断 | fault record path 也要可见 |
| 返回 error response 给 DMA | DMA 可生成 error completion | DMA 必须释放 slot |
| 自动 retry | transient fault 可能恢复 | mapping 错误时会反复占用资源 |
| 停止 channel | 避免继续破坏状态 | 需要清晰恢复流程 |
| 生成 error completion | driver 能闭环任务 | completion buffer 若也 fault，会再次失败 |

fault 后必须释放或冻结资源到可恢复状态。若 translation fault 不触发 completion/status/interrupt，软件只会看到任务 hang。

## 观测点

| 观测点 | 要记录 |
| --- | --- |
| request input | stream ID、substream/context、IOVA、access type |
| context lookup | context hit/miss、permission set |
| TLB/page walk | hit/miss、walk address、walk fault |
| permission check | read/write/secure/privileged result |
| fault record | fault type、IOVA、stream ID、transaction type |
| DMA response | error completion、retry、channel stop、slot release |
| software path | fault interrupt、status read、clear/retry |

这些信息缺一项，fault 归因就会变慢。尤其要记录 transaction type，否则 descriptor fault 和 data fault 容易混在一起。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| IOMMU fault 等于 memory controller 问题 | fault 发生在翻译/权限层，data request 可能没到 memory |
| fault address 一看就知道原因 | 还要知道 stream/context、访问类型和子事务阶段 |
| data buffer 映射正确就够 | descriptor、completion、page table memory 也需要合法映射 |
| fault 后重试一定能恢复 | 权限或 mapping 错误会反复 fault 并占资源 |

## 一句话理解

IOMMU fault 的核心是定位“哪个带身份的 DMA 子事务，在什么地址语义和权限下被翻译层拒绝”。

## 建模启示

这个案例要把 IOMMU/SMMU 建模成 DMA path 上的身份、翻译和权限状态机。Resource 包括 context table、TLB、page walk port、fault record、DMA channel slot 和 completion path；Topology 决定 IOMMU 位于 device、DMA、interconnect 还是 memory fabric 前；Interaction 包括 stream/context lookup、translation、permission check、fault response、retry/error completion；Capability 包括隔离、虚拟化、fault reporting、TLB invalidation 和 resource release。

事件模型建议显式表达 `dma_subtxn_issue`、`context_lookup`、`translation_hit_or_miss`、`page_walk_issue`、`permission_check_fail`、`iommu_fault_record`、`fault_interrupt_assert`、`dma_error_complete`、`fault_clear_done`。这些事件能把 descriptor fault、data fault、completion fault 和 page-walk fault 区分开。
