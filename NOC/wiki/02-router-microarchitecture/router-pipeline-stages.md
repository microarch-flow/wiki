# Router Pipeline Stages

上级：[02 Router Microarchitecture](./README.md)
相关：[Allocator Design VC Switch](./allocator-design-vc-switch.md), [Credit Based Flow Control](./credit-based-flow-control.md)

## 这页在回答什么问题

经典 router 为什么常被拆成 `BW/RC/VA/SA/ST` 或 `RC/VA/SA/ST/LT` 这样的阶段，以及 header、body、tail 在流水线上为什么不是同一种对象。

如果这一页没立住，后面你很难分清 credit stall、VC unavailable 和 switch conflict 到底属于哪一层问题。

## 先讲结论：pipeline 不是为了教科书整齐，而是为了把冲突分层

一个 wormhole router 至少要处理四类事情：

- 把到来的 flit 放进某个输入缓冲
- 为 header 决定下一跳和下游 VC
- 让满足条件的队首 flit 竞争 crossbar
- 把获胜 flit 发上物理链路

这些事情如果全部堆在同一个周期里做，逻辑会过深、共享资源冲突也难以解释。分阶段的价值不是“更学术”，而是把不同资源竞争拆开：路由计算是局部逻辑，VC 分配是长期资源申请，switch 分配是短期资源争用，link traversal 则是物理传输。

## 一个常见的五级划分

最常见的心智模型是：

| 阶段 | 全称 | 核心动作 | 谁会经过 |
| --- | --- | --- | --- |
| `BW` | Buffer Write | flit 写入 input buffer | 所有 flit |
| `RC` | Route Computation | header 计算输出方向 | 仅 header |
| `VA` | VC Allocation | header 竞争下游 VC | 仅 header |
| `SA` | Switch Allocation | 队首 flit 竞争 crossbar | 所有可前进 flit |
| `ST/LT` | Switch/Link Traversal | 穿过 crossbar 并上链路 | 获胜 flit |

有些文献把 `ST` 和 `LT` 拆成两级，有些合在一起。对第一版建模，重要的不是记住名字，而是记住：`VA` 和 `SA` 在竞争不同资源。

## Header 和 body 为什么不是同一路径

header 要干最重的控制工作。它必须知道目的地、决定输出端口、再在下游申请一个逻辑通道。body 和 tail 不需要重做这些计算，它们沿着 header 已建立的绑定往前走。

所以一个 packet 的生命周期更像：

```text
header: BW -> RC -> VA -> SA -> ST/LT
body:   BW ---------> SA -> ST/LT
tail:   BW ---------> SA -> ST/LT -> release VC
```

这就是为什么 tail 不是“最后一个普通 flit”。它在语义上承担了释放长期资源的责任。

## 一个 cycle-by-cycle 例子

假设：

- 每级 1 cycle
- link traversal 单独占 1 cycle
- credit 足够，下游 VC 可分配

则一个 4-flit packet 过一个 router 的时间线可写成：

```text
cycle:   0    1    2    3    4    5    6    7    8
header:  BW   RC   VA   SA   LT
body0:   -    BW   wait wait SA   LT
body1:   -    -    BW   wait wait SA   LT
tail:    -    -    -    BW   wait wait SA   LT(release)
```

两个关键信息：

- body flit 可以在 header 还没走完 VA/SA 时就先进入 buffer
- 但它们不会前进，因为 input VC 还没进入 `ACTIVE` 状态

这也是很多新手容易误判的地方：body 卡住，并不一定是 credit 不够；也可能只是 header 还没建立好路径。

## Router 中真正并行的是“不同 VC 处在不同阶段”

router 每个周期不是只干一件事，而是多个阶段在不同 VC 上并行进行。比如同一个周期里：

- 一个 VC 的 header 在做 RC
- 另一个 VC 的 header 在做 VA
- 第三个 VC 的 body 在争 SA
- 上一周期 SA 获胜的 flit 正在走 LT

所以 pipeline 的收益不是把单个 flit 变快，而是让不同 flit 的不同动作重叠。

一个 snapshot 例子：

```text
cycle T:
  VC0: header in VA
  VC1: body0 eligible for SA
  VC2: flit on link return path
  VC3: idle
```

没有 pipeline，这些动作就必须串行执行；有了 pipeline，你得到的是吞吐，不是单个 flit 的魔法零延迟。

## 为什么 VA 和 SA 必须分开

这是 router pipeline 最值得强调的地方。

`VA` 分配的是下游 router 的一个 VC，它是 packet 生命周期级别的长期资源。header 一旦申请成功，该 packet 通常会一直占着这条逻辑通道直到 tail 离开。

`SA` 分配的是当前周期的 crossbar 通路，它是 flit 级别的短期资源。这个周期 body0 赢了，下一周期可以换成别的 flit 赢。

如果把两者混为一谈，就会得出很多错误判断，例如把“队首 flit 这拍没过”误判成“packet 没有拿到路径”。一个常见的性能现象是：header 已经完成 VA，但 body 连续几拍都输 SA，于是系统表现为 switch conflict，而不是 route blocked。

## 为什么许多实现还会插入更深流水

经典五级不是自然法则。真实芯片里，常见会继续插 deeper pipeline，原因通常有三个：

- router radix 大，allocator 逻辑太深
- crossbar 宽，ST 路径时序太差
- link 长，需要单独 pipeline LT

代价很直接：单 hop latency 变大。收益也很直接：频率更高，长线更可收敛。

所以“几级 pipeline”不是纯微架构审美问题，而是频率、线长和吞吐的硬 trade-off。很多 NPU 宁愿接受多 1 到 2 cycle 的 hop latency，也要把全局链路频率保住，因为一旦时钟掉下来，全网所有 path 都会受影响。

## 和 BUS ready/valid 的关键区别

BUS 里你熟悉的是 channel handshake。那套机制更像局部接口的交付语言：这一拍收没收到。NoC router pipeline 则多了一层：这拍即使收到了，也不等于能继续前进。因为前进还要看：

- header 是否完成 RC/VA
- 目标 VC 是否存在 credit
- 当前 crossbar 是否抢到

所以 NoC 的局部握手只是入口；真正的前进条件是若干内部状态同时成立。这也是为什么 NoC 的 stall 分类会比 BUS 更细。

## 常见误解

常见误解：经典 5 级 router 每个 flit 都必须完整走 5 级。  
实际上：只有 header 需要完整经历控制阶段，body/tail 通常复用 header 已建立的绑定。

常见误解：pipeline 深一点一定更慢。  
实际上：单 hop latency 确实更长，但如果它换来了更高频率和可实现的长线，全系统吞吐可能反而更好。

## 一句话理解

router pipeline 的本质是把“收、算路、占逻辑通道、抢物理通道、上链路”拆成不同资源阶段；header 负责建路，body 负责跟随，tail 负责释放。

## 建模启示

cycle-level 模型至少要显式保留每个 VC 的状态机：

```text
VCState = IDLE | RC | VA | ACTIVE
```

并维护：

```text
InputVC {
  state
  route_port
  downstream_vc
  buffer_queue
}
```

事件层面建议至少有：

- `buffer_write(flit, input_vc)`
- `route_compute_done(input_vc, output_port)`
- `vc_alloc_grant(input_vc, downstream_vc)`
- `switch_alloc_grant(input_vc, output_port)`
- `link_traverse(flit, output_link)`

如果你只关心平均吞吐，可以把 `RC` 折叠成零延迟组合逻辑，把 `ST` 和 `LT` 合并；如果你关心 stall attribution 或 worst-case latency，上述阶段最好分开，因为 `VC_UNAVAILABLE`、`SWITCH_CONFLICT` 和 `LINK_BUSY` 是不同病因。
