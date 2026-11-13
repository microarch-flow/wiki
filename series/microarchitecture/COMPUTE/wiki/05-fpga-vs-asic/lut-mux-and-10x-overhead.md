# FPGA vs ASIC：可配置性、LUT 与实现开销

上级：[05 · FPGA vs ASIC](./README.md)
相关：[mux 与数据搬运成本](../02-datapath-foundations/mux-and-data-movement-cost.md)、[cache vs scratchpad](../../../../storage/01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md)

## 选择的输入和代价

FPGA 用配置位选择逻辑函数和互连，可在部署后重新配置；ASIC 通常为特定功能制造电路。比较需要指定同一工作量、精度、时序目标、利用率、工艺和实现范围。还要分别比较面积、时延、功耗、单次任务能量、开发费用和产量。一个面积比不能直接推导成功耗比或能量比。

本专题部分直觉来自 Dwarkesh Patel 对 Reiner Pope 的访谈《Chip design from the bottom up》。访谈中的成本或数量级只能作为特定语境的示意，不能作为当前报价或所有 FPGA 的固定系数。项目决策还需产品价格、开发验证成本、量产规模、功耗和生命周期更新需求。

## LUT4 与可配置互连

一个 4 输入 LUT 可用 16 位配置的真值表表达任意四输入布尔函数，再按输入选择一位作为输出。可配置互连通过开关或 mux 选择连接。实际 FPGA 还有寄存器、存储器、DSP 和时钟等硬块；逻辑与布线映射依赖器件和工具。

```text
输入 a,b,c,d → LUT4 选择 → 真值表中的一个输出位
例：a∧b∧c∧d → 真值表只有输入 1111 的输出为 1
```

同一 AND 函数也可用三个二输入 AND 门表达。真值表与门级表达展示通用性与专用性的结构差异，但其抽象元件个数不是等效面积、功耗或整芯片性能测量。真实 LUT 电路也不必按某种 AND/OR 网络实现。

## 量化研究的适用范围

[Kuon 和 Rose，2007 年的 90 nm 对照研究](https://www.eecg.utoronto.ca/~jayar/pubs/kuon/kuontcad06.pdf)比较了 FPGA 与标准单元 ASIC 的若干 benchmark。论文报告：仅 LUT/触发器逻辑的平均面积比约 35；使用存储器和乘法等硬块时，所测 benchmark 的平均面积差缩小至约 18；关键路径延迟比约 3–4，动态功耗比约 14，硬块可降低功耗差。论文还估计大量使用硬块可能进一步缩小面积差。这些是研究方法、器件和负载限定下的结果，不是现代器件的通用倍数，也不是单次任务能耗比。

## 建模启示

```text
Implementation { target, device_or_library, tool_flow, workload, precision,
                 frequency, LUTs, registers, DSPs, memories, routing,
                 area, timing, dynamic_power, static_power }
```

先为目标负载分别进行映射和综合，再记录硬块利用、布线、关键路径、活动率和执行周期。动态功率、静态功率与运行时间一起决定任务能量。早期探索可用来源明确的分项假设，但面积、时延和功率应分别校准，不应把 LUT4 的示意门数比当成统一乘数。固定费用与单位成本应使用项目实际报价；可用 `total_cost = NRE + volume × unit_cost` 做敏感性分析。
