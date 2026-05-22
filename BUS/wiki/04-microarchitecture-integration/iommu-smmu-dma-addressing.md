# IOMMU、SMMU 与 DMA 寻址

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)、[AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)、[DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)、[PCIE Wiki: IOMMU、地址翻译与设备隔离](../../../PCIE/wiki/03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

DMA master 发出的地址不一定是最终 memory physical address。IOMMU/SMMU 把设备侧地址转换成系统物理地址，并在转换过程中检查权限、隔离不同设备或虚拟机、产生 fault、触发 page walk。

对 BUS 建模来说，IOMMU/SMMU 不是“地址旁边多查一张表”。它插在 DMA request path 上，会改变请求延迟、可观察 fault、backpressure、sideband 属性、调试入口和错误归因。一次 DMA read/write 可能先被翻译层接收，然后命中 TLB 继续前进，也可能因为 miss 引出额外 memory transaction 去读页表。

## 为什么 DMA 需要翻译和隔离

没有翻译层时，device 直接用系统物理地址访问 memory。这种模型简单，但在多进程、虚拟化和安全隔离下风险很高。

| 需求 | 没有 IOMMU/SMMU 的问题 | 引入后的收益 |
| --- | --- | --- |
| 设备隔离 | device 可写错地址或越权访问 | 按 device/stream 限制可访问范围 |
| 虚拟化 | guest 不能直接暴露 host physical address | IOVA/GPA 到 PA 的受控转换 |
| buffer 管理 | DMA buffer 必须物理连续或受限 | 可映射分散 physical pages |
| fault 诊断 | 越界 DMA 可能破坏 memory 后才暴露 | fault 可定位到 device、地址和权限 |
| 热迁移/重映射 | device 地址视图僵硬 | 软件可更新映射和权限 |

设计 trade-off 是性能与保护。关闭翻译层延迟最低，但隔离最弱；启用翻译层增加 TLB、page walk、fault 和配置成本，但把 DMA 从“裸 master”变成受控 master。

## DMA Request Path 如何被改写

一个 DMA request 经过 IOMMU/SMMU 后，路径从单纯访存变成“翻译 + 权限 + 原始访问”两段。

```text
device / DMA
  -> interconnect or local port
  -> IOMMU/SMMU translation lookup
      -> TLB hit: translate + permission check
      -> TLB miss: page table walk through BUS
      -> fault: record + response / abort
  -> translated request to memory fabric
  -> memory controller / SRAM / coherent interconnect
```

| 阶段 | 输入 | 输出 | 建模状态 |
| --- | --- | --- | --- |
| request accept | stream ID、IOVA、read/write、attributes | translation lookup | `dma_req_accept`、translation queue occupancy |
| TLB hit | cached mapping | PA + permissions | `translation_hit`、额外固定延迟 |
| TLB miss | no mapping in TLB | page walk request | `translation_miss`、page walk outstanding |
| permission check | translated mapping | allow 或 fault | access type、privilege、security state |
| translated issue | PA + attributes | memory BUS transaction | downstream outstanding +1 |
| response | data/write ack/fault | device visible completion | `dma_resp_return` 或 `iommu_fault_record` |

这条路径说明，DMA 性能问题可能卡在 translation queue、TLB miss、page walk memory access、fault handling 或下游 memory fabric，而不是只卡在 memory controller。

## Stream ID、Context 与权限

IOMMU/SMMU 需要知道“谁在访问”。这个身份可能来自 stream ID、device ID、requester ID、substream ID、security state 或虚拟化上下文。

| 标识 | 作用 | 错误配置后果 |
| --- | --- | --- |
| stream/device ID | 选择设备上下文 | 设备使用错误页表或权限 |
| substream/context ID | 区分同一设备内部多个地址空间 | 多队列、多 VM 场景互相污染 |
| read/write attribute | 判断访问权限 | 写保护失效或合法访问被拒绝 |
| secure/non-secure | 区分安全世界和普通世界 | secure memory 暴露或访问失败 |
| cache/shareability attribute | 决定后续 memory path 行为 | cache 可见性和 coherence 错误 |

建模时不能只写“DMA 经过 IOMMU”。要把 identity、context lookup、translation table、permission bit 和输出属性都放入事务状态。否则同一个 IOVA 为什么对 device A 合法、对 device B fault，就无法解释。

## TLB Hit 与 Page Walk

翻译层内部会配置 TLB 或 translation cache 来降低重复翻译成本。命中时，DMA 请求只增加少量延迟；缺失时，IOMMU/SMMU 需要通过 BUS 读取页表，这会引入额外 transaction。

| 情况 | BUS 行为 | 性能影响 |
| --- | --- | --- |
| TLB hit | request 直接转换后继续访问 memory | 延迟低，吞吐接近无翻译路径 |
| TLB miss | 发起 page table walk read | 增加 memory read，占用 interconnect 和 memory 带宽 |
| page walk hit memory conflict | page walk 与 DMA data 竞争 DDR | DMA 自己制造额外 contention |
| invalid entry | 记录 fault，不再发出 data request | 设备看到错误或任务停止 |
| stale mapping | TLB 未失效或同步失败 | DMA 访问旧 physical page |

page walk 是 IOMMU/SMMU 对 BUS 的“侧向流量”。它可能走同一 DDR controller，也可能走独立端口。若模型把 translation miss 当成固定延迟，就会低估 DDR contention、QoS 和 timeout 风险。

## Fault 不是 Memory Controller 错误

IOMMU fault 表示翻译层拒绝或无法完成地址转换。它和 memory controller ECC、slave error、AXI decode error 是不同层级的错误。

| Fault 类型 | 发生位置 | 典型含义 |
| --- | --- | --- |
| translation fault | context/page table 缺失 | IOVA 没有合法映射 |
| permission fault | 权限位不允许 | 写只读页、非安全访问安全页 |
| context fault | stream/context 配置错误 | device ID 没有对应上下文 |
| walk fault | page table read 失败 | 页表所在 memory 或权限有问题 |
| output address fault | translated PA 不被下游允许 | firewall 或 physical range 限制 |

fault 的设计取舍是“返回给 device、上报给 CPU、还是让任务停住”。高可靠系统需要 fault record、interrupt、status register 和可恢复流程；简单系统可能把 fault 映射成 DMA engine error。BUS 模型要写清 fault 是否占用 response path、是否释放 DMA outstanding、是否触发 interrupt，以及 fault record 的 MMIO 可见性。

## 例子：Descriptor Fetch 触发 Translation Fault

考虑 DMA engine 启动后读取 descriptor，但 descriptor 地址没有正确映射。

| 阶段 | 事件 | IOMMU/SMMU 状态 | BUS 可见结果 |
| --- | --- | --- | --- |
| T0 | CPU 写 descriptor 到 memory | 映射应由软件提前建立 | 若 cache 未 clean，后续也可能读旧值 |
| T1 | CPU 写 DMA start MMIO | DMA task active | start 与 mapping 更新需要有顺序 |
| T2 | DMA 发起 descriptor read，带 stream ID + IOVA | translation lookup | 下游 memory request 尚未发出 |
| T3 | TLB miss，发起 page walk | page walk outstanding | DDR 上出现页表 read |
| T4 | 页表 entry invalid | fault record 生成 | descriptor read 被拒绝 |
| T5 | DMA engine 收到错误或停止任务 | outstanding release | completion 可能变成 error |
| T6 | CPU 通过 MMIO 读取 fault status | fault visible | 软件看到 faulting IOVA、stream ID、类型 |

这个例子说明：descriptor fetch fault 不是 DDR 没返回 descriptor，也不是 DMA data path 失败。故障发生在 translation path，且真正的 data memory request 没有发出。调试时若只看 memory controller，会找错层级。

## IOMMU 与 Coherence、Cache Maintenance

IOMMU/SMMU 解决的是地址转换和权限，不自动解决所有 cache 可见性问题。DMA 读写的数据是否与 CPU cache 一致，取决于 coherent path、shareability attribute、cache maintenance 和 barrier。

| 场景 | 需要关注 |
| --- | --- |
| CPU 更新页表后启用 DMA | 页表写入是否对 IOMMU page walk 可见 |
| CPU 更新 descriptor 后 DMA 读取 | descriptor cache clean 或 coherent visibility |
| DMA 写 completion 后 CPU 读取 | invalidate、coherent completion 或 memory ordering |
| 修改 mapping 后继续 DMA | TLB invalidation、completion wait、旧请求 drain |
| 多 device 共享 buffer | 每个 stream 的权限和 cache 属性是否一致 |

页表本身也是 memory 数据。软件更新页表后，需要确保 IOMMU/SMMU 的 page walk 能看到新 entry，并且旧 TLB entry 被失效。否则 BUS 上的 DMA request 可能继续使用旧 translation，即使软件以为映射已经更新。

## 放置位置与 Backpressure

IOMMU/SMMU 可以放在 device 附近、DMA 聚合入口、主互连前或 memory fabric 内部。放置位置影响回压和可观察性。

| 放置方式 | 收益 | 代价 |
| --- | --- | --- |
| per-device translation | 隔离清晰，fault 归因直接 | 面积和配置成本高 |
| shared SMMU before memory fabric | 集中管理，多 device 共享 TLB/page walk | translation queue 成为热点 |
| integrated in coherent interconnect | 属性和 coherence 结合紧密 | 调试边界更复杂 |
| near DMA engine | 延迟可控，局部 backpressure | 多 DMA/外设复用困难 |

若 shared SMMU 的 translation queue 满了，多个 device 的 DMA 都会被 backpressure；若 page walk 与 data path 共用 DDR，TLB miss 会降低有效数据带宽；若 fault record path 本身走 MMIO，CPU 读取 fault status 又依赖另一条 BUS 路径。模型要把这些路径分开。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| IOMMU fault 等于 memory controller 出错 | fault 发生在翻译/权限层，data request 可能从未到达 memory |
| 每次 DMA 都完整 page walk | TLB hit 不需要 page walk，miss 才产生额外 BUS 事务 |
| IOMMU 解决 cache 一致性 | IOMMU 解决地址和权限，cache 可见性还要看 coherence 和 maintenance |
| 关闭 IOMMU 只影响安全 | 也会改变地址视图、fault 行为、debug 归因和虚拟化模型 |

## 一句话理解

IOMMU/SMMU 把 DMA master 从“直接访存者”变成“带身份、权限、翻译和 fault 语义的 BUS 参与者”。

## 继续阅读

- 如果你在追 `DMA 任务链路是怎么被翻译层插入的`：看 [AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)
- 如果你在追 `descriptor fetch 和 data move 谁先 fault`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `IOMMU fault 现场该怎么拆`：看 [IOMMU Fault 案例卡](../06-scenarios-case-studies/iommu-fault-case-card.md)
- 如果你在追 `fault 与 hang 的定位入口差别`：看 [Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)

## 建模启示

IOMMU/SMMU 要建模成 DMA request path 上的翻译与权限状态机。性能模型要记录 translation queue、TLB 命中率、page walk outstanding、walk memory path、fault record path、backpressure 方向和下游 memory fabric 争用。功能模型要记录 stream ID、context、IOVA、PA、permission、security state、cache/shareability attribute、TLB invalidation、fault 类型和 DMA completion 行为。

事件模型建议显式表达 `dma_req_accept`、`context_lookup`、`translation_hit`、`translation_miss`、`page_walk_issue`、`page_walk_done`、`permission_check`、`translated_req_issue`、`iommu_fault_record`、`fault_interrupt_assert`、`dma_error_complete`。这些事件决定一次 DMA 是正常访存、翻译等待、权限失败，还是引出额外 BUS 流量并改变系统调试路径。
