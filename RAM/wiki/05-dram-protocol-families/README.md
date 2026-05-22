# DRAM 协议层

上级：[`RAM/wiki/`](../)
相关：[DRAM 基础](../04-dram-foundations/README.md), [Memory Controller](../06-memory-controller/README.md)

## 这页在回答什么问题

上一章已经把 DRAM 的物理和阵列逻辑搭起来了，这一章要回答的是：这些底层约束是如何一步步被接口化、标准化、产品化，最终变成系统能看见的命令、时序参数和不同协议家族。也就是说，这里不是另起一条新主线，而是在讲“物理债务如何被翻译成协议契约”。

## 正文

很多人第一次接触 DRAM，往往是从协议名词开始的：`DDR4`、`DDR5`、`LPDDR`、`GDDR`、`HBM`、`tRCD`、`CL`、`burst length`。这种入口当然现实，因为系统工程师和软件工程师最常接触的就是这些接口术语。但如果只停在这一层，协议会显得像一堆很难记的常数和标准碎片。上一章已经把根因讲清楚了：DRAM 的 cell 太弱、访问必须先开行、refresh 不可取消、bank 并行有限、core 与 I/O 节奏脱节。现在这一章的任务，就是把这些根因一条条映射到协议层。

这章里的每一篇，其实都可以读成“上一章某个物理约束，在系统接口中留下了什么痕迹”。`commands-act-rd-wr-pre.md` 解释为什么 DRAM 不可能只暴露一个抽象的 load/store 语义，而必须显式拆成 ACT、RD、WR、PRE 这样的阶段。`timing-parameters-trcd-trp-tras.md` 解释为什么这些命令之间必须带着一组看似琐碎、实则来自感测、恢复和预充预算的时间约束。`why-double-data-rate.md` 则把上一章讲过的 core/I/O 剪刀差，翻译成 DDR 这种“在同一时钟周期内多搬一部分数据”的接口演化。

从这里开始，协议家族之间的分化也会变得更有逻辑。`DDR`、`LPDDR`、`GDDR`、`HBM` 并不是四个彼此无关的名字，而是站在同一套 DRAM 物理基础上，针对不同系统目标重新布置 trade-off 的几条路线。通用服务器主存重视容量、生态和板级扩展，所以 DDR 路线会围绕通用性和通道扩展去平衡；移动设备更在意功耗和待机行为，所以 LPDDR 会对供电状态、I/O 摆幅和自刷新机制更敏感；图形和独立加速器更在意总带宽，于是 GDDR 会把单 pin 速率和更激进的接口预算往前推；HBM 则更进一步，把协议和堆叠/近距 I/O 绑在一起，换取超高带宽密度和更好的每 bit 能耗。

这一章还有一个非常重要的阅读边界：它讲的是“协议为何这样设计”，而不是“控制器如何利用这些协议做调度”。也就是说，这里要先把可用的动作、时序边界和产品路线区别讲清楚；等进入 `06-memory-controller/`，再讨论 FR-FCFS、page policy、refresh 管理和地址映射如何在这些边界内做决策。这个顺序不能倒，因为如果先看调度策略，再回头看协议，就很容易把很多控制器行为误以为是经验技巧，而看不到它们其实是在为特定 timing 和资源共享限制找最优缝隙。

读这一章时，最好始终带着两个问题。第一，这个协议机制在补哪一层物理短板？例如 burst 和 prefetch 是在补 core/I/O 速率不一致，bank group 是在补 bank 并行进入高速接口时代后的资源争用。第二，这个协议分化在押注哪一种系统目标？例如 LPDDR 的低功耗状态机和 HBM 的超宽近距接口，分别说明了移动系统和高带宽加速器愿意接受的代价并不相同。只要沿着这两个问题去读，协议就不会再是一堆平铺参数，而会重新长回物理和系统根因。

从建模角度看，这一章也标志着 DRAM 模型的第二次抬层。`04` 章更多是在说阵列为什么长这样；到了这里，模型需要开始显式具备 `command vocabulary`、`timing guards`、`burst transfer behavior` 和 `power-state differences` 这些协议级对象。也就是说，从这一章开始，系统不再只是面对一个“有 open row 的 bank 阵列”，而是在和一个带明确命令语义与时序契约的存储接口打交道。

## 一句话理解

这一章讲的是 DRAM 的底层物理与阵列约束如何被翻译成系统可见的命令、timing 参数和不同协议家族，而不是凭空多出了一套标准术语。

## 建模启示

这章对应的核心建模转变，是在 `DramArrayModel` 之上再加一层协议接口模型。也就是说，访问不再只是“请求打到某 bank 某 row”，而是要经过一串显式命令和时序守卫条件。协议层最少要提供：可发哪些命令、命令之间隔多久、一次数据传输是多长 burst、功耗状态机是否影响可访问性。

一个适合作为后续各页公共底座的抽象草图可以是：

```text
DramProtocolModel {
  family: enum { DDR, LPDDR, GDDR, HBM }
  supported_cmds: set { ACT, RD, WR, PRE, REF }
  timing_table: object
  burst_length: int
  prefetch_factor: int
  power_states: set<object>
}
```

配合上一章的阵列状态，最小交互形式可以写成：

```text
if cmd_is_legal(protocol, bank_state, now):
    issue(cmd)
else:
    stall_until_legal()
```

如果只做非常粗的性能估算，你可以把协议差异折叠成“不同 family 的有效带宽和典型延迟”；但只要你要比较 DDR/LPDDR/GDDR/HBM 的真实 trade-off，或者要分析 controller 为什么必须这样调度，这一层显式协议模型就不应该省略。
