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

## PI 和 SI 的耦合

供电噪声会变成时序 jitter、接口误码或功能不稳定；信号回流路径也依赖电源/地结构。高速信号和供电网络不能分开优化。一个封装看似 routing 足够，若 return path 和 PDN 阻抗不稳定，接口仍可能失败。

## 一句话理解

PDN 是供电路径，PI 是这条路径在动态负载下稳不稳，decap 是缩短高频瞬态电流回路的局部储能结构。

## 架构师启示

架构师定义功耗、HBM 带宽和 chiplet 通信时，也在定义 PDN 难度。若 power profile、NoC burst、HBM 访问和 D2D activity 没有进入封装 PI 评估，最终性能可能被 voltage droop 和热电耦合限制。
