# ACT、RD、WR、PRE：DRAM 命令集为什么长这样

上级：[DRAM 协议层](./README.md)
相关：[行列解码与读出放大：为什么 DRAM 必须先开行](../04-dram-foundations/row-column-decode-sense-amplify.md), [关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源](./timing-parameters-trcd-trp-tras.md)

## 这页在回答什么问题

为什么 DRAM 的外部接口不可能像 SRAM 那样近似为一个“给地址，读数据”的黑盒，而必须显式拆成 ACT、RD、WR、PRE 这样的阶段性命令。更关键的是，这些命令并不是接口层的人为发明，而是上一章里那条物理访问路径在协议层的直接投影。

## 正文

如果只从软件语义出发，内存访问似乎应该很简单：给一个地址，读或写对应数据即可。DRAM 之所以没有长成这种接口，不是因为标准喜欢复杂，而是因为底层阵列根本不支持“直接按地址随机抓取一个小字”。上一章已经说明了这一点：1T1C cell 很弱，必须先整行接入位线、由 sense amp 放大并恢复；sense amp 形成当前 open row 的工作副本后，列访问才有意义；切换到别的行前，还必须释放当前行状态并把位线回到可再次感测的预充条件。因此，DRAM 的命令集本质上是在把这一长串必经的物理阶段显式暴露给控制器。

`ACT`，也就是 activate，对应的就是“先开行”这件事。它不是一个抽象授权动作，而是实打实地让某个 bank 中目标 row 的 wordline 拉高，使该行所有 cell 接到位线，随后整排 sense amp 开始检测并放大微弱差分，再把恢复后的逻辑状态维持在 row buffer 一侧。控制器一旦发出 ACT，并不是只打开了“一个地址入口”，而是把这整个 bank 的当前工作副本换成了目标 row。也正因为 ACT 的代价大、范围宽，后续多次命中同一 row 时才有机会把这笔成本摊薄。

`RD` 和 `WR` 对应的则是在已打开的 row 上做列访问。注意这里的关键前提是“row 已经在 row buffer 里可见”。`RD` 不是去原始 cell 里直接读数据，而是在当前 bank 已经激活出来的那一整行工作副本上，选出请求的列地址并开始 burst 传输。`WR` 也类似，只不过写入数据会被送到 row buffer / sense amp 一侧，再被最终写回到对应 cell。换句话说，RD/WR 的语义不是“访问 DRAM 阵列”，而是“访问当前已经打开的 DRAM 行窗口”。这也是为什么行未打开时，控制器不能直接发 RD/WR，而必须先经过 ACT。

`PRE`，也就是 precharge，对应的是“把当前 bank 从已打开行状态恢复到可再次开新行的初始条件”。直觉上它像是在“关行”，但更精确地说，它是在释放当前连接到 row buffer 的工作状态，并把位线重新拉回预充电平，为下一次感测做好准备。如果没有 PRE，controller 就无法在同一个 bank 上切换到别的 row，因为 sense amp 和位线仍然被当前 open row 占着。常见误解是把 PRE 看成某种可有可无的 cleanup；实际上，没有它，row conflict 根本无法被正确解决。

把这四个命令连起来看，就能发现它们几乎是一条物理流水线的显式接口化：

```text
ACT  ->  RD / WR  ->  PRE
开行     列访问       释放并预充
```

对于最常见的三类访问情形，这条命令链会长成不同样子：

```text
Row hit:
  RD/WR

Row miss (bank closed):
  ACT -> RD/WR

Row conflict (different row already open):
  PRE -> ACT -> RD/WR
```

这三种情况之所以后面会反复出现在控制器和性能分析里，就是因为它们不是协议层标签，而是不同物理路径的简写。常见误解是把 row hit 看成“幸运命中某种缓存”，而把 PRE/ACT 看成“多出来的几条命令”；更准确的理解应该是：RD/WR 只在 open row 已经就位时才是便宜的，PRE/ACT 则是在底层状态不匹配时必须补缴的物理切换成本。

还有一个容易被忽略的点是，命令集的显式化其实把 controller 的自由度放大了。因为协议没有把所有东西强行封装成一个不可拆的“内存事务”，controller 才有机会利用 row locality、交织不同 bank、推迟 PRE、或者在不同请求之间重排命令。例如，如果连续多个请求都命中当前 open row，controller 可以选择暂时不 PRE，让后续 RD/WR 直接命中；如果另一个 bank 正在忙 activate，它也许可以先服务当前 bank 的列访问。也就是说，ACT/RD/WR/PRE 看似复杂，实际上正是后面调度优化得以存在的接口前提。

当然，这种显式命令接口也意味着使用它的人必须承担更多责任。控制器不能像使用理想 SRAM 一样随便发读写，而必须确保命令顺序与 bank 状态匹配，必须知道哪个 bank 当前 open 的是哪个 row，也必须满足后面各种 timing 限制。也正因为如此，DRAM 性能从来不只是由颗粒规格决定，而是由 controller 能否聪明地利用这套命令语言决定。协议把底层结构暴露出来了，控制器就得真的理解并驾驭它。

为什么这些命令能长期稳定存在，而不是被更高层接口完全吞掉，也和 DRAM 的产品目标有关。DRAM 的密度优势非常依赖这套共享 sense amp、整行感测和按 bank 管理的结构。如果你试图把所有复杂性都藏在芯片内部，对外只暴露一个简单随机访问黑盒，那么控制器将失去利用 row locality 与 bank parallelism 的空间，系统也更难在通用主存场景下把带宽做上去。换句话说，DRAM 并没有选择“最简单好用”的接口，而是选择了“最能保住物理效率并允许系统优化”的接口。

从这一点回看，ACT/RD/WR/PRE 其实不像传统意义上的“指令集”，而更像一组围绕阵列状态机暴露的操作原语。ACT 改变 bank 的 open row 状态，RD/WR 消费该状态，PRE 清空该状态。后面 timing 参数的意义，正是约束这些状态变化必须等待多长时间才能安全发生。只要这个框架先立住，后面的 tRCD、tRAS、tRP、CAS latency 就不会再像是孤立常数，而会变成这些原语之间的等待条件。

所以，这一页真正要建立的结论是：DRAM 命令集之所以长这样，不是因为协议层人为把一笔读写事务拆碎了，而是因为底层阵列本来就必须经历“开行、访问、释放”的多阶段过程。协议只是把这个过程原样交给了系统，并允许 controller 在这个显式状态机上做优化。

## 一句话理解

ACT、RD、WR、PRE 不是人为拆碎的一笔内存请求，而是 DRAM 底层“开行、在已打开行上列访问、再释放预充”这条物理访问路径的显式接口化。

## 建模启示

在建模里，DRAM 访问不应被直接映射成一个“read(addr)”原子操作，而应至少分解成命令流和 bank 状态更新。即使你不打算模拟完整 JEDEC 细节，也最好保留 `ACT`、`COL_ACCESS`、`PRE` 这三类原语，因为 row locality 和调度优化正建立在它们可被拆分和重排这一点上。

一个最小可用的命令抽象可以写成：

```text
enum DramCmd { ACT, RD, WR, PRE, REF }

BankState {
  open_row: row_id | INVALID
  state: enum { CLOSED, OPEN, BUSY }
}
```

访问分解框架可以直接写成：

```text
if bank.open_row == target_row:
    emit(RD or WR)
elif bank.open_row == INVALID:
    emit(ACT)
    emit(RD or WR)
else:
    emit(PRE)
    emit(ACT)
    emit(RD or WR)
```

如果只关心粗粒度平均延迟，可以把这几步折叠成 row-hit / row-miss / row-conflict 三种代价表；但只要你要建模命令重排、page policy 或多 bank 交织，最好显式保留命令队列和 bank 状态机。因为“能不能把两个请求调换顺序”，本质上取决于这些命令级状态是否兼容。
