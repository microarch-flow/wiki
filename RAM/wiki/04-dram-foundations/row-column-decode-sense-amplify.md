# 行列解码与读出放大：为什么 DRAM 必须先开行

上级：[DRAM 基础](./README.md)
相关：[Row buffer：DRAM 内部的小 cache](./row-buffer-as-cache.md), [ACT、RD、WR、PRE：DRAM 命令集为什么长这样](../05-dram-protocol-families/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

为什么 DRAM 不能像 SRAM 那样给定地址就直接读出一个小字，而必须先选中整行、把整行内容感测到 sense amp 一侧，再做列访问。更准确地说，行列解码、位线预充和 sense amp 共享这几件事，是怎样一起把 DRAM 访问结构逼成“先开行，后取列”的。

## 正文

理解 DRAM 时，一个最值得先纠正的直觉是：它并不是“用得更慢一点的随机访问存储器”。从软件语义上看，DRAM 当然支持随机地址访问；但从阵列物理上看，它的随机访问不是直接落到单个 cell 上，而是必须绕过一个非常强的结构前提：单个 1T1C cell 太弱，弱到不值得也不可能为每个 bit 单独配一套始终可用的放大和恢复资源。因此，DRAM 的访问必须先经过整行级别的感测与恢复，再从已经被打开的那一行中选出所需列。这个“必须”不是协议选择，而是阵列经济性与物理可行性的结果。

先从位线和 sense amp 的关系看。每一列 DRAM cell 都接在一根长位线上，位线本身有显著电容，而且通常会在访问前被预充到接近中间电平。某一行被选中时，这一行的每个 cell 都通过各自访问晶体管同时接到各自位线上。因为 cell 电容远小于位线电容，所以单个 cell 能给位线带来的电压偏移极小，只够在预充中点附近制造一个很小的正负扰动。sense amp 的任务，就是检测这点极小差异并迅速放大到完整逻辑电平。关键在于，sense amp 不是给一个 bit 临时“读一下”就完事，它还会把放大后的结果继续保持并反驱回 cell，完成恢复。

为什么必须是“整行一起接上位线”？因为 sense amp 是按列共享的，而不是按 bit 独立复制的。对每一根位线或每一对差分位线来说，sense amp 常驻在那里；你选择某一行时，这一行所有列的 cell 会同时把各自的微弱信息送到对应位线上，于是整排 sense amp 被整行一起激活。换句话说，row decode 的本质不是“告诉系统你想访问第几行”，而是“让这一整行 cell 与整排 sense amp 建立连接”。只要这件事发生了，整行就已经被读出并恢复到 sense amp / row buffer 一侧了，不管你最后只想取其中 64 bit 还是 256 bit。

这就是“先开行”的真实含义。很多资料会把开行描述成一个协议动作，但在阵列层，更准确的说法是：row decoder 选择某一条 wordline，使该行所有 cell 同时接入位线；随后 sense amp 在每一列上完成微弱信号放大，并把这一整行的逻辑状态暂时保存在感测放大器阵列一侧。也正因为整行信息此时已经驻留在 sense amp 旁边，后续的列访问才只是在这个“已打开的工作副本”里选出所需字节或 burst 段，而不是再次去直接接触原始 cell。

可以用一个有限度的类比帮助理解：SRAM 更像是每个小房间里本来就亮着灯，你只需要推门看看；DRAM 更像是一整条走廊里的门后都很暗，你必须先把整层的照明系统接起来，整排门后的状态才会一起显现出来。这个类比只适合帮助理解“为什么感测是按行展开的”，一旦进入 timing 和恢复细节，仍然要回到 wordline、bitline 和 sense amp 的精确语言。

列解码 `column decode` 的意义，恰恰建立在这一步之后。因为整行已经被 sense amp 打开，所以列选择不再是在巨大二维阵列里“随机抓取某个 cell”，而是在一行已经展开的位线结果中选择某一段输出。也就是说，DRAM 的 row/column 并不是两个对称层级。row 负责把弱模拟信息变成可用数字状态，并付出最大的一次性开销；column 负责在这个已打开状态上做相对便宜的局部多路选择。这也是为什么 row miss 和 row hit 的成本会差那么多，后面 row buffer 概念才会成立。

为什么 DRAM 不像 SRAM 那样直接让每个小块有独立局部 sense amp、直接按细粒度访问？答案还是面积和共享效率。SRAM 可以接受更昂贵的每 bit 成本，因为它服务的是小容量低延迟层；DRAM 的目标是每 bit 成本尽量低，如果把 SRAM 式局部直接访问能力搬进来，放大器数量、布线、单元周边开销和面积都会显著膨胀，直接破坏 DRAM 的密度优势。也就是说，DRAM 之所以选择“整行感测 + 列选择”，本质上是在说：为了用极少的外围电路服务极大量的 cell，必须接受行级粒度的访问前置开销。

行列解码结构还会直接塑造系统看到的时序。因为 row 打开需要经历 wordline 拉高、charge sharing、sense amp 放大和 cell 恢复，所以它天然比列选通慢得多；因为 row 关闭前当前 open row 还占着那排 sense amp，换行前就需要预充和释放；因为列访问是在已打开 row 上进行的，所以连续访问同一行时成本可以显著更低。于是后面你看到的 `ACT -> RD/WR -> PRE` 其实并不是三个人为拆开的命令，而是这条物理访问路径在接口层的显式投影。

这套结构还顺手解释了几个经常被混淆的点。第一，sense amp 在 DRAM 里不仅是“读出放大器”，它实际上临时扮演了被打开那一行的工作存储体，因此后面 row buffer 才会被类比成一个小 cache。第二，column access 之所以能 burst，是因为数据已经不在原始 cell 侧，而是在 row buffer / sense amp 一侧顺序可取。第三，row conflict 的痛苦不在于“换个地址而已”，而在于你必须放弃当前整排已经占着的 sense amp 状态，重新让另一整行完成一遍昂贵的打开过程。

从工程取舍看，DRAM 的行列分工本质上是把访问代价做成高度不均匀：row 代价大而稀疏，column 代价小而频繁。这样做的好处，是如果 workload 恰好在一行内有足够局部性，前面的开销可以被摊薄；坏处是如果访问模式频繁跨行，系统就会不断支付大额前置成本。这也是为什么后面 page policy、address mapping 和 memory controller 调度会变得如此重要，因为它们其实都在回答同一个问题：怎样让昂贵的 row 开销被更充分摊销。

所以，本页真正想建立的不是“DRAM 有 row 和 column”这一层定义，而是更具体的结论：DRAM 必须先开行，是因为弱 cell 只能通过整排共享的 sense amp 被放大和恢复，而这种共享方式天然把一次访问分成了“昂贵的行激活”和“便宜得多的列访问”两段。只要这一层看懂了，后面的 row buffer、ACT/PRE、row hit/miss/conflict 就都会连成一条线。

## 一句话理解

DRAM 必须先开行，不是因为接口标准喜欢这么设计，而是因为 1T1C cell 太弱，只能通过整排共享的 sense amp 被整行一起放大和恢复，随后列访问才有意义。

## 建模启示

对建模来说，本页最重要的结论是：DRAM 的服务时间至少要拆成 `row activation cost` 和 `column access cost` 两段。只要把这两段压成一个常数，row locality、page policy 和 burst 行为就都很难被正确表达。即使模型不下沉到电压级，也至少要显式表达“打开一行”和“在已打开行中取列”是两类不同事件。

一个最小可用的状态和事件草图可以是：

```text
DramRowState {
  open_row: row_id | INVALID
  sense_ready: bool
  precharged: bool
}
```

```text
event Activate(bank_id, row_id)
event SenseRestoreDone(bank_id, row_id)
event ColumnRead(bank_id, row_id, col_id, burst_len)
event ColumnWrite(bank_id, row_id, col_id, burst_len)
event Precharge(bank_id)
```

如果只关心粗粒度平均性能，可以把 `Activate + SenseRestoreDone` 折叠成单个 `row_open_latency`；但只要你想分析 row hit 与 row conflict 的差异、或者想比较不同 burst / prefetch 组织，`Activate` 和 `ColumnRead/Write` 就不应再被混在一起。一个实用的访问代价框架可以直接写成：

```text
cost(req) =
  if open_row == target_row:
      column_cost
  else if open_row == INVALID:
      activate_cost + column_cost
  else:
      precharge_cost + activate_cost + column_cost
```

这就是后面整个 DRAM timing、row buffer 命中和 controller 调度模型的最小物理骨架。
