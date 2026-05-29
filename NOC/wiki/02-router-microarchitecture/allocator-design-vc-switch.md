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

这也是很多论文在讲"加 VC 提升吞吐"时容易淡化的代价：VC 不是白来的，它会把 allocator 做大，而 allocator 是频率敏感路径。

## 三种主流 allocator 的参数化模型

第一版 simulator 必须能正交比较 separable / iSLIP / wavefront 三种方案。三者的延迟、复杂度、效率有显著差异，下面给出可直接代入 `R` 公式的参数化形式。

### 通用符号

| 符号 | 含义 |
|------|------|
| `P` | router radix（输入/输出端口数） |
| `V` | 每端口 VC 数 |
| `N = P · V` | 总候选数 |
| `t_pipe` | allocator 占用的流水线拍数（决定关键路径深度） |
| `η` | allocator 效率 = `成功授予数 / 期望最大匹配数`，取值 [0, 1] |
| `K` | 同一输出端口/输出 VC 的竞争者期望数 |

`η` 是把 allocator 抽象成"匹配问题求解器"后的效率系数：完美匹配 `η = 1`，简单 round-robin 在高负载下可能 `η = 0.5~0.7`。它直接进入 [`credit-based-flow-control.md` 的 R 公式](./credit-based-flow-control.md#downstream_buffer_residency)：

```text
E[VA_contention] = (K_VA - 1) / (2 · η_VA)
E[SA_contention] = (K_SA - 1) / (2 · η_SA)
```

### 1. Separable Allocator

把"N → M 匹配"拆成两级独立仲裁：每个 input 先选一个 request、每个 output 再从被请求自己的 input 里选一个 grant。两级都用并行 round-robin / fixed-priority。

```text
separable:
  t_pipe          = 1 cycle (input 端 + output 端串联在同一拍内)
  gate_depth      ∝ log(P) + log(V)
  η_VA            ≈ 0.6 ~ 0.75 (依赖请求分布均匀性)
  η_SA            ≈ 0.65 ~ 0.80
```

特点：
- 实现最简单，时序友好，频率可推到 1 GHz+
- 局部最优不等于全局最优：input0 的本地胜者可能输给别人，input0 上原本可以让另一个 VC 胜出去往不同 output，但本拍机会被浪费
- η 偏低的根因就是上面这种"丢失的并行匹配机会"

适用：第一版、对面积/频率敏感、deterministic 工作负载。

### 2. iSLIP Allocator

separable 的迭代加强版。每轮里 input 选、output 选、然后用本轮 grant 信息更新优先级；多轮迭代收敛到接近最大匹配。

```text
iSLIP:
  t_pipe          = I cycles (典型 I = 1~3 iteration)
  gate_depth      ∝ I · (log(P) + log(V))
  η_VA            ≈ 1 - 0.3^I             # 例如 I=2 → η≈0.91, I=3 → η≈0.97
  η_SA            ≈ 1 - 0.3^I
```

特点：
- 多迭代意味着 t_pipe 增长，会直接拉长 R
- 但 η 显著上升，单 cycle 吞吐更高
- 在 P · V 很大（高 radix + 多 VC）时收益最大

关键 trade-off：

```text
R_with_iSLIP = R_fixed + I + E[contention_with_η(I)]
            ≈ R_fixed + I + (K-1)/(2·(1-0.3^I))
```

`I=2` 通常是甜点：t_pipe 多 1 拍，但 η 从 0.7 升到 0.91，contention 项的下降通常 > 1 拍。

适用：高 radix（≥ 6 port）、高 VC（≥ 4）、吞吐敏感。

### 3. Wavefront Allocator

把 P×V 候选排成对角线波前，沿对角线串行扫描，每个对角线上的所有候选者并行授予；扫完一遍即得全局最大匹配。

```text
wavefront:
  t_pipe          = 1 cycle (但关键路径串行 P+V 级门)
  gate_depth      ∝ P + V                  # 注意是 +，不是 log
  η_VA            ≈ 0.95 ~ 1.0             # 接近最优匹配
  η_SA            ≈ 0.95 ~ 1.0
```

特点：
- 1 拍内得全局最优匹配，对低频率系统很有吸引力
- 关键路径长度 ∝ P + V，时序压力大；P=8 + V=8 = 16 级门通常顶到 600~800 MHz
- 公平性需要额外的优先级旋转机制配合

适用：对吞吐和公平性要求都很高、但频率不顶天的场景。

### 三者对比表

| 维度 | Separable | iSLIP (I=2) | Wavefront |
|------|-----------|-------------|-----------|
| `t_pipe` | 1 | 2 | 1 |
| 关键路径 | log(P) + log(V) | 2·(log P + log V) | P + V |
| `η`（典型）| 0.7 | 0.91 | 0.97 |
| 实现复杂度 | 低 | 中 | 高 |
| 频率上限（5-port, 4-VC, 14nm）| ~1.5 GHz | ~1.2 GHz | ~800 MHz |
| 频率上限（8-port, 8-VC）| ~1.0 GHz | ~800 MHz | ~500 MHz |
| 适合 P·V | ≤ 20 | 20 ~ 64 | 任意，但受频率约束 |

### 把 allocator 模型代回 R

用上面参数把 [credit-based-flow-control](./credit-based-flow-control.md#典型数值例子) 里的"短线 R≈8"和"长线 R≈12.5"重算一遍：

5-port 4-VC、`K=2`：

| Allocator | t_pipe | E[VA+SA contention] | R (短线) |
|-----------|--------|---------------------|----------|
| Separable | 1 | `(1)/(2·0.7) · 2 = 1.43` | 1+3+1.43+2 = **7.4** |
| iSLIP I=2 | 2 | `(1)/(2·0.91) · 2 = 1.10` | 1+3+1.10+2 + (extra pipe) ≈ **8.1** |
| Wavefront | 1 | `(1)/(2·0.97) · 2 = 1.03` | 1+3+1.03+2 = **7.0** |

8-port 8-VC、`K=4`：

| Allocator | t_pipe | E[VA+SA contention] | R |
|-----------|--------|-------------------|---|
| Separable | 1 | `(3)/(2·0.7) · 2 = 4.3` | 1+3+4.3+2 = **10.3** |
| iSLIP I=2 | 2 | `(3)/(2·0.91) · 2 = 3.3` | 1+3+3.3+2 + 1 = **10.3** |
| Wavefront | 1 | `(3)/(2·0.97) · 2 = 3.1` | 1+3+3.1+2 = **9.1** |

读法：
- 低竞争（`K=2`）下 separable 接近最优，iSLIP 多花的拍数不值
- 高竞争（`K=4`）下三者 R 差异 ~10%，但**频率上限差异 2 倍**，按 `R / frequency` 算实际墙钟时间，separable 反而胜出
- 这就是为什么大型 router 仍常用 separable + 智能 priority rotation 而非全 wavefront

**结论：allocator 的"最优"是 R × cycle_time 的联合最小**，不是 R 或 frequency 单独最小。架构探索时必须把 frequency 作为 sweep 维度，否则 iSLIP / wavefront 会被错误地推荐。

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
  t_pipe          # 1..3
  iterations      # iSLIP only
  eta_VA; eta_SA  # 模型层效率系数，由 type 派生
  priority_rotation := ROUND_ROBIN | OLDEST_FIRST | CLASS_WEIGHTED
}
```

如果只关心 steady-state 吞吐，可以把 allocator 策略近似成概率服务模型（用 `η` 直接缩放 contention 项）；如果关心 stall attribution、tail latency 或 age-based fairness，就必须逐拍模拟仲裁结果——因为 `VC_UNAVAILABLE` 与 `SWITCH_CONFLICT` 在系统归因上不是一回事，且 `η` 折叠会把 tail latency 整体压低。

最重要的一条建模约束：**架构探索 sweep 必须把 `(allocator_type, frequency_GHz)` 作为联合维度**。单独 sweep `allocator_type` 会让 iSLIP/wavefront 看上去更优，但它们的 `frequency` 折扣往往把收益抵消。详见上文 [allocator 对比表](#三者对比表) 的频率列。
