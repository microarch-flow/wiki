# HBM:先进封装的标志性应用

上级:[后道封装](../README.md)
相关:[2.5D 路线](../2.5d-routes/README.md), [3D 路线](../3d-routes/README.md), [CoWoS-S 完整制造流程](../2.5d-routes/cowos-s-complete-process.md)

## 这页在回答什么问题

为什么 HBM 是理解先进封装的最佳案例之一。它把 memory stack、logic die、interposer/RDL、PI、热、KGD 和 final package 放进同一个系统问题里。

## HBM 为什么适合作为案例

HBM 本身是 3D memory stack，又必须和 logic die 通过近距高密度接口连接。它天然把两层问题叠在一起：

```text
inside HBM:
  DRAM die stack -> TSV / vertical interconnect

logic + HBM package:
  logic die <-> interposer/RDL/bridge <-> HBM stack
```

第一层是 memory 内部的 3D 堆叠，第二层是 logic 与 memory 的 2.5D 或更高层级系统集成。这使 HBM 成为连接前面 2.5D、3D、RDL、bump、substrate、热和测试章节的核心案例。

## 本目录阅读顺序

```text
hbm-as-case-study
  -> why-hbm-forces-2.5d-3d
  -> hbm-stack-manufacturing
  -> ai-gpu-hbm-package-architecture
  -> hbm-evolution-hbm2-hbm3-hbm4
```

先理解 HBM 为什么改变封装需求，再拆 HBM stack 自身如何形成，然后画出 AI GPU + HBM package 的对象关系，最后看 HBM 代际演化如何反过来推动封装路线升级。

## HBM 改变了哪些架构问题

HBM 不是“更快的外部 DRAM”。它把内存带宽问题从板级通道拉回 package 内部，让逻辑 die 通过极宽、短距、低能耗接口访问 memory stack。

| 架构问题 | HBM 带来的变化 |
| --- | --- |
| Memory bandwidth | 从拉高单线速率转向更宽并行接口 |
| Power-per-bit | 依赖更短互连和更低寄生 |
| NoC / memory controller | 需要在片上组织更高并发的访存入口 |
| Package layout | HBM stack 数量和位置成为 floorplan 约束 |
| Thermal design | 高功耗 logic 与 HBM 邻近导致热耦合 |
| Test/yield | HBM stack 和 logic 都是高价值 KGD |

这里的 RAM/内存层级问题不再只在芯片架构图里解决，NoC 与 memory controller 的带宽需求会落到 package 中的物理互连密度、供电和热路径上。

## 一句话理解

HBM 把存储带宽问题变成先进封装问题：memory 自己要 3D 堆叠，memory 与 logic 又需要 2.5D/3D 级近距高密度集成。

## 架构师启示

架构师定义 HBM 系统时，必须同时定义 memory controller/NoC 带宽、HBM stack 数量、package 布局、interposer/RDL 能力、KGD 策略和热设计。只在逻辑架构层写“接入 HBM”是不够的，因为 HBM 的价值只有在封装互连、供电和热路径闭合后才能释放。
