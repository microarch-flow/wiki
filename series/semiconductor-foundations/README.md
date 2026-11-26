# 半导体与电路基础

<span id="半导体基础" aria-hidden="true"></span>在电路图上，一个反相器只占一个符号。输入电压从低变高时，它怎样把输出电压拉低？如果下一级是寄存器，又该等到什么时候采样？这两个问题把硅里的电荷、晶体管里的电流和电路里的时钟连在了一起。

<span id="延伸阅读" aria-hidden="true"></span>先跟着电子看清二极管为什么会整流。让两个结共用一片很薄的基区，就可以追问[发射区注入的电子怎样抵达集电极](electrons-to-diode/README.md#bjt)。沿 MOS 管这条路走，则能在[硅片剖面上找回反相器的输入、输出和电源线](cmos-logic-gates/README.md#physical-inverter)。把两个反相器接成反馈环后，就可以追问一个比特怎样保存、怎样被下一拍的新值改写。<span id="历史导读" aria-hidden="true"></span>想追问时钟从哪里来，可以从晶体管放大读到 PLL。想知道一拍要留多久，可以先读[电容充到半高要多久](fanout-and-wire-delay/README.md#rc-half)，再顺着门延迟、本地供电和寄存器的采样窗口往下读。

## 文章知识关系

十篇文章从电子与材料出发，逐步解释器件、逻辑电路、时钟，以及真实芯片中的功耗和时序约束。下表列出每篇文章要解决的核心问题，以及理解它时最有帮助的前置知识。表格按推荐阅读顺序排列；也可以根据下方的学习目标选择，不必始终从第一篇读起。

<figure class="foundation-article-map" markdown="1">

[![十篇文章的知识关系：电子与二极管→MOS 管→逻辑门，继而分向小信号放大到 PLL 的时钟路线、锁存器与触发器，以及门延迟到建立与保持的性能路线。触发器还关联 PLL 分频和时序采样。](assets/article-map.svg)](assets/article-map.svg)

<figcaption>实线表示知识主线的承接关系，虚线表示不同路线之间的联系。箭头不是强制阅读顺序。点击图可查看大图。</figcaption>
</figure>

<span id="阅读顺序" aria-hidden="true"></span>

| 文章 | 核心问题 | 建议先掌握 |
| --- | --- | --- |
| 1. [从电子到二极管](electrons-to-diode/README.md) | 硅如何导电，PN 结如何形成势垒并实现单向导通？ | 本系列起点 |
| 2. [MOS 管与沟道电流](bands-to-channel/README.md) | 栅极如何控制沟道，源漏电压如何驱动电流？ | 第 1 篇：能带、掺杂与载流子 |
| 3. [从 MOS 管到逻辑门](cmos-logic-gates/README.md) | NMOS 和 PMOS 如何通过充放电产生逻辑 0 和 1？ | 第 2 篇：MOS 管的导通与关断 |
| 4. [从反相器到锁存器与触发器](latch-and-divider/README.md) | 电路如何保存一个比特、按时钟边沿采样并实现分频？ | 第 3 篇：反相器与逻辑电平 |
| 5. [晶体管的小信号放大](transistor-amplifier/README.md) | 晶体管如何把输入电压的微小变化放大？ | 第 1–3 篇：器件电流与反相器 |
| 6. [石英振荡器的起振与稳幅](quartz-oscillator/README.md) | 石英的谐振如何与放大电路结合，产生稳定的时钟？ | 第 5 篇：信号放大 |
| 7. [PLL 怎样实现二倍频](integer-pll/README.md) | 锁相环如何通过相位比较和反馈控制改变时钟频率？ | 第 4、6 篇：分频与时钟来源 |
| 8. [门延迟、翻转能量与芯片功耗](fanout-and-wire-delay/README.md) | 负载与连线为何影响翻转速度，一次翻转为何消耗能量？ | 第 3 篇：逻辑门与电容充放电 |
| 9. [本地供电、翻转能量与时钟频率](supply-voltage-and-frequency/README.md) | 供电压降、去耦和工作电压如何影响能量与延迟？ | 第 8 篇：门延迟与翻转能量 |
| 10. [建立与保持：数据为何太晚或太早](pvt-and-path-delay/README.md) | 数据为什么可能错过采样窗口，工艺、电压与温度如何改变时序？ | 第 4、8、9 篇：边沿采样与路径延迟 |

## 按学习目标选择

- **从零理解数字电路（1 → 2 → 3 → 4）**：从电子运动开始，理解晶体管、逻辑门和比特存储。这条路线也为后续学习运算单元和 SRAM 提供基础。
- **理解时钟从哪里来（5 → 6 → 7）**：沿小信号放大、石英振荡到锁相环阅读；如果还不熟悉反相器或分频，先补第 3、4 篇。
- **理解芯片的频率与功耗（8 → 9 → 10）**：如果已经了解逻辑门与触发器，可以直接进入这条路线，理解电路中的充放电、供电和采样约束。

## 接着往哪读

想知道芯片怎样做乘法，可以从几个输入位画起，看逻辑门怎样生成部分积，部分积又怎样相加。见[从部分积到 MAC](../microarchitecture/01-datapath/multiply-accumulate-from-gates.md)。

想知道一个比特怎样在片上存储器里保存，可以从两个交叉耦合的反相器出发，进一步看存储单元怎样连接位线、怎样完成读写。见[6T SRAM 存储单元](../storage/02-sram/foundations/6t-cell-bistable-storage.md)。

想知道时钟能跑多快，可以跟着数据走过两个寄存器之间的一段逻辑，算一算它能否赶上下一个采样边沿。见[电路与时序基础](../microarchitecture/02-pipeline/electrical-timing-foundations.md#4-算一条路径需要多长的时钟周期)。

想从硅片继续追到封装，可以顺着[板卡到裸片的供电路径](supply-voltage-and-frequency/README.md#board-to-die)往里走。再换一根信号线，看[GPU 与 HBM 之间的横向连线，以及 HBM 堆栈里的垂直连接](../chip-development/FAB/wiki/04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture.md#hbm-section)。
