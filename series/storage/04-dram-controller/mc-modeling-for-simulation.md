# DRAM 控制器建模：状态、事件与验证

上级：<span id="mc-在-cycle-level-仿真里的建模方法"></span>[DRAM 控制器与请求调度](./README.md)

相关：[DRAM 命令时序](../03-dram/protocols/timing-parameters-trcd-trp-tras.md) · [QoS、公平性与隔离](./qos-multi-master-arbitration.md) · [存储器建模模板](../reading-and-reference/02-reference/memory-modeling-template.md)

## 这页在回答什么问题

MC 在 cycle-level 仿真里的建模方法，应保留哪些状态和事件，才能回答指定问题？本文给出可裁剪的模型边界、命令合法性示例和验证办法；它不是任何特定 DRAM 协议的完整实现。

## MC 在 cycle-level 仿真里的建模方法 {#保留哪些离散状态和事件}

先选择要回答的问题，再选粒度：

| 模型 | 适合的问题 | 不能仅凭该模型推断 |
| --- | --- | --- |
| 已校准的固定或统计延迟与带宽 | 已有条件下的早期系统估算。 | 未校准的新地址映射、调度或刷新策略的细节。 |
| 请求队列与 bank 行状态 | 比较明确假设下的行复用、排队和资源竞争。 | 未建模的具体命令时序和电气行为。 |
| 命令与数据事件 | 检查所实现模式下的发令、DQ 窗口和策略交互。 | 模拟电压波形、器件正确性或所有未实现模式。 |

状态需要与问题对应。研究页策略时要有行状态和关行决策；研究写排空时要有写队列和方向切换；研究刷新和 QoS 时要有义务、作用范围与相应仲裁。更细的模型仍需参数来源和验证，粒度本身不保证准确。

## 状态与事件循环

命令模型通常需要请求队列及其容量、每个 bank 的行和忙碌状态、独立命令域的发射能力、DQ 的**未来传输区间**、必要的跨 bank 时间约束，以及刷新和策略状态。完整 bank 标识至少包含所建模的 channel、rank、bank group 和 bank；可以用一一对应的展平标识代替。

仅保存当前 DQ 方向和一个“现在是否空闲”的标志不足以检查未来重叠。对给定模式，可在列命令发射时按其读写延迟和 burst 长度预留未来数据窗口，再检查已有窗口与读写转向约束。具体 DQ/DQS 边沿和保护间隔应按目标器件实现。

按目标协议需要跟踪不同 bank group 的 `tCCD`、不同 bank 的 `tRRD`，以及 `tFAW` 的滚动 ACT 窗口；同 bank 的再次 ACT、PRE、刷新和电源状态有其他约束。这些名称和适用关系不能无条件套用到所有 DRAM 家族。

一个事件驱动模型可以按下列顺序推进。这里将同一时刻的到达和完成事件先处理，再做命令仲裁；若模型采用其他顺序，需要明确并保持一致。

```text
while simulation_running:
    process_arrivals_and_completions(now)
    for domain in independent_command_domains:
        candidates = candidates_for(domain, state)
        legal = filter_legal(candidates, state)
        chosen = choose_by_policy(legal)
        if chosen exists:
            issue_and_reserve_atomically(chosen)
    now = earliest_future_event_after(now)
```

独立命令域按固定顺序遍历；`filter_legal` 检查全部适用时序、状态、顺序及资源约束。示例假设每个域在一个发射槽最多发射一条命令。若模型支持同一域同时发射多条命令，需要逐条重新检查并预留资源；不同域的同刻动作共享资源时，也需要重新检查或联合预留。若没有候选，下一时刻必须考虑 `tRCD`、`tRP`、刷新恢复和独立命令域下一发射槽等事件，不能只等待外部请求。策略还要及时安排强制刷新和必要准备，单次合法发射不保证未来截止条件一定满足。若系统空闲，可等待未来到达；若仍有待处理请求却找不到任何未来事件，应报告模型错误或无法前进的原因。

[DRAMsim3](https://github.com/umd-memsys/DRAMsim3)将 bank 状态、channel 状态、命令队列和配置分开组织，可作为一种模拟器结构参考；它的具体策略不等于所有控制器的设计。

## 折叠模型的适用边界

对同一发射事件，假设各前置动作已经完成，三个独立约束给出的最早时刻分别为 row ready@10、refresh release@8、DQ ready@6，则最早发射为 **max(10, 8, 6) = 10**，不是三者相加。若刷新阻止了此前的 ACT，就必须先重新计算 ACT 和 row ready；不能沿用旧的 10。

折叠等待时，可以在明确的时间线上计算阻塞区间并集，或使用互斥的归因规则。把行命中、刷新和转向折成固定平均值可用于校准范围内的粗估，但不能自动预测改变到达顺序、映射或仲裁后的结果。

## 同 bank PRE 记分板

以下仅示意 DDR4、BL8、无写 CRC、CA parity 和 CS-to-CA latency 关闭的显式 PRE。时间以命令采样 CK 为单位，`nRAS`、`nRTP`、`nWR`、`nRP` 由目标器件及模式换算；`WL = AL + CWL`。其他协议条件仍须另查。

```text
on ACT(bank, now):
    pre_ready[bank] = now + nRAS
on RD(bank, now):
    pre_ready[bank] = max(
        pre_ready[bank], now + AL + nRTP)
on WR(bank, now):
    write_ref = now + WL + BL/2
    pre_ready[bank] = max(
        pre_ready[bank], write_ref + nWR)
can_issue_PRE = (bank_is_open
    and now >= pre_ready[bank]
    and other_guards_allow)
on PRE(bank, now):
    next_act_ready[bank] = now + nRP
```

例如 WR 在周期 0，`AL=0、CWL=9、BL=8、nWR=12`：名义写数据窗口为 `[9, 13)`，写恢复参考沿为 13，写项要求 PRE 不早于 25。若同一行的 ACT 项要求 28，则这两项共同要求不早于 28；还须检查其他命令、总线、刷新和模式条件。自动预充应按目标规则建内部事件。详细依据见[时序文章](../03-dram/protocols/timing-parameters-trcd-trp-tras.md#ddr4-同-bank-显式-pre-的完整下界)。

### 用小例子验证模型

至少检查：两个真正独立的命令域可以在同一时刻各发合法命令；同一 DQ 的未来读写窗口不能冲突；PRE 同时满足 ACT 与所有列命令下界；刷新作用域及截止前准备正确；已发列命令不会重复发射；同址读写顺序和响应关联符合所选接口。为每个阻塞候选记录原因与释放时刻，便于定位分歧。

## 一句话理解

模型应保留影响目标问题的资源、状态和事件，并用具体规则验证命令与数据的合法性。

## 建模启示

明确输入地址、大小、方向、到达时间、依赖和来源，以及输出响应与统计的边界。比较 NPU 外存可预测性时，还需检查流量到达、共享路径、队列、维护动作和系统契约；列出策略参数不等于证明等待上界。
