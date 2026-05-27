# 05 Architecture And System

上级：[CIM Wiki](../README.md)
相关：[04 Circuit And Macro](../04-circuit-and-macro/README.md), [NoC: Memory-Centric NoC](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md), [RAM: HBM Wide I/O](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md), [BUS: AXI DMA Interface](../../../BUS/wiki/04-microarchitecture-integration/axi-dma-system-interface.md), [FAB: 3DIC](../../../FAB/wiki/04-back-end-packaging/3d-routes/3dic-fundamentals.md)

## 这页在回答什么问题

为什么一个很强的 CIM macro 不等于一个很强的 CIM system？因为 macro 之外会新增 tile buffer、local reduction、NoC、global memory、host interface、runtime 和 workload mapping，局部收益会在这些层级中衰减或转移。

## 本章的系统层级

```text
macro
  -> tile
  -> chip
  -> board / package
  -> host / runtime / workload
```

第 05 章不再讨论 cell 物理是否成立，而是讨论 macro 如何组成系统、系统收益如何保存、哪些成本会重新出现。CIM 仍指 cell 或 array path 参与计算；DRAM/HBM/GDDR-PIM 是 memory die/bank 内独立 compute unit 的系统路线；HBM base die、interposer 或 package-side compute 属于 NMC 边界。

## 本章页面地图

| 页面 | 核心问题 | 系统风险 |
| --- | --- | --- |
| [From Macro to System](./from-macro-to-system.md) | macro 指标怎样升到 tile/chip/system | buffer、NoC、host 吞掉收益 |
| [Dataflow Mapping](./dataflow-mapping-on-cim.md) | GEMM/Conv/Attention 如何映射到 CIM | utilization、tiling、fallback |
| [Interconnect and Reduction](./interconnect-and-reduction.md) | macro/tile 间如何通信和归约 | partial sum traffic 和拥塞 |
| [Memory Hierarchy](./memory-hierarchy-with-cim.md) | on-array、buffer、SRAM、HBM 如何分工 | 容量错配和 reload |
| [Performance Energy Modeling](./performance-energy-modeling.md) | 如何把 macro 指标推到系统指标 | 口径不统一和隐藏成本 |
| [Reliability and Error Tolerance](./reliability-and-error-tolerance.md) | analog/mixed-signal 误差如何进入系统 | calibration、retraining、降级 |
| [Host Integration](./cim-system-integration-with-host.md) | CIM 如何接入 SoC/PCIe/host | 同步、DMA、driver/runtime |

## 三条 Paradigm 到系统层的差异

Analog CIM 的系统问题是误差、校准和 ADC 后数据流。Digital CIM 的系统问题是 bit-serial 周期、accumulator、buffer 和 NoC 是否抵消局部收益。Mixed-signal CIM 的系统问题是 analog/digital 边界后的校正、partial sum 合并和软件可建模性。

## 一句话理解

第 05 章回答“macro 收益如何活到系统层”：不是看峰值 TOPS/W，而是看 mapping、memory hierarchy、interconnect、host 和 reliability 是否共同闭合。

## 建模启示

架构探索不需要一开始建模全部电路细节，但必须显式建模层级。可把 macro/tile/buffer/NoC/HBM/host 作为 Resource，把连接关系作为 Topology，把数据搬运、归约、校准和 fallback 作为 Interaction，把 bit-width、array size、ADC cost、error model 和 supported op 作为 Capability；无法早期确定的 device 细节可以折叠成 latency、energy、effective precision 和 error-rate 参数。
