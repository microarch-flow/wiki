# 案例：TSMC 16nm CIM Macro

上级：[09 研究前沿](README.md)
相关：[SRAM-CIM 深入](../02-memory-technologies/sram-cim-deep-dive.md), [Macro 设计框架](../04-circuit-and-macro/macro-design-tradeoff-framework.md), [指标术语表](metrics-glossary.md)

## 这页在回答什么问题

这页回答：如何阅读一个先进工艺下的 CIM macro 论文，以及为什么它是研究案例而不是产业产品案例。

基本信息：

| 字段 | 内容 |
| --- | --- |
| 论文 | A 16nm 216kb, 188.4TOPS/W and 133.5TFLOPS/W Microscaling Multi-Mode Gain-Cell CIM Macro for Edge-AI Devices |
| 会议/年份 | ISSCC 2025 |
| 机构 | TSMC Corporate Research、National Tsing Hua University、ITRI 等 |
| 技术路线 | 16nm gain-cell CIM macro，支持 MX/INT/FP multi-mode |
| 层级 | macro-level fabricated silicon，不是完整 chip/system |
| 来源 | [TSMC Research AI page](https://research.tsmc.com/page/artificial-intelligence/1.html), [DOI/abstract record](https://colab.ws/articles/10.1109%2Fisscc49661.2025.10904606) |

这个案例的研究价值不是“TSMC 在卖 CIM 产品”，而是它展示了 foundry research 如何把先进工艺、gain-cell macro、microscaling data format 和多模式 MAC 放进同一篇电路论文。TSMC 页面给出的口径是 16nm、216kb、188.4 TOPS/W、133.5 TFLOPS/W；摘要记录进一步说明它面向 MX-INT-FP multi-mode CIM，尝试把 FP-to-MX conversion、shared-scale processing、adder tree energy 和 accumulation-aware dataflow 放进 macro 内部处理。

它回答的研究问题是：CIM macro 能否不只服务固定 INT8 CNN，而是支持更复杂的低比特/浮点混合格式。传统 CIM macro 如果只支持单一 INT mode，面对 Transformer/edge AI 中不同 layer 的动态范围会很硬；M2-CIM 这类 multi-mode 设计把格式转换和 shared-scale 处理下沉到 macro 内，减少 system-to-CIM 数据往返。

它不能回答的问题同样重要。216kb macro 不能说明整颗 chip 的 global buffer、NoC、host interface、external DRAM access、compiler/runtime 都已解决；188.4 TOPS/W 或 133.5 TFLOPS/W 也不能直接外推成系统能效。读这类论文必须问：是否包含 ADC/SA、adder tree、format conversion、local buffer、data write path；是否是 peak macro metric；测试 workload 是 synthetic MAC 还是完整模型。

对本 wiki 的 taxonomy，它属于 CIM macro research：计算发生在 memory macro/array 近侧，且不是 Samsung HBM-PIM 这类 memory-die PIM。它更接近 SRAM/gain-cell digital/mixed-signal CIM 路线，而不是 ReRAM analog crossbar 路线。

## 一句话理解

TSMC 16nm case 的价值是展示先进 CMOS CIM macro 如何处理 mixed precision 和数据格式转换，不是证明 CIM 已经系统级量产。

## 研究启示

先进工艺 CIM 研究正在从“单一低比特高能效”转向“格式、数据流、局部处理和系统接口的共同优化”。对架构研究者来说，这类 macro 最有价值的不是峰值 TOPS/W，而是它暴露出哪些开销必须下沉到 macro 内，哪些仍会留给 tile/chip/system。
