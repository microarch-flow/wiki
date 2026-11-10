# 多维 DMA 与 Stride 地址生成

上级：[03 DMA 引擎微架构](./README.md)

相关：[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

为什么很多高性能 DMA 不能只支持线性搬运，而必须支持 stride、2D、3D 甚至 tensor-like 地址生成；以及这种灵活性到底是在省软件，还是在真正改变系统效率。

## 线性 DMA 为什么很快就不够

如果数据在源端和目的端都按连续线性布局出现，线性 DMA 已经足够。但真实系统很少这么干净。图像通常按行存放，带 pitch 和 padding；张量 tile 既有逻辑块边界，也有物理 SRAM bank 布局；KV cache、feature map、activation buffer 又常常要求源宿布局不同。软件当然可以用很多条线性 descriptor 把这些访问展开，但代价会非常明显：

- descriptor 数量膨胀
- submit 开销上升
- 小事务碎片化
- overlap 更难维持

所以 stride / 2D / 3D DMA 的本质，不是“更花哨的描述符”，而是把一部分规则地址生成逻辑从软件循环下沉到 DMA engine。

## 多维地址生成真正节省了什么

它节省的首先是软件控制流。软件不必再为每一行、每一面、每一个 tile 都单独提交一笔线性任务。它也可以减少 descriptor 和 completion 的控制碎片，但底层每行仍受协议、对齐和目标边界约束；事务数不一定减少。硬件有机会跨行优化，前提是地址连续、允许合并且不改变副作用。

把 stride DMA 想成按楼层和房间号自动派送比较贴切。软件不必每送一间房就重新写一次路线，只需要告诉系统“每层送多少间、层间隔多大、总共送几层”。这个类比的边界很明确：它只解释规则地址生成，不解释底层 burst 如何因 page、bank 或协议边界被拆分。

## 至少要看哪几个字段

一个最小 2D DMA 通常至少要表达：

- `active bytes`：每行真正要搬的数据量
- `src_pitch / dst_pitch`：源和目的分别相邻两行的起始地址差
- `repeat count`：总共重复多少行

3D 或更高维会继续叠加 plane stride、depth count 等字段。关键不是字段越多越强，而是表达能力是否刚好覆盖目标 workload 的规则性。表达过弱，软件仍要展开；表达过强，硬件验证和边界处理复杂度急剧上升。

## 2D 地址与边界例

对第 `r` 行，`src=s0+r×src_pitch`、`dst=d0+r×dst_pitch`，搬 `L` 个有效字节。例：`s0=0x1000,d0=0x2000,L=4,rows=3,src_pitch=8,dst_pitch=6`，三行分别是 `0x1000→0x2000`、`0x1008→0x2006`、`0x1010→0x200C`，每行搬 4 B；源分别跳过 4 B padding，目的跳过 2 B。

```text
for r in [0, rows):
  s = checked_add(s0, checked_mul(r, src_pitch))
  d = checked_add(d0, checked_mul(r, dst_pitch))
  split_and_transfer(s, d, L)  # 分别满足接口边界、权限与 byte mask
```

`rows=0` 或 `L=0` 的行为须由 IP 契约定义；若定义为空操作，不应产生数据访问。负 stride 仅在字段编码和实现支持时合法，需用有符号宽运算检查下溢/溢出。源目的区间重叠时，普通 DMA 未必具有 memmove 语义；除非设备明确保证方向与读取顺序，否则应拒绝或由软件处理。每一行还须按源目的边界分别拆分。

## 为什么它和 memory system 有强耦合

多维 DMA 最大的收益和最大的问题都来自它与下游 memory system 的耦合。一个 stride 看起来只是“每行跳过一些字节”，但落到 DRAM、HBM 或 local SRAM 上时，会直接改变：

- row locality 能否被利用
- bank/port 热点是否放大
- burst 是否被连续中断
- completion 是按整体任务还是按子块推进

这正是它和 [RAM wiki 的 row locality](../../../RAM/wiki/07-system-architecture/sram-vs-dram-access-pattern.md) 必须连起来看的原因。某些 tile 大小与 stride 组合在软件视角里很规则，到了 memory controller 视角却可能极度不友好。

## 什么时候 2D/3D DMA 反而不值

如果访问模式本身高度不规则，或软件早就必须为每块数据单独建立依赖与同步，那么把地址生成硬塞进 DMA 未必划算。此时多维字段只会增加 descriptor 复杂度和验证成本，真正的性能主因仍然可能是 irregular gather、translation miss 或 consumer 端口冲突。

所以多维 DMA 不是“凡有规则就该上”，而是“当规则性足够强，能显著减少 descriptor 膨胀并改善事务组织时才值”。

## 常见误解

常见误解：`支持 2D/3D DMA 就一定更高效`。实际上如果 stride 让 burst 被频繁截断，或者 row locality 变差，效率可能更低。

常见误解：`多维 DMA 只是少写点软件循环`。实际上它还会改变 descriptor 压力、completion 聚合方式和内存系统看到的流量形状。

常见误解：`一条多维任务天然比很多线性任务更好`。实际上前提是它所表达的模式足够规则，且硬件能有效利用这种规则。

## 一句话理解

多维 DMA 的价值不在于描述符更花哨，而在于把规则地址生成下沉到硬件，从而减少控制碎片化并改善数据供给组织。

## 建模启示

这页的关键是把“规则地址生成”和“底层事务展开”分成两层。event-driven 仿真中，建议先生成逻辑子块序列，再让每个子块经过统一的 burst/边界拆分模型。

一个够用的结构是：

```text
StridedTransfer {
  src_base; dst_base
  active_bytes_per_row
  src_pitch; dst_pitch
  row_count
}
```

若只关心高层估算，可以用 `repeat * active_bytes` 加一个 stride 惩罚系数；若关心 row locality、bank hotspot 或 completion 粒度，就必须显式展开每一行或每一块。
