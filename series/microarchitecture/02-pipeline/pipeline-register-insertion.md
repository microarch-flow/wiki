# Pipeline register 插入：路径、延迟与吞吐的权衡

上级：[04 · 时钟与流水](./README.md)
相关：[时钟同步](./global-clock-synchronization.md)、[反馈环](./feedback-loop-clock-constraint.md)、[频率与吞吐](./frequency-is-not-throughput.md)

## 一次前馈切分

前馈逻辑的输入经过组合路径后写入寄存器。插入中间寄存器后，输入在两个采样窗口中依次通过两段逻辑：

```text
输入 → [逻辑 A] → reg → [逻辑 B] → reg → 输出
```

假设切分前完整 setup 要求为 2 ns。切分后两个新路径的完整要求分别为 1.2 ns 和 1.3 ns，且该域无其他更慢路径，则周期下界从 2 ns 变为 1.3 ns，频率上限从 500 MHz 变为约 769 MHz。两个数字包括示例中的寄存器、布线和时钟修正。这是手算假设，不是产品时序。若输入依赖、资源和接口允许每拍启动一笔，II 可以保持 1 拍，而通过该块的延迟从一拍增加为两拍。延迟的 ns 值未必增加，也未必减少；取决于新周期和路径。

## 前提与代价

插入寄存器后，功能和协议要能容忍新延迟。有效位、异常、反压、分支和多路输入必须与数据对齐；反馈依赖另见[反馈环](./feedback-loop-clock-constraint.md)。每个寄存器位都消耗面积、时钟功耗、布线和时序预算。频繁切分还可能导致 hold 修复、拥塞和时钟树成本。时序收益取决于切分平衡、寄存器开销和剩余的其他路径，不能假定频率翻倍或无限提升。

## 建模启示

```text
Pipeline { stages, latency_cycles, initiation_interval_cycles,
           stage_setup_requirements, area, power, clock_domain }
T_domain >= max(all_valid_setup_requirements_in_domain)
```

对只关心事务行为的模型，可以折叠内部级数，但仍应保留真实的 latency、II、反压与频率。对频率估计，必须用所有路径的完整 setup 要求，并独立检查 hold 和时钟域。模型中 `II=1` 是已知能力或假设，不是寄存器数量自动推出的结论。
