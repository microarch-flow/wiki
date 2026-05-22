# 同样是 RAM，为什么 SRAM 和 DRAM 走向了完全不同的工程路径

上级：[概览](./README.md)
相关：[6T cell 为什么是 6 个晶体管，双稳态如何对抗扰动](../02-sram-foundations/6t-cell-bistable-storage.md), [1T1C cell，一颗电容为什么改变了一切](../04-dram-foundations/1t1c-cell-destructive-read.md)

## 这页在回答什么问题

SRAM 和 DRAM 都属于 RAM，都支持随机访问，为什么最后却变成两条几乎互不替代的工程路线。更关键的是，它们的分化不是历史偶然，而是对同一组物理约束做出的两种根本不同回答。

## 正文

如果只从名称上看，`Static RAM` 和 `Dynamic RAM` 的区别好像只是“一个要不要 refresh”。这种理解太浅，因为 refresh 不是 DRAM 后来附带上的维护动作，而是它从一开始选择存储方式后必然付出的代价。SRAM 和 DRAM 的真正分歧，发生在“一个 bit 应该怎样被存住”这一层。SRAM 选择用交叉耦合反相器形成双稳态，把一个 bit 变成一个会自行维持的电路状态；DRAM 选择把一个 bit 存成电容上的少量电荷，再用访问晶体管把它接到阵列中。前者把稳定性和快速读写放在第一位，后者把面积效率和可扩容性放在第一位。后面的所有差异，都是这个分叉的展开。

SRAM 这条路线的核心优点，是它把“存储”和“保持”合在了一起。只要供电存在，交叉耦合结构就会把当前逻辑状态持续再生，因此不需要周期性刷新，也不需要每次读取后再把数据写回。这样做直接带来两个结果。第一，读取路径可以设计得更短，访问延迟可以压得很低。第二，接口语义更接近“真正的随机访问”，地址一到，就希望很快得到数据，而不用先经历开行、感测、恢复这样的多阶段过程。代价也同样直接：每个 bit 需要更多晶体管，更大面积，更高漏电，以及在多端口、超大容量和先进制程下更难收敛的稳定性问题。

DRAM 则反过来，把“单 bit 尽可能便宜”这件事放到极致。1T1C 单元的面积远小于 6T cell，因此可以在同样硅面积里塞进更多 bit，这让 DRAM 成为大容量主存的现实选择。但这条路线一开始就在借债。电容上的电荷会漏失，所以需要 refresh；读出时感测本身会扰动甚至消耗原始电荷，所以读是破坏性的；单个 cell 信号很弱，所以不能像 SRAM 那样直接按 bit 读取，而必须把整行接到位线和 sense amp 上做放大与恢复。换句话说，DRAM 是用阵列级复杂性和时间级复杂性，换取了单元级面积优势。

这两条路线最值得注意的差别，不在“一个快一个慢”这么简单，而在访问成本曲线的形状完全不同。SRAM 的单次访问成本相对稳定。它当然也会受 bank 划分、端口冲突、位线长度和工艺波动影响，但总体上，一次读取更像是局部电路操作。DRAM 的访问成本则强烈依赖上下文。同一个地址，在 row hit、row miss、row conflict 下对应完全不同的命令路径和时延；同一个 bank，是否正处于 refresh、是否被别的请求占用，也会改变访问结果。这意味着 DRAM 不是“慢一点的 SRAM”，而是一种对访问模式高度敏感的存储介质。

这也是为什么 SRAM 和 DRAM 不是简单按容量分层，而是按“适合承载什么样的访问行为”分层。SRAM 适合放在距离计算最近的位置，因为它更容易支持低延迟、高频率、细粒度随机访问，以及更强的确定性。register file、cache、scratchpad、TCM、NPU 本地 buffer 都属于这条路线的不同用法。DRAM 适合放在更远、更大、更便宜的层次，因为它擅长提供大容量，但要求系统接受更高访问延迟、更复杂并行组织，以及更依赖局部性和调度器的性能表现。常见误解是把 SRAM 和 DRAM 的关系理解为“同一种东西的高配版和低配版”；实际上，它们更像是两类目标函数完全不同的设计点。

从演化路径看，这种分化还会继续放大，而不是随着工艺进步自动收敛。先进制程并没有让 SRAM 和 DRAM 越来越像，反而让它们各自的问题更尖锐。SRAM 在缩小过程中越来越受限于读写稳定性、最小工作电压和漏电；DRAM 在提高容量和带宽时，则越来越受限于 refresh 开销、感测裕量、bank 组织、I/O 能耗和堆叠封装复杂度。也就是说，工艺进步不是消除了 trade-off，而是把两条路线分别推向了自己的极限边界。

更重要的是，这种分化决定了后面的系统组织方式。只要底层是 SRAM，你就会优先讨论端口数、banking、tag/data 分离、软件管理与硬件管理的边界。只要底层是 DRAM，你就必须讨论 row buffer、page policy、address mapping、refresh、channel 并行和 memory controller 调度。系统架构上的很多“上层差异”，其实只是底层器件差异在更高层的投影。比如 scratchpad 和 cache 的争论，本质上发生在“同为 SRAM 时如何管理局部数据”；而 DDR、LPDDR、GDDR、HBM 的分化，则发生在“同为 DRAM 时如何把容量、功耗、带宽和封装关系重新平衡”。

站在建模角度看，SRAM 和 DRAM 的分化还有一个非常实际的含义：两者不能套用同一种性能抽象。SRAM 更适合建模成有限端口、有限 bank、固定或近固定服务时间的资源；DRAM 则必须建模成有显式内部状态的资源，其服务时间依赖 open row、bank busy、refresh credit、command timing 和队列调度。很多过于粗糙的架构模型之所以会误判系统瓶颈，就是因为它把 DRAM 也当成“容量更大、延迟更高的 SRAM bank”。

所以，这一页真正想建立的结论不是“SRAM 快、DRAM 大”，而是更严格的一句：SRAM 和 DRAM 是对同一组存储目标做出的两种正交选择。SRAM 先保局部访问质量，再接受面积与成本；DRAM 先保每 bit 成本与容量，再接受时间与控制复杂性。后面的两条主线，都会围绕这个基本分岔展开。

## 一句话理解

SRAM 和 DRAM 的根本分化，不在于一个要 refresh 一个不要，而在于一个用双稳态电路优先保证局部访问质量，另一个用最省面积的存储单元优先保证容量与成本。

## 建模启示

这一页对应的核心建模决策是：先按资源语义把 SRAM 和 DRAM 分开，再决定每一类资源需要保留哪些状态。对 SRAM，最小模型通常只需要显式描述 `num_ports`、`bank_count`、`access_latency_cycles`、`capacity_bytes` 这些稳定属性，再加少量瞬时状态，例如端口占用或 bank busy。对 DRAM，这样的静态参数表不够，因为服务时间依赖内部上下文，至少要有 `open_row[bank]`、`bank_ready_cycle[bank]`、`refresh_due_cycle`、`rw_turnaround_state` 这类显式状态。

一个足够清楚的对比性数据结构草图可以写成：

```text
SramModel {
  capacity_bytes: uint64
  bank_count: int
  num_ports: int
  access_latency_cycles: int
  bank_busy_until[bank_count]: cycle
}

DramModel {
  capacity_bytes: uint64
  channel_count: int
  banks_per_channel: int
  open_row[channel][bank]: row_id | INVALID
  bank_ready_cycle[channel][bank]: cycle
  next_refresh_cycle[channel]: cycle
  command_queue: queue<MemReq>
}
```

如果只关心粗粒度性能，SRAM 的 bit cell 级细节和 DRAM 的 sense amp 电气细节都可以折叠掉；但两者的“状态形态”不能折叠成同一种东西。前者更像固定服务时间的共享资源，后者更像受内部状态和调度影响的状态机资源。这个区分一旦做对，后面 cache、scratchpad、DDR、HBM 和 MC 模型的边界就会清楚很多。
