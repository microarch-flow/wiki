# 半导体与电路基础

<span id="半导体基础" aria-hidden="true"></span>在电路图上，一个反相器只占一个符号。输入电压从低变高时，它怎样把输出电压拉低？如果下一级是寄存器，又该等到什么时候采样？这两个问题把硅里的电荷、晶体管里的电流和电路里的时钟连在了一起。

先跟着电子看清二极管为什么会整流，再沿 MOS 沟道走到一个会翻转的逻辑门。想追问时钟从哪里来，可以从晶体管放大读到 PLL。想理解芯片为什么耗电、为什么有频率上限，可以从门的负载读到供电与时序。最后一篇把电路图中的反相器对应到硅片、封装和板卡。

## 阅读顺序

1. [从电子到二极管](electrons-to-diode/README.md)。从硅中的电子状态、掺杂与载流子出发，跟踪 PN 结的势垒怎样形成，再看电源正接和反接时电子各往哪里走。
2. [MOS 管与沟道电流](bands-to-channel/README.md)。在同一只 NMOS 上分两次调电压。先看栅极隔着绝缘层怎样让硅表面出现电子，再看源漏之间有压差时电子怎样流动。
3. [从 MOS 管到逻辑门](cmos-logic-gates/README.md)。先给单只 NMOS 的输出端接一只电容，再加上一只 PMOS。沿着充放电路径读出反相器的输出，接着用串联和并联推导 NAND 与 NOR。
4. [从硅到门电路](silicon-to-logic/README.md)。想沿另一条器件路线走，可以从 PN 结继续跟踪一个电子，看它怎样在 NPN 管中被注入、传输和收集。
5. [从电容充电到时钟边沿](voltage-to-clock/README.md)。先算电容电压升到门限需要多久，再看电路怎样反复翻转、石英晶体怎样提供频率参考。最后回到寄存器，看输入数据为什么要在时钟边沿前后保持稳定。
6. [晶体管的小信号放大](transistor-amplifier/README.md)。给栅极叠加 5 mV，沿着漏电流和负载电阻算出输出电压。
7. [石英振荡器的起振与稳幅](quartz-oscillator/README.md)。沿 Pierce 回路辨认选频、起振、稳幅与整形。
8. [锁存器、触发器与二分频](latch-and-divider/README.md)。让两只反相器保持一个比特，再逐沿数出触发器的输出周期。
9. [PLL 怎样实现二倍频](integer-pll/README.md)。以 25 MHz 为参考，从 40 MHz 的初始振荡出发，看反馈怎样把输出调到 50 MHz。
10. [扇出、布线与门延迟](fanout-and-wire-delay/README.md)。分别改变负载电容和导线电阻，看远端电压何时越过门限。
11. [翻转能量与芯片功耗](switching-energy-and-power/README.md)。从单次翻转的能量，算到一组节点的平均功率，比较相同频率下的不同任务。
12. [降压与时钟频率](supply-voltage-and-frequency/README.md)。先算降压节省的能量，再看数据路径还能否在一拍内完成。
13. [IR drop 与本地去耦](ir-drop-and-decoupling/README.md)。沿供电和回流路径算电阻压降，再看同时翻转时去耦电容怎样供电。
14. [PVT 与路径延迟](pvt-and-path-delay/README.md)。改变工艺、电压和温度，分别检查数据到得太晚和太早。
15. [从反相器到芯片封装](inverter-to-package/README.md)。从两只管子的剖面看到封装和板卡，再辨认 GPU 与 HBM 之间的连接。

## 接着往哪读

想知道芯片怎样做乘法，可以从几个输入位画起，看逻辑门怎样生成部分积，部分积又怎样相加。见[从部分积到 MAC](../microarchitecture/01-datapath/multiply-accumulate-from-gates.md)。

想知道时钟能跑多快，可以跟着数据走过两个寄存器之间的一段逻辑，算一算它能否赶上下一个采样边沿。见[电路与时序基础](../microarchitecture/02-pipeline/electrical-timing-foundations.md#4-算一条路径需要多长的时钟周期)。

想看反相器的剖面怎样一步步加工出来，或继续追踪 2.5D、3D 和 HBM 的封装工艺，可以从[芯片开发与实现中的 FAB 制造与封测](../chip-development/FAB/wiki/README.md)进入。
