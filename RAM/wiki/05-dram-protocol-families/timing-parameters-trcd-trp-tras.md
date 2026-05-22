# 关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源

上级：[DRAM 协议层](./README.md)
相关：[ACT、RD、WR、PRE：DRAM 命令集为什么长这样](./commands-act-rd-wr-pre.md), [刷新：DRAM 的原罪和它的代价](../04-dram-foundations/refresh-the-fundamental-cost.md)

## 这页在回答什么问题

为什么 DRAM 协议里会有一大串看起来像“神秘常数”的 timing 参数，以及这些参数各自在等什么物理过程完成。更具体地说，tRCD、tRP、tRAS、tCL 不是随便规定的空档，而是 cell、位线、sense amp 和 I/O 路径必须拿到的时间预算。

## 正文

第一次看 DRAM 规格书时，很多人会把 timing 参数当成一种不透明的背诵负担：`tRCD`、`tRP`、`tRAS`、`CL`、`tRFC`、`tWR`，好像只是标准委员会写出来的一串数字。这样记当然能在表层上区分不同颗粒，但你很难据此形成判断。真正有用的理解方式是反过来看：每一个 timing 参数，其实都在回答一个问题，“在前一个物理动作完成到足够安全之前，后一个动作最早什么时候可以开始”。

上一页已经把 DRAM 命令集拆成了 `ACT -> RD/WR -> PRE` 这条显式路径。现在只需要再多问一步：为什么这些命令之间不能立刻无缝连着发？答案就是，底层阵列和 I/O 并不是理想瞬时资源。开行后，位线上的微弱差分需要时间被 sense amp 放大并稳定；读出结果从 row buffer 到 I/O 还要穿过列路径和外部接口；一行被使用过后，位线和 cell 侧也需要时间恢复到可再次切换的状态。timing 参数就是这些等待条件的协议化名字。

先看 `tRCD`，也就是 row-to-column delay。它约束的是从 `ACT` 到第一次 `RD` 或 `WR` 之间必须等待多久。物理上，这段时间对应的是：wordline 被拉高后，cell 与位线开始 charge sharing，sense amp 开始识别并放大微弱差分，直到该行的数据在 row buffer 一侧足够稳定，可以安全接受列访问。也就是说，`tRCD` 不是“控制器慢一点再发命令”的人工保守量，而是在等“这一整行真的已经被打开并可用了”。

再看 `tCL`，也就是 CAS latency，通常讨论的是从 `RD` 命令发出到第一拍读数据真正从 I/O 侧出来之间的延迟。它约束的不是 row 打开，而是“已打开行上的列选通、内部数据路径和外部接口启动”这一段。换句话说，row buffer 里即使已经有了正确数据，也不等于下一拍数据马上就能从引脚上出来；列 mux、预取边界、电路流水和对齐逻辑都需要时间。因此 `tCL` 更多是在描述列访问到外部可见数据之间的接口路径时延，而不是 cell 感测本身。

`tRAS` 的名字常被简单翻译成 row active time，但它真正表达的是：一行被 ACT 打开后，至少要保持激活多长时间，才能保证 sense、restore 和必要的数据操作完整完成。这里最容易犯的错误，是把 `tRAS` 理解成“既然数据已经读出来了，为什么还不能立刻关行”。答案在于，对 DRAM 来说，开行不仅是把数据放大出来，还包括把数据可靠恢复回 cell。行打开得太短，可能意味着某些 cell 还没完成足够恢复，或者写操作相关的内部状态还不安全。于是 `tRAS` 本质上是在限制“这一行至少得活够多久，才能被认为完整服务过”。

`tRP`，也就是 row precharge time，则约束从发出 `PRE` 到这个 bank 真正能再次接受下一次 `ACT` 之间必须等待多久。物理上它对应的是：当前 open row 被释放后，位线要重新回到预充平衡状态，sense amp 和相关阵列路径也要复位到下一次感测的初始条件。如果你在 `PRE` 后立刻对同一个 bank 发下一个 `ACT`，新一行会在旧状态还没真正清空时接入阵列，感测条件就会不正确。因此 `tRP` 本质上是在等 bank 从“刚用过一行”恢复成“可安全开新行”的中性状态。

把这几个最关键的参数串起来，就能得到一条更接近物理过程的命令时序：

```text
ACT ---- wait tRCD ---- RD ---- data after tCL -----
 |-------------------- row stays active --------------------|
                must satisfy at least tRAS
PRE ---- wait tRP ---- next ACT
```

这个图想表达的核心不是具体数值，而是等待窗口各自对应哪段过程：`tRCD` 在等“开行后能列访问”，`tCL` 在等“列访问后能把第一拍数据推出 I/O”，`tRAS` 在等“这一行活得足够久以完成恢复”，`tRP` 在等“关行后重新预充好可以换下一行”。

如果再看写路径，会发现很多参数的直觉也类似。写操作不仅需要列路径把数据送入 row buffer，还需要给 cell 留够时间完成写回和恢复，因此又会出现 `tWR` 这类 write recovery 相关约束；refresh 则会引入 `tRFC` 这类更长的不可服务窗口，因为那不是单个请求的路径，而是整个刷新操作在占用阵列资源。也就是说，DRAM 的 timing 表面上像一堆细碎符号，本质上都是在给不同物理阶段划边界。

这里必须强调一个常见误解：timing 参数并不是“同一颗 DRAM 的固定自然常数”，而是工艺、组织、代际和目标速率共同决定的安全窗口。你看到不同代 DDR 的参数变化，不应该只读成“新一代更快”或“数字更大更小”，而应该问：是阵列本体更快了，还是接口变快但内部等待预算并没同比缩小，还是某些约束因容量/密度增加反而变得更紧。后面你会看到，很多时候外部带宽提上去了，但某些绝对时间量级并没有按直觉等比例缩短，这正说明 DRAM 内部物理过程并不会因为 I/O 名义速率提高就自动同速提上去。

从系统视角看，理解 timing 参数最重要的价值，不是记住典型值，而是知道它们会怎样塑造访问成本结构。只要存在 `tRCD` 和 `tRP`，row hit 就一定比 row conflict 便宜得多；只要 `tRAS` 不能任意缩短，开行就一定是一笔必须尽量摊薄的成本；只要 `tCL` 不为零，列访问后的数据返回也一定不是“下拍立即可见”的理想读。也就是说，timing 参数不是附属常量，而是 DRAM 访问非均匀性的定量边界。

所以，本页真正要建立的不是一份速查表，而是一种解释框架：每一个 timing 参数都应该能被翻译回某段物理等待。只要这层对应关系建立起来，后面看到 controller 调度、page policy 或不同 DRAM family 的时序差异时，你就能顺着“它在等哪段过程”往下判断，而不是停留在参数名本身。

## 一句话理解

tRCD、tRP、tRAS、tCL 这些参数不是标准里凭空冒出来的等待常数，而是在给 DRAM 的开行、感测、恢复、列访问和预充这些物理过程划安全边界。

## 建模启示

在建模里，这些 timing 参数最少应该被实现成命令间的 guard，而不是只折成一个“读延迟常数”。如果只用一个统一 latency，模型可以大致估算平均响应，却无法表达 row hit/miss/conflict 差异，更无法表达 controller 为什么要重排命令。

一个最小可用的 timing 表可以写成：

```text
DramTiming {
  tRCD: cycle
  tCL: cycle
  tRAS: cycle
  tRP: cycle
  tWR: cycle
  tRFC: cycle
}
```

对应 guard 形式可以直接写成：

```text
guard RD_or_WR legal only if now >= act_cycle + tRCD
guard PRE legal only if now >= act_cycle + tRAS
guard next_ACT legal only if now >= pre_cycle + tRP
guard data_visible at rd_cycle + tCL
```

如果只关心粗粒度性能，可以把这些 guard 折成三类代价：`row_hit_cost`、`row_miss_cost`、`row_conflict_cost`。但只要你要研究协议差异、controller 调度或 refresh 与普通请求的交互，最好显式保留 timing 表和命令级时间戳。因为很多“为什么这条请求不能现在发”的答案，根本不是队列里有没有空位，而是 timing guard 还没放行。
