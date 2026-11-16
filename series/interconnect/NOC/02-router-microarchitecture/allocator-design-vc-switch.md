# Allocator Design VC Switch

上级：[02 Router Microarchitecture](./README.md)
相关：[Router Pipeline Stages](./router-pipeline-stages.md), [../04-routing-and-flow-control/arbitration-policies.md](../04-routing-and-flow-control/arbitration-policies.md)

## 这页在回答什么问题

VC allocator 和 switch allocator 分别在竞争什么资源，为什么它们既紧耦合又不能混为一个仲裁问题。

allocator 是 NoC router 真正的“调度核心”。很多性能差异，表面看像 topology 差异，实际上是 allocator 策略和规模把结果拉开了。

## VC allocator：决定 packet 能不能建路

VC allocator 只服务 header flit。它的任务是：在目标 output port 的下游 router 上，找一个空闲 VC 分配给这个 packet。

这个动作看似简单，实则是在申请长期资源。一旦 header 成功绑定下游 VC，后续 flit 复用绑定。何时可供下一包分配取决于释放策略：严格策略要等下游 tail 离开并返回 free；若提前复用，则必须证明 FIFO 顺序与包上下文安全。见 [VC 状态与许可](../08-simulator-construction/core-data-structures.md#三种独立状态)。

所以 VC allocator 回答的是：“这个 packet 有没有资格继续往前走。”

它失败时，你看到的现象通常是：

- header 停在 VA
- body 已到达本地 buffer 但不能进入 SA
- 整个 packet 像被“按住不放”

这类 stall 更接近路径资源短缺，而不是瞬时争用。

## Switch allocator：决定这一拍谁过 crossbar

switch allocator 的对象是所有满足前进条件的队首 flit。它们已经知道要去哪、也已有下游 VC 绑定，此时争的是当前周期的物理 crossbar 通路。

所以 switch allocator 回答的是：“这一拍谁先走一步。”

它失败时的现象通常是：

- flit 继续留在队首
- 下一拍还可以再竞争
- packet 没有失去路径，只是这拍没抢到

这类 stall 更像瞬时局部拥塞，而不是长期资源不可用。

## 一个最小例子

假设 East 方向下游有 2 个空闲 VC，当前 router 里有 3 个 header 都想往 East：

```text
header A -> wants East
header B -> wants East
header C -> wants East
```

VC allocator 可能让 A 和 B 成功，C 失败。此时：

- A/B 进入 `ACTIVE`
- C 继续停在 `VA`

下一拍，A 和 B 的队首 flit 又要争当前 router 的 East output crossbar。switch allocator 可能让 A 先过、B 等一拍。

这说明：

- VC allocator 在决定谁有“长期通行证”
- switch allocator 在决定谁这拍能“过闸机”

## 为什么 allocator 复杂度会上升得很快

候选者一多，allocator 的组合逻辑会迅速膨胀。

设：

- `P` = 输入端口数
- `V` = 每端口 VC 数

那么参与 switch allocation 的候选上界接近 `P * V`。如果是 5-port、4-VC router，就是 20 个候选者；8-port、8-VC 就到 64 个量级。再加上每个 output port 都要独立仲裁，逻辑深度和布线都不轻。

这也是很多论文在讲"加 VC 提升吞吐"时容易淡化的代价：VC 不是白来的，它会把 allocator 做大，而 allocator 是频率敏感路径。

## 三种 allocator 与可复现的匹配

输入是本拍可服务的 input→output 请求图；输出是无冲突匹配，即一个 input 和一个 output 至多各参与一次。VC 分配还受下游 VC 可用性约束，资源持有期可跨多个 flit，不能用平均竞争者数直接推导 VA 持有时间。

| 方法 | 执行方式 | 需要测量的代价 |
| --- | --- | --- |
| separable | 以本地选择和 output 仲裁组成一轮匹配 | 被局部选择遗漏的匹配、延迟、面积和频率 |
| iSLIP | 每轮 request → output 按 RR grant → input 按 RR accept；仅第一轮成功匹配更新相应指针 | 迭代次数、匹配数、实现的 latency/II 和频率 |
| wavefront | 对请求矩阵按优先序传播，产生无冲突匹配 | 矩阵维度、优先级旋转及具体组合逻辑关键路径 |

例：两个 input `I0/I1`，两个 output `O0/O1`，请求为 `I0→{O0,O1}`、`I1→{O0}`。假设第一轮两 output 的 grant 指针都先选 I0，I0 的 accept 指针先选 O0。第一轮 grant 为 `O0→I0, O1→I0`，accept 得到 `I0→O0`，只匹配一条；第二轮剩余 I1 只请求已匹配的 O0，无法增加匹配。若第一轮 O0 先授予 I1、O1 授予 I0，则一次得到两条匹配。这个例子展示请求图和指针对结果的影响，不是三种算法性能排名。

多轮可以在同一拍展开为组合逻辑，也可以跨拍流水；iteration 数不等于固定 cycle latency。分别报告单次调度延迟、启动间隔 II、可实现时钟频率、每拍成功匹配数及 workload 分布。wavefront 的矩阵大小由实际输入/输出候选构造决定，不能通用写成 `P+V` 级门。η 可定义为某窗口的成功匹配数除以相同请求图上最大匹配数，但必须由相同工作负载仿真或测量获得，不能由算法名称代入固定系数。iSLIP 原始规则见 [McKeown 论文](https://yuba.stanford.edu/~nickm/papers/ToN_April_99.pdf)。

## 常见两级 switch allocation

很多实现会用两级仲裁：

1. 每个 input port 先在本地选一个候选 VC
2. 每个 output port 再在所有输入候选者之间选胜者

这样做不是形式主义，而是为了把一个大仲裁拆成多个小仲裁，降低时序压力。

一个简化时序：

```text
input 0: VC1 wins local selection
input 1: VC0 wins local selection
input 2: VC3 wins local selection

all want East
-> East output arbitration picks one
```

代价是局部最优不一定全局最优。比如 input0 选出来的本地候选输了，而该端口另一个想去 South 的 VC 原本可能本可在这拍获胜。要不要为这种情形做更复杂的选择逻辑，就是吞吐与实现复杂度的 trade-off。

## Speculative allocation 值不值得

有些高性能 router 会做 speculative allocation，例如 header 在等待 VA 成功的同时提前尝试 SA。这能压缩部分延迟，但也带来两个问题：

- 逻辑更难验证，因为“猜中”和“猜错”路径都要处理
- 对 deterministic 和可分析系统不友好，因为动态行为更复杂

对你的主线，speculative allocator 通常不是第一优先级。先把非投机、时序清晰的 allocator 建稳，通常更符合 deterministic NPU 的建模目标。

## 和 BUS arbitration 的相同点与不同点

相同点是：两者都在给稀缺资源定服务顺序。

不同点在于：BUS arbitration 常围绕“谁获得本次事务或 channel 使用权”；NoC 里至少有两层仲裁：

- packet 级长期资源分配
- flit 级短期资源分配

这正是 NoC allocator 比普通 BUS 仲裁更难的地方。你不仅要知道“谁先过”，还要知道“谁已经占着长期资源、谁只是暂时没抢到”。

## 常见误解

常见误解：VC allocator 和 switch allocator 只是两个名字，本质都是仲裁。  
实际上：它们都在仲裁，但争的是不同生命周期的资源；失败语义也完全不同。

常见误解：allocator 只影响公平性。  
实际上：allocator 还会影响频率、buffer 占用、packet 前进速度，以及系统是否容易产生长尾延迟。

## 一句话理解

VC allocator 决定 packet 有没有路权，switch allocator 决定这个周期谁先走一步；前者是长期资源申请，后者是短期资源调度。

## 建模启示

模型里建议把两类仲裁分成两个独立函数：

```text
vc_allocate(header_flit, output_port) -> downstream_vc | FAIL
switch_allocate(candidate_flits[], output_port) -> winner | NONE
```

至少保留这些状态：

- `vc_alloc_wait_cycles`
- `switch_alloc_wait_cycles`
- `downstream_vc_free_bitmap`
- `per_output_requesters`

allocator 参数化建议落成独立的配置对象，与 router 其他参数解耦：

```text
AllocatorConfig {
  type            := SEPARABLE | iSLIP | WAVEFRONT
  latency_cycles; initiation_interval
  iterations      # iSLIP only；可组合展开或跨拍
  measured_eta_VA; measured_eta_SA  # 同一负载下校准，不由 type 推导
  priority_rotation := ROUND_ROBIN | OLDEST_FIRST | CLASS_WEIGHTED
}
```

若用概率服务近似，应基于同负载校准，并单独验证尾延迟和等待分布；不能仅用平均 η 推导 VA 的 packet 持有期。逐拍模型则直接记录请求图、指针和 grant。比较方案时应联合报告匹配吞吐、时钟、延迟和 II，使用综合/布局或测量数据，而不是预设某算法频率折扣。
