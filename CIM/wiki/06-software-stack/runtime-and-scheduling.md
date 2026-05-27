# Runtime 与调度：Write 慢、Read 快的非对称性如何被利用

上级：[06 Software Stack](./README.md)
相关：[Host Integration](../05-architecture-and-system/cim-system-integration-with-host.md), [BUS: AXI DMA System Interface](../../../BUS/wiki/04-microarchitecture-integration/axi-dma-system-interface.md), [NoC: DMA Engine Interaction](../../../NoC/wiki/05-system-integration/dma-engine-noc-interaction.md), [RAM: DRAM Commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md), [FAB: Reliability](../../../FAB/wiki/05-final-test-and-reliability/reliability-jedec-standards.md)

## 这页在回答什么问题

CIM runtime 真正在调度什么？不是只启动 kernel，而是管理权重驻留、read/write 非对称、buffer 双缓冲、DMA、tile 占用、校准、fallback 和 host completion。

## Runtime 的职责

```text
load / pin weights
  -> schedule activation streams
  -> manage tile buffers and partial sums
  -> trigger calibration or health checks
  -> coordinate fallback execution
  -> DMA writeback and completion
```

BUS wiki 的 DMA、doorbell、interrupt 和 IOMMU 路径决定 host 侧成本；NoC 的 DMA interaction 决定片上搬运能否和计算重叠。

## Write 慢、Read 快的路线差异

ReRAM/Flash/PCM analog CIM 写入慢、verify 重、endurance 有限，runtime 应尽量长期驻留权重，把 workload 组织成少写多读。频繁在线更新、training 或动态专家切换会削弱这类路线。

SRAM digital/mixed-signal CIM 写入快得多，runtime 可以更灵活地 reload 权重或切换模型，但仍要管理 bit-serial cycle、local buffer 和 NoC traffic。

DRAM/HBM/GDDR-PIM 的 runtime 关注 memory command、bank/channel offload 和 result return，不是 CIM array write；RAM wiki 的 ACT/RD/WR/PRE command timing 是这类接口的背景。HBM base die/interposer/package-side NMC 则关注 package bandwidth、DMA 和 accelerator scheduling。

## 调度策略

Weight residency scheduling 决定哪些层、专家或 tile 权重常驻。Activation streaming 决定输入是否能持续喂饱 array。Partial-sum scheduling 决定 local、tile 还是 chip 级合并。Fallback scheduling 决定 unsupported op 是否会打断流水。

调度粒度越小，硬件利用率可能越高，但 host synchronization、DMA descriptor、cache coherency 和 completion interrupt 成本上升。小 batch、decode token-by-token 和动态控制流尤其容易暴露这个问题。

## 一句话理解

CIM runtime 的核心是把“少写多读、局部计算、混合执行”变成稳定调度计划，而不是机械启动一个矩阵乘 kernel。

## 工具链启示

runtime 需要可见 weight residency、write cost、tile availability、NoC contention/backpressure、reduction location、calibration state、fallback cost、DMA overlap 和 host stall。调度器应优先把写慢 memory 用在固定权重高复用子图，把频繁变化或控制复杂的子图留给数字路径。
