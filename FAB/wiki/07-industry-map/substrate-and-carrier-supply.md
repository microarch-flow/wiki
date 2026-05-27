# 基板与载板供应

上级:[产业地图](README.md)
相关:[基板与载板](../04-back-end-packaging/key-components/substrate-and-carrier.md), [材料供应链](materials-supply-chain.md), [大陆先进封装瓶颈](mainland-china-bottlenecks.md)

## 这页在回答什么问题

为什么 substrate 和 carrier 是先进封装供应链的核心环节，ABF substrate、大尺寸基板和临时载体分别卡住什么能力。

## Substrate 的产业位置

Package substrate 连接上层 interposer/RDL/module 和下层 board。高端 AI/HPC package 需要大尺寸、高层数、高 I/O、大电流和较好 warpage 控制的 substrate。

```text
logic + HBM module
  -> package substrate
  -> board / system
```

当上层 CoWoS-like、Fan-out 或 bridge 平台变强时，substrate 会成为系统能否落地的承载层。

## ABF substrate

ABF build-up substrate 是高性能处理器封装中的关键基板类型。ABF 作为绝缘 build-up film，支持多层微细线路，把芯片端高密度连接过渡到系统板级尺度。

| 需求 | 对 substrate 的压力 |
| --- | --- |
| 更多 HBM stack | package 尺寸和 I/O 数增加 |
| 高功耗 logic | 电流承载和 PDN 更难 |
| 高速接口 | 损耗、阻抗、回流路径更重要 |
| 大尺寸 package | warpage 和平整度更难 |
| 多 die 组装 | assembly 窗口和良率风险上升 |

## Carrier 的作用

Carrier 多用于制造过程中的临时支撑。Fan-out、RDL-first、thin wafer、temporary bonding/debond 等流程需要 carrier 提供平整加工基准。Carrier 不一定进入最终产品，但会影响 RDL overlay、die shift、thin die handling 和 debond 良率。

## 供应链为什么紧

高端 substrate 不是简单 PCB。它需要材料、层压、激光加工、微孔、铜镀、翘曲控制、测试和大尺寸良率共同成立。AI/HPC package 放大后，substrate 的面积、层数、平整度和交付节奏都会成为瓶颈。

## 一句话理解

Substrate 是高密度封装接入板级系统的最终承载平台，carrier 是先进封装制造中保证平整度和薄片处理的临时平台；两者都能限制高端 package 量产。

## 架构师启示

架构师定义 HBM 数量、package 尺寸和功耗时，应同步确认 substrate 层数、电流承载、SI/PI 和 warpage 能否闭合。基板能力不足会迫使架构减少 HBM、改变 die placement 或切换封装路线。
