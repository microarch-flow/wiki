# Router Power Area Tradeoff

上级：[02 Router Microarchitecture](./README.md)
相关：[Input Buffer Organization](./input-buffer-organization.md), [../07-evaluation-methodology/power-area-modeling.md](../07-evaluation-methodology/power-area-modeling.md)

## 这页在回答什么问题

router 的性能、面积和功耗之间到底是谁在主导，以及为什么“加一点 buffer / 多几个 VC / 做宽一点链路”经常会同时牵动三四个代价项。

这页要打破一个常见直觉：NoC router 的成本中心通常不是路由计算，而是 buffer、crossbar 和与之相连的控制逻辑。

## Router 成本为什么主要不是算路

很多概念图会把 attention 放在 `RC/VA/SA` 这些控制方块上，于是容易误以为“router 很复杂，主要复杂在算法”。真实硬件里，功耗和面积常常更集中在：

- input buffer SRAM / register file
- crossbar 多路选择网络
- allocator 广播与仲裁逻辑
- 长链路收发器和驱动

`RC` 这类纯组合比较逻辑通常占比反而不大。它当然重要，但更像“决定能否工作”；真正决定是否贵的，常是为工作付出的存储和布线代价。

## Buffer：面积第一大头

buffer 会吃面积，原因不是抽象的“SRAM 也要硅面积”，而是它同时乘上了多个维度：

```text
buffer bits
  = ports * vcs_per_port * depth_per_vc * flit_width
```

任何一项翻倍，buffer 总量就跟着翻倍。一个 5-port router，从 4 VC 增到 8 VC，其他参数不变，buffer 面积几乎直接倍增。

功耗上，buffer 既有动态访问能耗，也有 leakage。对长时间活跃的大流量 NoC，动态部分会很明显；对先进制程和大规模全网 router，leakage 也不再能忽略。

## Crossbar：随 radix 和位宽膨胀

crossbar 的直觉很好理解：它越像“任意输入到任意输出”的全连接交换矩阵，逻辑和布线就越重。

尤其当这两个参数增加时，代价会非常显著：

- router radix 增大
- flit / link width 增大

你可以把 crossbar 看成一个会被“端口数”和“每端口位宽”双重放大的结构。cluster 内小 crossbar 看起来很爽，到了高 radix 全局 router 就会突然变得昂贵，这也是很多系统选择 lower-radix mesh 而不是高扇出单级交换的原因之一。

## Allocator：不一定最大，但经常最卡频率

allocator 的面积未必像 buffer 那样压倒性，但它经常是时序敏感路径，尤其在：

- VC 数量较多
- output port 候选者多
- 做复杂优先级、aging 或 speculative allocation

这会带来一个典型 trade-off：

- 更聪明的 allocator 可能改善吞吐和尾延迟
- 但也可能拖低频率，或迫使你加 pipeline

对 chip-wide NoC，这种频率损失的系统代价常常比单个 router 的局部优化更重。

## 链路宽度不是白给吞吐

把 link 做宽，看起来最直接：每拍搬更多位。但它会同时抬高：

- buffer 宽度
- crossbar 位宽
- driver 切换能耗
- 布线占用

所以 link width 从 128b 到 256b，不是在“白送一倍带宽”；它可能同时让 router buffer、crossbar 和物理线成本一起显著上升。

这就是为什么很多 NPU 不会无限加宽单条链路，而会在 `多条较窄链路 / 更规则 topology / 更强局部复用` 之间重新平衡。

## 一个定量例子

假设 router 参数：

- 5 ports
- 4 VC / port
- 6 flit depth / VC
- 128b flit

input buffer bits:

```text
5 * 4 * 6 * 128 = 15360 bits
```

若改成 256b flit：

```text
5 * 4 * 6 * 256 = 30720 bits
```

仅 input buffer bits 就翻倍，还没算 crossbar 和链路驱动。这个简单计算足以说明：位宽优化从来不是单点局部改动。

## 对 deterministic NPU 的特殊含义

deterministic NPU 通常不愿意把大量性能押在“更深 buffer、更复杂 allocator、更动态策略”上，因为那会让最坏情况分析更松、更难证。

所以更常见的取向是：

- VC 数适中
- buffer 深度覆盖 credit round-trip 再留少量裕量
- allocator 策略简单可分析
- topology 和调度优先帮助消除热点

换句话说，deterministic NPU 更偏爱“在系统层减少冲突”，而不是“在 router 内部吞掉所有冲突”。

## 常见误解

常见误解：router 性能不够，就优先优化 route compute。  
实际上：很多时候真正吃面积和功耗、也更容易拖慢频率的是 buffer、crossbar 和 allocator。

常见误解：更深 buffer 是最安全的保守选择。  
实际上：它会显著增加面积和在途积压，对 worst-case latency 与功耗都未必友好。

## 一句话理解

router 的三角关系是：buffer 决定你能吞多少抖动，crossbar 和 link width 决定你每拍能过多少位，allocator 决定这些资源如何被分；三者共同定义性能、面积和频率边界。

## 建模启示

这一页最适合抽成参数模型：

```text
RouterSpec {
  num_ports
  num_vcs
  vc_depth
  flit_width
}
```

并导出一阶成本量：

```text
buffer_bits = num_ports * num_vcs * vc_depth * flit_width
```

如果只做 early-stage architecture exploration，可以把 router 动态能耗近似成：

- `buffer_read_write_energy * flit_moves`
- `crossbar_energy * crossbar_traversals`
- `link_energy * phit_transfers`

如果关心时序与频率，则至少要增加：

- `allocator_fan_in`
- `crossbar_radix`
- `link_pipeline_stages`

因为这些参数通常比 `route_compute_logic_size` 更接近真实频率瓶颈。
