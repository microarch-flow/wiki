# SRAM 设计与选型 checklist

上级：[参考资料](./README.md)
相关：[单口、双口、多口 SRAM，端口数为什么是关键代价](../02-sram-foundations/single-port-dual-port-multi-port.md), [为什么 SRAM 在先进制程下不再线性 scale](../02-sram-foundations/sram-process-scaling-challenge.md)

## 这页在回答什么问题

当需要做 SRAM 规格定义、IP 选型或架构评审时，应该按哪些问题逐项检查，才能不漏掉端口、容量、Vmin、banking 和功耗这些关键约束。

## 正文

这份 checklist 的目标不是替你完成 SRAM 设计，而是避免在规格定义、IP 选型、架构评审和模型抽象时漏掉最容易晚爆雷的约束。SRAM 相关问题最常见的失败模式，不是完全不知道某件事，而是只看了容量和名义延迟，就过早假设“这块 SRAM 大概能用”。真正到后面实现时，才发现端口数爆了、bank 冲突压不住、Vmin 不过、retention 状态没想清、或者这块 SRAM 的系统角色和它的组织方式根本不匹配。

因此，这份清单按一个比较稳的顺序排：先确认这块 SRAM 在系统里到底扮演什么角色，再往下检查它的访问语义、端口与并发、阵列组织、功耗与工艺边界，最后再看模型是否把关键状态保留下来。这个顺序不是唯一正确顺序，但它能最大限度避免“先把物理东西定死，后面才发现系统语义不对”的返工。

## 1. 先确认它在系统里是什么资源，不要只写“on-chip SRAM”

先回答：

- 它是 `register file`、`cache`、`scratchpad`、`TCM`，还是 `weight/activation/accumulator buffer`？
- 里面放什么由谁决定：固定逻辑、硬件替换、编译器、软件还是 DMA 调度？
- 它更偏“操作数仓库”“局部 staging”“重用驻留池”还是“确定性服务区”？

如果这一层没说清，后面很多参数都无从判断。因为同样 1 MB SRAM，做 cache、做 activation buffer、做 TCM，合理组织方式会完全不同。

## 2. 先问访问语义，再问名义容量

先回答：

- 是读主导、写主导，还是高频读改写？
- 访问是否必须确定性完成，还是允许 miss / refill / backpressure？
- 数据生命周期是短暂滚动、长时间驻留，还是局部反馈回路？
- 是否需要支持 refill 与当前消费重叠？

如果这一步没做，最常见的后果是：容量看起来够，但真实读写模式与结构不匹配。比如把高频 psum 回路当普通输入 buffer 设计，或者把需要双缓冲的 activation buffer 当单槽 staging 区处理。

## 3. 端口需求要从真实并发来源反推，不能只写“需要多读多写”

先回答：

- 并发来自哪里：同拍多操作数读取、多个 consumer 并发、DMA 与 compute 重叠，还是局部读改写？
- 需要真多端口，还是可以靠 banking、replication、time-multiplexing 替代？
- 读写是否必须同拍完成，还是允许流水错开？

如果这一步草率，后果通常最重。真多端口会迅速推高 bitcell 和阵列代价；反过来，如果误以为 banking 能替代一切，又可能在关键热点上出现结构性冲突。

## 4. 容量不要从“总预算剩多少”正推，要从工作集和重用窗口反推

先回答：

- 这一级至少要容纳哪个 `working set` 才有意义？
- 多给容量买到的是更长驻留，还是只是更低利用率的大池子？
- 当前 tile / block / burst 的自然粒度是什么？
- 容量缩小之后，外层回取频率、片上冲突和 stall 会怎么变？

如果只按剩余面积拍容量，最常见的后果是：做出一块“看起来不小”的 SRAM，但它既不够支持关键重用，也大不到能真正改变外层流量。

## 5. banking 和作用域要一起定，不要把 bank 只当后期实现细节

先回答：

- bank 是按 `PE`、`cluster`、`function` 还是 `address interleave` 切？
- 这块 SRAM 是局部私有、局部共享，还是全芯片共享？
- 消费者的读出几何形状和 bank 切分是否对齐？
- 是否会出现某些 bank 长期热点，而其他 bank 空闲？

如果这一步没处理好，典型后果是：总容量和总带宽都不低，但局部 bank hotspot 或跨 cluster 扇出把吞吐拖死。

## 6. 别只写总带宽，要拆读带宽、写带宽和同周期组合

先回答：

- 每拍最多需要多少读、多少写？
- 同一时刻是否既要 refill，又要消费，又要 drain？
- 读写是否共享同一组 bank、同一路径、同一仲裁点？
- 某条局部反馈路径是否比总带宽更早撞墙？

如果只看总带宽，很容易忽略最真实的问题：某类流量在某一时间相位内集中爆发，导致局部服务能力不够。

## 7. 时序目标要明确：你是在追单拍访问、固定几拍，还是允许流水

先回答：

- 这块 SRAM 的读写时延能否固定成常数？
- 同拍读写冲突语义是什么？
- 是否允许更深流水来换频率？
- 上层是否依赖严格一拍返回，还是能接受调度器插空？

如果时序语义没定清，后果往往是系统接口先假定得太乐观，后面为收敛频率被迫加 pipeline，却连带改动大量上层逻辑。

## 8. 工艺与稳定性边界必须提前问，不要默认“逻辑能做，SRAM 也能做”

先回答：

- 目标工艺节点下的 bitcell 面积、Vmin、SNM 和波动边界是否已知？
- 低电压模式下，是 hold 先坏、read 先坏，还是 write-ability 先坏？
- 容量做大之后，yield、margin 和测试压力怎样变化？

如果这一步晚想，典型后果是：架构侧已经把这块 SRAM 当成既大又低压的理想资源，但物理上根本不稳。

## 9. 功耗状态不要只写 active power，要把 retention 和唤醒也拉进来

先回答：

- 这块 SRAM 会长期 active，还是大量时间 idle？
- 是否需要 `light sleep`、`retention`、`deep sleep`？
- 唤醒延迟和唤醒能耗是否会破坏上层时序假设？
- low-power 粒度是整块、按 bank，还是按更小分区？

如果这一步忽略，后果常常不是“功耗略高”，而是系统空闲策略根本无法用，或者省下的 leakage 被频繁唤醒成本吃回去。

## 10. 测试与可观测性要留接口，不然排障成本会非常高

先回答：

- 是否需要 ECC / parity / BIST / redundancy？
- bank 冲突、fill/drain、sleep/wake 状态是否可观测？
- 出问题时，能否区分数据没来、bank 被占、端口冲突还是低功耗状态未恢复？

如果完全没有可观测性，后期你会看到“阵列偶发饿住”或“功耗异常”，但很难定位到底是功能问题、时序问题还是调度问题。

## 11. 最后再检查：模型是不是把关键约束都保留下来了

先回答：

- 模型里有 `bank_count`、`ports_per_bank`、`read/write asymmetry` 吗？
- low-power 状态是否被保留，还是被抹平成永远 active？
- 这块 SRAM 的系统角色语义是否被保留，还是所有片上 SRAM 都被压成一个统一池子？
- 是否能统计 stall 的具体原因，而不只是“buffer busy”？

如果模型阶段就把这些约束压没了，后面很多设计空间比较都会失真，看起来像“面积差不多，性能也差不多”，但真实实现会完全不是一回事。

## 最后再看一遍：最常见的漏项是什么

如果时间很紧，至少别漏下面这些：

- 资源角色没定义清楚
- 真多端口需求被低估
- bank 热点和作用域没分析
- 总带宽写了，但同周期流量组合没拆
- Vmin / retention / wake-up 语义没考虑
- 模型把所有片上 SRAM 压成同一种资源

这几项是最常见、也最容易造成后期返工的地方。

## 一句话理解

SRAM 设计评审最怕的不是“不够大”，而是角色、端口、banking、低功耗和建模语义这几层有任何一层提前被想当然地压平了。

## 建模启示

这份 checklist 最适合直接映射成一组结构化字段，作为选型表或模型输入模板：

```text
SramReviewItem {
  role: enum
  access_pattern: enum
  required_concurrency: str
  capacity_bytes: int
  bank_count: int
  scope: enum
  read_bw_Bps: float
  write_bw_Bps: float
  latency_cycles: int
  low_power_modes: set
  wakeup_cycles: int
  observability_features: set
}
```

如果某块 SRAM 连这些字段都填不完整，通常说明方案还停留在“有一块本地 SRAM 应该够了”的阶段，还没有准备好进入严肃比较或实现讨论。
