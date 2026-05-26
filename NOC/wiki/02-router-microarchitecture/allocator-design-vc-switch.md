# Allocator Design VC Switch

上级：[02 Router Microarchitecture](./README.md)
相关：[Router Pipeline Stages](./router-pipeline-stages.md), [../04-routing-and-flow-control/arbitration-policies.md](../04-routing-and-flow-control/arbitration-policies.md)

## 这页在回答什么问题

VC allocator 和 switch allocator 分别在竞争什么资源，为什么它们既紧耦合又不能混为一个仲裁问题。

allocator 是 NoC router 真正的“调度核心”。很多性能差异，表面看像 topology 差异，实际上是 allocator 策略和规模把结果拉开了。

## VC allocator：决定 packet 能不能建路

VC allocator 只服务 header flit。它的任务是：在目标 output port 的下游 router 上，找一个空闲 VC 分配给这个 packet。

这个动作看似简单，实则是在申请长期资源。因为一旦 header 成功绑定下游 VC，该 packet 通常会持续占着它直到 tail 离开。

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

这也是很多论文在讲“加 VC 提升吞吐”时容易淡化的代价：VC 不是白来的，它会把 allocator 做大，而 allocator 是频率敏感路径。

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

如果只关心 steady-state 吞吐，可以把 allocator 策略近似成概率服务模型；如果关心 stall attribution、tail latency 或 age-based fairness，就必须逐拍模拟仲裁结果，因为 `VC_UNAVAILABLE` 与 `SWITCH_CONFLICT` 在系统归因上不是一回事。
