# 漏电、保持电压、low-power SRAM 设计

上级：[SRAM 基础](./README.md)
相关：[为什么 SRAM 在先进制程下不再线性 scale](./sram-process-scaling-challenge.md), [MCU 里的 TCM，为什么实时性需要确定性 SRAM](../03-sram-applications/tcm-itcm-dtcm-in-mcu.md)

## 这页在回答什么问题

SRAM 不需要 refresh，为什么仍然会成为低功耗设计里的难点。更具体地说，当你想把一大片 SRAM 省电地留在芯片上时，漏电、保持电压、局部掉电和唤醒延迟之间到底在交换什么。

## 正文

很多人第一次接触 SRAM 时，会自然得出一个结论：它不像 DRAM 那样需要 refresh，所以保持数据应该几乎”免费”。这就像说”自己的房子不用交房租，所以居住成本为零”——你不交房租，但物业费、水电费、折旧维护一样不少。SRAM 的确不需要周期性刷新，但它要维持双稳态，前提是电源持续存在，而只要电源持续存在，交叉耦合反相器和访问相关外围就会持续消耗静态功耗。于是 SRAM 的保持成本不是 refresh bandwidth，而是 `leakage + retention voltage + always-on supply` 这组问题。

先把保持和掉电彻底分开。所谓 `hold` 或 `retention`，指的是 cell 在不被主动访问时，仍然依赖某个供电电压维持当前状态。所谓 `power-gating`，则是把供电部分或完全切掉，此时若没有额外保存机制，普通 SRAM 数据就会消失。也就是说，SRAM 的“静态”从来不是“断电不丢”，而只是“不断电就能靠正反馈自保持”。常见误解是把“无需 refresh”误解成“可以很便宜地一直存着”；实际上，大面积 SRAM 长时间待机时，静态漏电本身就会成为系统功耗预算里的显著部分。

为什么漏电会变成核心问题，要回到 cell 的本质。一个 6T cell 由始终偏置在某个状态的晶体管网络组成，只要 VDD 在，晶体管就不会真正“完全不耗电”。在较大工艺节点下，单个 cell 的 leakage 也许不显眼；但当片上 SRAM 达到 MB 甚至几十 MB 量级时，数百万到数十亿个 bit 的漏电会积成真实的 standby power。先进制程下，这个问题会更尖锐，因为为了追求速度常常使用更激进的器件选项，而阈值降低、器件更小、变异更大时，亚阈值漏电和栅漏往往更难忽略。于是 SRAM 宏会天然成为芯片待机功耗的大头之一。

这就引出 `retention voltage`，也就是维持当前 cell 状态所需的最低供电电压。这个电压通常显著低于正常工作电压，但不是可以无限往下拉的。电压一旦低到某个阈值以下，cell 的双稳态 margin 会缩小到不足以对抗失配、噪声和温度扰动，原本稳定的 0/1 就可能翻转或变得不可预测。这里要注意，retention voltage 和 functional Vmin 不是同一个量。前者回答“能不能不访问只保住数据”，后者回答“能不能在这个电压下继续可靠读写”。在 low-power 设计里，这两个门槛常常决定了不同的睡眠模式。

一个典型的模式划分可以用酒店来类比。`active mode` 就是客房正在使用——灯开着、空调开着、随时可住。`retention mode` 就是客房暂时没人但保留预订——灯关了、空调调到最低，但行李还在房间里，客人回来时只需要重新打开灯就行。`power-off mode` 就是彻底退房——房间完全断电，行李已被清走，下次入住要重新 check-in 和搬行李。工程上真正难的不是给它们起名字，而是决定哪些 bank 或 sub-array 进入哪种模式，以及模式切换时愿意付出多少唤醒延迟和控制复杂度。

为什么不把所有 SRAM 都直接降到 retention 模式？因为 retention 并不是零代价。第一，retention 供电轨本身要一直存在，意味着仍然要保留某种 always-on 电源岛。第二，低电压下对噪声、IR drop 和温度变化更敏感，因此电源完整性和 margin 要更保守。第三，从 retention 唤醒到 active 往往需要一定恢复时间，外围控制和时钟树也要重新拉起。第四，并不是所有 SRAM 宏都愿意在极低 retention voltage 下保证全部 PVT 角可用，因此保守设计会把 retention voltage 留得更高，省电收益又被削弱。也就是说，retention 不是“免费待机”，而是“用一部分静态功耗换取不丢数据和较快恢复”。

这也是 low-power SRAM 设计里为什么会有大量辅助技巧。最基础的是 `bank-level power gating` 或 `subarray-level sleep`，让不活跃区域单独降压或断电，而不是整块 SRAM 一起保持。再进一步，会有读写 assist 和 retention assist，用来在低压下提高可读、可写或可保持的 margin。某些设计还会采用高 Vt 器件、stack effect、局部 body-bias、分裂供电或 retention latch 式外围方案，以在待机功耗和唤醒时间之间找到新平衡。常见误解是把 low-power SRAM 看成“正常 SRAM 加个睡眠信号”；实际上，它往往是一整套从 cell、外围到电源岛的协同设计。

这里有一个很现实的 trade-off：就像冰箱里的食物——你想保鲜越多食物，电费越高；你想省电关掉冰箱，食物就会变质，下次要重新采购。对 MCU 的 TCM、实时控制代码或始终在线缓冲区，数据丢失代价高（像冰箱里的珍贵药品），因而更愿意保 retention。对某些推理加速器里的中间 buffer，如果 workload 切换后本来就要重新装填（像每天都会买新鲜食材的厨师），那么完全 power-gate 再 reload 可能反而更划算。系统设计里最差的做法，是把所有 SRAM 一刀切地留在一个模式里，不区分热数据、冷数据和恢复代价。

从阵列组织角度看，前一篇讲的 bank/sub-array 切分，在这里会再次变成低功耗粒度。因为你只有把 SRAM 切成多个相对独立的电源与控制片段，才能做到“只保留必要局部”。这意味着 low-power 能力并不是后加的属性，而是从阵列组织阶段就要开始考虑。如果某个 buffer 被做成一个过于一体化的大宏，后面即使从系统上看很想只休眠一部分，电路上也未必做得到。

这套问题在先进制程和 AI 芯片里会更加突出。先进制程下 leakage 更敏感，大片 SRAM 的待机成本更难忽略；AI/NPU 场景下又常常有大量片上 buffer，其中有的承担长生命周期权重缓存，有的只承载很短的流水中间数据。两类数据显然不该共享完全相同的 low-power 策略。后面到了 `npu-memory-hierarchy.md` 和 `data-movement-first-principle.md`，这个差异会转化成“哪些层应该常驻，哪些层应该按 tile 周期性装填”的系统决策。

所以，“SRAM 不需要 refresh”并不等于“SRAM 保持很便宜”。更准确的说法是：SRAM 把保持成本从 refresh 时隙，换成了持续供电和漏电约束。low-power SRAM 设计真正要回答的问题，不是“能不能睡”，而是“睡到什么程度、保留哪些状态、唤醒时愿意付多少时间和能量”。只要系统里片上 SRAM 规模上来，这些就不会是边角问题。

## 一句话理解

SRAM 的保持成本不表现为 refresh，而表现为必须持续供电才能维持双稳态，所以 low-power 设计的核心是在 leakage、retention voltage、数据保留粒度和唤醒代价之间找平衡。

## 建模启示

这篇对应的关键建模后果是：SRAM 不能只被建模成“访问时耗能、空闲时零成本”的资源。即使没有访问，它也可能处于 `active-idle`、`retention` 或 `power-off` 这几种不同状态，而这些状态会决定背景功耗、可访问性和唤醒延迟。对很多系统级探索，漏掉这组状态，功耗结论会明显失真。

一个最小可用的状态机草图可以是：

```text
enum SramPowerState { ACTIVE, RETENTION, OFF }

SramPowerModel {
  active_leakage_mW: float
  retention_leakage_mW: float
  wake_from_retention_cycles: int
  wake_from_off_cycles: int
  retention_voltage_mV: int
  functional_min_voltage_mV: int
}
```

对应事件可以写成：

```text
event EnterRetention(array_id)
event ExitRetention(array_id)
event PowerGate(array_id)
event PowerRestore(array_id)
```

如果只关心吞吐，`wake_from_retention_cycles` 和 `wake_from_off_cycles` 也许可以忽略；但只要你要比较不同 buffer 的生命周期管理，或者分析 always-on 区域的功耗占比，就必须显式区分 `RETENTION` 和 `OFF`。这两者在系统里的含义完全不同：前者保状态、耗更少电；后者不保状态、恢复更慢，但静态功耗最低。

如果进一步把这篇和前一篇的先进节点问题结合起来，一个很实用的约束是：

```text
guard supply_voltage >= retention_voltage_mV for state == RETENTION
guard supply_voltage >= functional_min_voltage_mV for state == ACTIVE
```

这能直接防止模型给出一种不现实的解：把大片 SRAM 长期留在超低电压下，既假装保住数据，又假装随时可访问。
