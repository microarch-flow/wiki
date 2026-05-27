# 可靠性与误差容忍：Analog 路线的核心系统问题

上级：[05 Architecture And System](./README.md)
相关：[Non-Idealities and Error Sources](../04-circuit-and-macro/non-idealities-and-error-sources.md), [FAB: 3DIC Thermal Stress](../../../FAB/wiki/04-back-end-packaging/3d-routes/3dic-thermal-and-stress-challenges.md), [RAM: Refresh Cost](../../../RAM/wiki/04-dram-foundations/refresh-the-fundamental-cost.md), [BUS: MMIO Cache Interrupt](../../../BUS/wiki/04-microarchitecture-integration/mmio-cache-interrupt-view.md)

## 这页在回答什么问题

误差容忍为什么是系统问题，而不是电路局部问题？因为 device variation、ADC quantization、temperature drift、mapping mismatch 和 model sensitivity 会共同决定端到端 accuracy、校准频率和运行时降级策略。

## 误差传播链

```text
device / cell state
  -> array output distribution
  -> ADC / SA quantization
  -> tile-level partial sum
  -> model layer output
  -> end-to-end accuracy
```

每一层都可能把误差放大或吸收。只报告 macro output error，不报告模型 accuracy 和 corner 条件，不能判断系统可靠性。

## 三条 Paradigm 的可靠性差异

Analog CIM 的误差是数值路径的一部分。ReRAM/Flash/PCM 的 drift、write variation、retention 和温度变化会改变权重；SRAM charge-domain 路线受 PVT、leakage 和 sense margin 影响。系统必须有 calibration、redundancy、QAT/noise-aware training 或运行时 guardband。

Digital CIM 的可靠性更接近传统 SoC：timing closure、read disturb、soft error、faulty bit、BIST/ECC 和 DFT。它不是无误差，但错误更容易离散化和 corner 化。

Mixed-signal CIM 同时面对两类问题。analog 段引入分布误差，digital 段试图校正；若误差随温度、老化或 workload 改变，静态校正参数会失效。

## 系统策略

校准可以离线、启动时或在线执行。离线校准成本低但覆盖范围窄；在线校准更稳但消耗带宽、时间和能量。redundancy 可以屏蔽坏列、坏 cell 或漂移严重的 block，但会降低密度。

模型适配可通过 QAT、noise-aware training、outlier handling 和 layer-wise precision 分配吸收一部分误差。它的边界是误差必须可建模、稳定且能被训练数据覆盖。

热和封装也会影响可靠性。3D integration、HBM-adjacent design 或高密度 macro 会带来 thermal gradient，应连接 FAB wiki 的热/应力建模，而不能只看常温 silicon demo。

## PIM/NMC 对照

DRAM/HBM/GDDR-PIM 的可靠性重点在 DRAM timing、refresh、bank scheduling、ECC、thermal 和 host coordination，不是 CIM analog error budget。RAM wiki 的 [refresh cost](../../../RAM/wiki/04-dram-foundations/refresh-the-fundamental-cost.md) 和 DRAM timing 背景更适合分析这类问题；host coordination 则会进入 BUS/MMIO/runtime interface。NMC 更依赖 package/die-to-die link、software isolation 和 system-level fault handling。

## 一句话理解

CIM 可靠性是 device、电路、mapping、模型和运行时共同闭合的误差预算；analog/mixed-signal 路线尤其不能只靠单点 accuracy demo。

## 建模启示

建模应保留 error distribution、calibration interval、temperature corner、aging/drift、redundancy、accuracy loss 和 fallback policy。Resource 包括健康状态不同的 macro/tile，Topology 包括 calibration path 和 thermal coupling，Interaction 包括在线校准、降级和重映射，Capability 包括可用 precision、redundancy 和 fallback capability。早期探索可把复杂 device physics 折叠成 error model，但必须让 error 影响 latency、energy、capacity 和 model accuracy，而不是只作为注释存在。
