# 早期 PIM 原型与 AI 时代的新机会

上级：[01 Overview](./README.md)
相关：[Memory Wall 与 Von Neumann Bottleneck](./problem-statement.md), [两条正交主线](./two-axes-memory-and-paradigm.md)

## 这页在回答什么问题

存内/近存计算并不是 2010s 才出现的新想法，为什么早期没有成为主流，而 AI 时代又重新点燃？这个问题不能用“以前工艺不够好，现在工艺好了”解释，真正变化的是 workload、数值精度、memory hierarchy、EDA/验证能力和商业场景。

## 早期为什么难以成为主流

1990s 到 2000s 已有 processing-in-memory、logic-in-memory 和 active memory 原型，但这些路线没有普遍成为主流商用系统；不能据此说原型都失败，也不能用后来 AI 技术的缺席解释所有历史案例。

例如 UC Berkeley 的 [VIRAM-1 及硬件/编译器协同设计](https://people.eecs.berkeley.edu/~yelick/papers/iram-proc-ieee01.pdf)面向音频、视频和图像等具有数据并行性的媒体程序。它把向量处理器与 embedded DRAM 集成，并设计向量 ISA 和配套编译器；这说明早期已有规整 workload 和软件工具，不能概括为只面对不规整通用程序或没有编译器。它是特定研究原型，不证明整类产品已经规模部署。

不同方案的采用还须分别评估：在目标工艺中整合逻辑与存储的面积、时序和制造成本，程序数据布局与可移植性，及与已有处理器和内存系统的端到端收益。公开原型本身不能证明这些因素各自造成了多少商业影响。低位量化、QAT 和模型容错则是后来的 AI 推理设计条件，不是 VIRAM 等早期媒体原型必须具备的前提。

## 2010s 后发生了什么变化

2010 年代 DNN/CNN 的发展为 CIM/PIM/NMC 提供了更匹配的目标，后来的 Transformer 进一步扩展了工作负载。大量核心子图可以降到 MVM/GEMM、dot product、bitwise operation 和 reduction。即使不是整网都适合，某些子图也足够大、足够规整，值得专门优化。

低精度推理改变了 analog/digital trade-off。INT8、INT4、binary/ternary network、quantization-aware training 和后来的 mixed precision 让“硬件数值不完美但模型可补偿”成为现实。Analog CIM 仍然有精度和校准问题，但模型层开始能吸收一部分硬件噪声。

Memory hierarchy 的压力更尖锐。HBM 提供高带宽，但成本、封装和能耗都高；片上 SRAM 很快、但面积贵、容量有限；LLM decode 和 long context 进一步把 KV cache 与权重访问推到系统瓶颈位置。于是“把 compute 靠近 data”从学术想法变成可被客户感知的能耗、延迟和 BOM 问题。

EDA、硅后测量和硬件软件协同能力也更成熟。现代 SoC 设计已经习惯用复杂 memory hierarchy、NoC、DMA、runtime 和 compiler 管理异构执行单元。CIM/PIM 仍然难，但比早期更容易嵌入一个异构 AI system。

## 为什么重生不等于成熟

重新点燃不代表路线已经定型。SRAM-CIM 更接近 CMOS 产品化，但容量和面积限制明显；ReRAM/Flash analog CIM 理论吸引力强，但 device variation、write/verify、retention、ADC/DAC 和校准仍是量产门槛；DRAM/HBM-PIM 更 system-oriented，但需要 memory vendor、controller、host runtime 和 workload 共同配合。

更重要的是，AI workload 也在变化。CNN 让早期 CIM 容易展示，Transformer/LLM 又把问题从固定卷积映射推向 attention、KV cache、decode latency、MoE routing 和软件栈。CIM 的机会不是线性扩大，而是在不同 workload 阶段不断迁移。

## 一条历史判断线

```text
早期示例 VIRAM-1:
  媒体向量程序 + embedded DRAM + 向量 ISA/编译器 + 原型验证

AI 时代 CIM/PIM/NMC:
  规整矩阵子图 + 低精度容忍 + memory-bound 场景 + 异构软件栈
```

这条线解释了为什么今天可以重新研究 CIM，也解释了为什么不能把 CIM 当成已经战胜传统架构的终局路线。

## 常见误解

常见误解：早期原型未规模采用只因工艺不成熟，或只因缺少 AI 量化工具。实际上须针对具体方案审查应用、工艺、编译器、集成成本及商业证据。

常见误解：AI 时代 CIM 一定会成为主流。实际上，AI 只是提供了更合适的局部场景，系统收益仍然要逐层证明。

常见误解：ReRAM/analog CIM 的论文进展意味着量产临近。实际上，论文能证明机制成立，产品还要证明一致性、校准、测试、寿命、软件和客户价值。

## 一句话理解

AI 时代的部分 workload 和低精度软件栈更匹配靠近 memory 的计算；已有原型和应用不意味着历史上的所有方案都失败，难点只是从“能不能算”转移到了“能不能稳定、可编程、可量产地带来系统收益”。
