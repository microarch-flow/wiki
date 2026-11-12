# 地址、描述符与 Burst

上级：[02 基础对象与传输语义](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[BUS：AXI Burst、Alignment 与 Boundary](../../../series/interconnect/BUS/wiki/03-on-chip-protocol-families/axi-burst-alignment-boundary.md)

## 这页在回答什么问题

为什么很多 DMA 的性能、灵活性和复杂度，最终都会收敛到 descriptor、burst 和边界拆分上；以及为什么“一个 descriptor”几乎从来不等于“一笔总线事务”。

## 先把三层语义分开

这页最重要的不是记 descriptor 里有哪些字段，而是先把三层语义拆开：

- `descriptor-level`：软件写给 DMA 的任务描述
- `logical transfer-level`：软件眼里的一笔搬运任务
- `transaction-level`：真正落到互连上的 read/write burst 或 packet

很多 DMA 误解都来自把这三层压成一层。一个 descriptor 可以对应一笔逻辑任务，而这笔逻辑任务在 AXI 上会拆成多笔 `AR/AW` 请求和对应的 `R/W/B` 流；在 PCIe 上又可能变成多个 TLP。后面你在 [BUS wiki 的 AXI 五通道](../../../series/interconnect/BUS/wiki/03-on-chip-protocol-families/axi-five-channels-handshake.md) 看到的通道行为，本质上就是 DMA 把上层任务翻译到底层事务后的样子。

## 为什么 DMA 会从寄存器编程演化到 descriptor

最早的 register-programmed DMA 并不神秘：CPU 把 `src/dst/len/control` 写进寄存器，启动一次传输，等 done，再写下一次。这种方式在任务数量少时完全足够。问题出在任务变碎、变多、变频繁之后。假设网络接收路径里有一串分散的 buffer，或者 AI runtime 需要连续提交很多 tile 搬运，CPU 若每次都重新写寄存器，控制开销会迅速吞掉系统收益。

descriptor 的设计动机正是把这种重复控制劳动批量化。软件先把多笔传输的参数写进内存，DMA 再自己去取、自己执行、自己更新完成状态。linked-list descriptor 像一串预先放在工位边上的任务单，DMA 做完一张就拿下一张；这个类比对线性链表成立，但对 ring descriptor 要立刻补边界，ring 更像循环复用的工位槽位，关键问题是 producer 和 consumer 指针不能撞车。

## 一个 descriptor 通常至少要回答什么

一个最小 descriptor 往往至少包含：

- source address
- destination address
- transfer length
- control flags
- next pointer 或 queue index

更复杂的系统还会加 stride、二维形状、优先级、completion token、ownership bit，甚至 fault policy。字段变多不是为了“花哨”，而是因为 DMA 被要求承担的系统语义变多了。比如支持二维 stride，不是为了把 descriptor 写得更复杂，而是为了避免软件用一大串线性 descriptor 去展开一个规则二维访问。

## Burst 决定的不是“搬多少”，而是“怎么占用系统”

descriptor 解决的是任务描述问题，burst 解决的是事务粒度问题。它并不改变逻辑上总共要搬多少字节，但会改变系统看到的 traffic shape。burst 过短，header 和握手开销占比高，memory latency 难隐藏；burst 过长，容易长时间占住链路，伤害小请求和高优先级控制流。

把 burst 想成高速公路上的编队通行窗口比较合适。单车一辆辆放行，管理开销高；整队放行，单位成本低。但这个类比的边界也很清楚：真实总线还有对齐、4KB 边界、最大 burst 长度、response return path 这些约束，所以“编队越大越好”并不成立。

## 边界规则为什么会把一个任务打碎

DMA 性能分析里经常看见“理论上一笔 256B 搬运，为什么硬件里像拆成了很多小块”。常见原因不是 DMA 坏了，而是边界规则在起作用：

- 地址没有按总线要求对齐
- 传输跨越 4KB 或 page 边界
- AXI burst 长度达到上限
- local SRAM bank 或端口映射要求拆分
- IOMMU 映射把逻辑连续区间切成多个物理段

一个保守的逻辑分块器可每次选择 `chunk = min(remaining, max_chunk_bytes, bytes_to_src_boundary, bytes_to_dst_boundary)`，推进源、目的和 remaining。这里 boundary 是当前路径确实要求的边界；对每个 chunk 再按接口生成合法读写 burst，尾部有效字节用允许的 byte lane/WSTRB 表示。源与目的各自独立拆分和重组也可合法，不一定都按同一边界拆。

例如 AXI4，源 `0x0FF0`、目的 `0x2000`、长度 32 B、每 beat 8 B，源在 16 B 后到 4KB 边界。保守分块得到 `[0x0FF0,0x0FFF]` 和 `[0x1000,0x100F]` 两个 16 B 子块，每个读 burst 为 2 beat，至少两次 AR/R；目的端独立规划时可以是一笔 4-beat AW/W/B，也可按两块发送。若只剩 5 B，最后使用合法 size/lane 或 strobe；不能假定无效 byte 被写入。

AXI4 的 4KB 与最大 beat 数、PCIe 的 MPS/MRRS 和请求边界、IOMMU page 映射是不同约束：page 不连续可能需要翻译或 scatter-gather，不自动等于 AXI 事务必须按物理页拆。算法还须验证地址宽度、溢出、权限和目标支持。见 [Arm IHI 0022H](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf?hash=6325311012DDADF238C35A6C0FD734E520754F82&la=en&revision=71bd7c57-2ed7-487b-bc3e-68c4ab56fa5f) 与 [RAM 地址映射](../../../RAM/wiki/06-memory-controller/address-mapping-channel-rank-bank-row-col.md)。

## Scatter-gather 的价值和代价

scatter-gather 的价值不在“更高级”，而在“把分散 buffer 仍然组织成一条可由 DMA 独立推进的逻辑任务”。这对网络、存储、用户态 buffer 映射和分页系统尤其关键，因为逻辑连续数据经常对应物理不连续段。

代价也很明确。每多一个 segment，就多一次 descriptor 解析、地址边界检查、潜在的 page translation 和回包组织成本。scatter-gather 解决了 CPU 不想逐段介入的问题，但没有让碎片化访问免费。

## 常见误解

常见误解：`一个 descriptor 就是一笔 burst`。实际上 descriptor 属于任务描述层，burst 属于互连事务层，中间还隔着边界拆分和地址转换。

常见误解：`burst 越长越好`。实际上 burst 太长会增加占路时间、放大热点和尾延迟，对混合流量系统尤其危险。

常见误解：`scatter-gather 只是软件方便`。实际上它深刻改变了 DMA 的地址生成、translation、response 组织和 completion 路径压力。

## 一句话理解

descriptor 决定 DMA 知道要做什么，burst 决定 DMA 以什么粒度占用系统，而边界规则决定这件事最终能否高效落地。

## 建模启示

这页对应的最小模型，不是“descriptor 直接等于 latency”，而是“descriptor 展开成事务序列”。event-driven 仿真里建议显式保留 `descriptor_fetch_done`、`transaction_split`、`read_issue`、`write_issue`、`boundary_penalty` 这几个事件。

一个可直接使用的中间结构是：

```text
ExpandedTransfer {
  descriptor_id
  subreq_count
  subreq[i] = {addr, bytes, dir, boundary_tag}
}
```

如果只关心稳态吞吐，可以把 `subreq[i]` 折叠成一个长度分布和平均边界惩罚；如果关心 ordering、fault pinpoint 或 page-crossing 效应，就必须显式保留每个子事务。
