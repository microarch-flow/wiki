# 时钟同步：采样边沿与时序约束

上级：[04 · 时钟与流水](./README.md)
相关：[pipeline register 插入](./pipeline-register-insertion.md)、[反馈环](./feedback-loop-clock-constraint.md)、[频率与吞吐](./frequency-is-not-throughput.md)

## 时钟域与数据路径

同步电路用时钟沿定义寄存器何时采样。一个寄存器发出数据，经组合逻辑和布线到达下一个寄存器。两个时钟沿之间，组合电路仍在传播信号，不是整个芯片暂停。时钟树有偏斜和抖动；不同域可以有不同频率、相位和门控状态。跨域路径需要按具体时钟关系约束，并按 CDC 协议、同步器或异步 FIFO 处理。

```text
launch register -- t_cq --> logic + wire -- t_setup --> capture register
         launch clock edge                    capture clock edge
```

## Setup 上界与 hold 下界

对同域、同沿、单周期路径，设 `t_skew = capture_clock_arrival - launch_clock_arrival`，且 setup uncertainty 已单列。一个常用简化条件是：

```text
T >= t_cq_max + t_logic_wire_max + t_setup + t_uncertainty_setup - t_skew
```

最大延迟决定 setup 所需的周期下界。hold 则检查最短数据路径，简化为：

```text
t_cq_min + t_logic_wire_min >= t_hold + t_uncertainty_hold + t_skew
```

上式使用同一偏斜定义。真实 STA 还需按库、时钟路径、相关性和约束确定 setup/hold 的 launch/capture 边沿、时钟偏斜及 uncertainty，避免重复计入。多周期路径、不同相位及跨域关系不能直接套这两个简式。AMD 的 [UG906 setup 边沿关系](https://docs.amd.com/r/2024.1-English/ug906-vivado-design-analysis/Setup/Recovery-Relationship)说明了 launch/capture 边沿和 setup slack 的关系。

## PVT 与工程证据

每条路径都要在约定的工艺、电压、温度（PVT）、模式和约束角下检查。库、布线、时钟树、芯片老化和目标可靠性影响裕量。没有适用于所有设计的固定 25% 裕量，也不能从某个名义角通过推断所有器件永远满足时序。需要记录设计覆盖的条件、STA 报告与实际验证范围。

## 建模启示

每个时钟域分别记录所有有效前馈和反馈路径的 setup 周期要求，并取最大值。hold 是独立的最小延迟检查，不会由降低频率自动解决。输入、输出和跨域路径也需各自约束。

例如，假设同一域内反馈路径完整 setup 要求是 1.0 ns，前馈路径是 1.4 ns，二者已经含寄存器和时钟修正，则 `T >= max(1.0, 1.4)=1.4 ns`，频率上限约 714 MHz。该数值是假设，不是硅片实测。另一域若有独立时钟，需要单独分析。频率只是吞吐的一项，还需知道每个工作流的启动间隔（II）与延迟。
