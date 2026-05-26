# Input Buffer Organization

上级：[02 Router Microarchitecture](./README.md)
相关：[Virtual Channel Fundamentals](./virtual-channel-fundamentals.md), [Credit Based Flow Control](./credit-based-flow-control.md)

## 这页在回答什么问题

输入缓冲到底是“每端口一个 FIFO”还是“每端口下面再拆多个 VC 队列”，以及这些组织方式分别在吞吐、面积、HoL blocking 和可分析性上代表什么。

buffer 不是 NoC 的边角料。对现代 router，buffer 往往既是最大面积头，又是 backpressure 是否会快速扩散的第一现场。

## 为什么 NoC 常把 buffer 放在输入侧

经典 wormhole router 更常用 input-buffered 架构，而不是 output-buffered。原因很直接：如果把缓冲放输出侧，你必须先让多个输入同时冲向同一个输出，再在输出端承受写入冲突和更高带宽要求；这会把 crossbar 和写口成本迅速拉高。

把缓冲放输入侧，相当于把“先排队，再竞争”前移。这样每个输入端口都能局部吸收抖动，crossbar 每拍只需要放行已排好队的候选者。代价则是：队头一旦卡住，会更容易产生 HoL blocking。

所以 input buffering 不是完美方案，而是“在面积和控制复杂度可接受的前提下，把冲突收敛到输入队列”的折中。

## 方案一：每端口单 FIFO

这是最简单的组织：

```text
input port
  -> FIFO
  -> RC/SA
```

优点：

- 实现最简单
- buffer 控制最少
- 容易做第一版原型

缺点同样致命：所有 packet 共用一个队列，队首 flit 只要因某个方向拥塞而停住，后面本来能走其他方向的 flit 也跟着停。HoL blocking 在这里最纯粹。

一个例子：

```text
FIFO head: packet A -> wants East, but East busy
FIFO next: packet B -> wants North, North free

结果：B 也不能过，因为 A 还在队首
```

这就是为什么“单 FIFO 能工作”不等于“单 FIFO 足够用”。一旦你进入高并发 AI traffic，这种错误耦合会迅速放大。

## 方案二：每端口多个 VC 队列

更常见的组织是：

```text
input port
  -> VC0 FIFO
  -> VC1 FIFO
  -> VC2 FIFO
```

多个 VC 共享同一物理链路，但逻辑上是多个独立队列。这样一个 VC 队首卡住时，另一个 VC 仍可能前进。它至少解决了两件事：

- 缓解 HoL blocking
- 给 message class / deadlock avoidance 提供分层工具

但它不会增加物理带宽。多个 VC 只是更精细地复用同一条链路，所以如果根本瓶颈是链路容量不够，多开 VC 不会创造新带宽。

## Buffer 深度为什么不能拍脑袋定

buffer depth 的最基本约束，不是 workload，而是 credit round-trip。

如果从当前 router 发一个 flit，到对应 credit 返回，需要 `R` 个 cycle，那么每个活跃 VC 至少要有大约 `R` 个 slot，才能避免链路在稳定流下出现气泡。

一个简单例子：

```text
forward link latency = 1
downstream consume latency = 1
credit return latency = 1

R = 3
```

若 VC 深度只有 2：

```text
cycle 0: send flit0, credit 2->1
cycle 1: send flit1, credit 1->0
cycle 2: cannot send, waiting for credit
cycle 3: credit returns
```

你白白丢了一拍带宽。也就是说，buffer 过浅不仅是“容量小”，还是“稳态吞吐上不去”。

## 深 buffer 也不是免费午餐

看到上面的公式，容易得出“那就把 buffer 做很深”。这同样不对。

深 buffer 的收益是：

- 更能吸收短时 burst
- backpressure 传播更慢
- 长链路更容易保持满载

深 buffer 的代价是：

- SRAM 面积线性增长
- 动态功耗和 leakage 上升
- 拥塞恢复更慢，因为网络里积压的 flit 变多
- 延迟尾部可能更差，因为大量排队被隐藏在 buffer 中

这也是 NoC 和 BUS 的一个明显差异。BUS 上 deeper FIFO 常被看作“缓冲抖动的好事”；NoC 上 deeper buffer 同时会改变阻塞传播速度和网络中的在途积压量，所以它既能救吞吐，也可能恶化最坏延迟分析。

## 一种实用组织：每 VC 小深度，而不是每端口大共享池

理论上，你可以给一个端口做共享 buffer pool，让忙的 VC 暂时多占一些空间。这会提高 buffer 利用率，但控制复杂度、归属管理和 starvation 风险都会上升。

很多 deterministic NPU 更常用的做法是：

- 每个 VC 小而固定深度
- 总 VC 数不多，常见 2 到 4
- 主要靠 traffic separation 和静态调度，而不是靠超深 buffer 吞拥塞

原因很现实。静态可分析系统不希望网络里藏太多不可见排队；过深 buffer 会让“最坏要排多少拍”变得更松、更难证明。

## 一个定量例子

假设：

- 5-port router
- 每端口 4 个 VC
- 每 VC 深度 6
- flit width = 128b = 16B

则 input buffer 总量：

```text
5 * 4 * 6 = 120 flit slots
120 * 16B = 1920B
```

一个 router 接近 2KB input buffer。若扩到 64 个 router，光 input buffer 就已经超过 120KB，还没算控制状态和其他 SRAM。这个数量级足以说明：buffer 组织不是参数小事，而是面积预算的中心问题之一。

## 常见误解

常见误解：buffer 越深，性能一定越好。  
实际上：超过 credit round-trip 所需后，边际收益迅速下降，反而可能增加面积、功耗和最坏排队时间。

常见误解：VC 只是逻辑概念，和 buffer 无关。  
实际上：VC 的存在必须落在独立队列或至少独立 credit/状态上，否则它就无法承担 HoL 缓解和隔离职责。

## 一句话理解

input buffer 的核心 trade-off 是：用多少局部排队空间，换多少吞吐稳定性和隔离能力，同时愿意付出多少面积、功耗和最坏排队时间。

## 建模启示

最小 cycle-level 抽象建议直接保留：

```text
InputPort {
  vcs: InputVC[]
}

InputVC {
  queue_depth
  occupancy
  flit_queue
}
```

事件和统计至少要有：

- `buffer_enqueue`
- `buffer_dequeue`
- `buffer_full_block`
- `high_watermark_update`

如果只做 first-order 性能比较，可以把每个 VC queue 简化成 `occupancy` 计数，而不存完整 flit 对象；但如果要区分 header/body/tail、或验证 tail 释放时机，就必须保留队列顺序。

若要研究 credit 深度对吞吐的影响，`queue_depth` 不能抽掉；若要研究 deadlock-free 性质，`queue_owner_packet_id` 和 `downstream_binding` 也必须显式记录，否则你看不到资源依赖链。
