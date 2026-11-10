# PI、PDN、Decap:供电完整性

上级:[跨工艺共性问题](README.md)
相关:[后道封装](../04-back-end-packaging/README.md), [HBM 代际演化](../04-back-end-packaging/hbm-as-case-study/hbm-evolution-hbm2-hbm3-hbm4.md), [封装内的信号完整性](signal-integrity-in-package.md)

## 这页在回答什么问题

PDN、PI、decap 分别是什么，为什么高性能先进封装不是只做信号连接，也是在重做从板级到 die 内的供电网络。

## 三个概念

| 概念 | 含义 |
| --- | --- |
| PDN | Power Delivery Network，把电从外部送到负载的完整路径 |
| PI | Power Integrity，动态负载下电压是否稳定 |
| Decap | Decoupling capacitor，高频瞬态电流的局部缓冲 |

PDN 是路径，PI 是结果，decap 是改善高频响应的重要手段。

## PDN 是跨层系统

先进封装中的 PDN 不止在 die 内。它跨过 board、package substrate、interposer/RDL、bump、TSV 和 die 内金属。

```text
voltage regulator
  -> board
  -> package substrate
  -> interposer / RDL
  -> bump / TSV
  -> die power grid
  -> switching load
```

任何一层的阻抗、回流路径、电流拥挤和 decap 布局都会影响最终 PI。

## 为什么高性能封装 PI 更难

AI/HPC 和 HBM 系统具备高功耗、高并发、宽接口和强动态负载。多个 chiplet 或 HBM stack 同时工作时，电流变化不再是单 die 问题，而是 package 级系统问题。

| 压力来源 | PI 风险 |
| --- | --- |
| 高功耗 logic | IR drop、热点、电迁移 |
| 宽 HBM/D2D 接口 | switching noise、return path 压力 |
| 多 chiplet | 供电区域耦合 |
| 2.5D/3D 层级 | bump/TSV/interposer 寄生 |
| 动态 workload | voltage droop、ground bounce |

## Decap 为什么位置关键

同样容量的 decap，离负载越近、回路越短，高频效果越好。先进封装会把 decap 分散在 die 内、interposer、package 或 substrate 上，目标是缩短瞬态电流路径。

```text
long supply path
  -> local decap near load
  -> reduced high-frequency loop
```

Interposer 或 package 不再只是连线层，也可能成为局部去耦和供电分配平台。

## 电源跌落手算：储能与路径寄生

假设负载电流突然增加 `0.1 A`，持续 `1 ns`，这段时间内上游没有提供额外电流，理想本地 `10 nF` 电容提供全部增量。由 `ΔV = ΔI × Δt / C`，电容电压下降 `10 mV`。若有效电容只有 `5 nF`，同一假设下跌落变为 `20 mV`。实际有效电容会随偏压、频率、温度及布局变化。

再假设路径串联电阻 `10 mΩ`，增量电流的静态 `IR` 压降为 `1 mV`。若电流在 `100 ps` 内线性上升，路径电感 `100 pH` 对应瞬时 `L·di/dt = 0.1 V`；此值说明快速边沿对电感敏感，并不意味着完整 PDN 一定产生 100 mV 跌落。这里的三个计算分别隔离电容、电阻和电感作用，不能在不定义具体电路和时间响应时直接相加。真实 PDN 需要频率相关阻抗、负载波形和仿真或测量。

对时序模型，可把测得的局部电压波形映射到对应库的延迟或工作点；不能假设每次跌落都导致固定周期惩罚。若缺少校准，扫描电压和延迟范围并标为假设。

## PI 和 SI 的耦合

供电噪声会变成时序 jitter、接口误码或功能不稳定；信号回流路径也依赖电源/地结构。高速信号和供电网络不能分开优化。一个封装看似 routing 足够，若 return path 和 PDN 阻抗不稳定，接口仍可能失败。

## 一句话理解

PDN 是供电路径，PI 是这条路径在动态负载下稳不稳，decap 是缩短高频瞬态电流回路的局部储能结构。

## 架构师启示

架构师定义功耗、HBM 带宽和 chiplet 通信时，也在定义 PDN 难度。若 power profile、NoC burst、HBM 访问和 D2D activity 没有进入封装 PI 评估，最终性能可能被 voltage droop 和热电耦合限制。
