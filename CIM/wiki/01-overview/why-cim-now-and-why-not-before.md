# 为什么 CIM 在 1990s 失败、在 2010s 重生

上级：[01 Overview](./README.md)
相关：[Memory Wall 与 Von Neumann Bottleneck](./problem-statement.md), [两条正交主线](./two-axes-memory-and-paradigm.md)

## 这页在回答什么问题

存内/近存计算并不是 2010s 才出现的新想法，为什么早期没有成为主流，而 AI 时代又重新点燃？这个问题不能用“以前工艺不够好，现在工艺好了”解释，真正变化的是 workload、数值精度、memory hierarchy、EDA/验证能力和商业场景。

## 早期为什么难以成为主流

1990s 到 2000s 的 processing-in-memory、logic-in-memory、active memory 研究已经看到了 processor-memory gap。但当时主流 workload 更依赖通用控制流、cache hierarchy 和标量/向量程序性能，靠近 memory 放 compute 很容易遇到三个问题。

第一，workload 不够规整。CIM/PIM 最喜欢的是可批量映射、数据复用清晰、控制流简单的矩阵/向量类计算。传统通用程序的大量分支、指针追踪、系统调用和复杂 cache 行为，让 memory-side compute 很难形成稳定软件接口。

第二，数值和软件生态不配合。早期主流计算更强调高精度和通用 ISA 兼容，而 CIM 尤其 analog/mixed-signal CIM 天然更适合低比特、固定模式、容错推理。没有低精度神经网络、QAT、noise-aware training 和 graph compiler，硬件即使能做局部计算，也很难被完整模型使用。

第三，工艺和验证收益不闭环。把逻辑放进 memory process 会牺牲逻辑密度和频率，把 memory 做进 logic process 又牺牲容量和成本。早期系统没有足够强的 AI memory-bound 需求来支付这种工艺、验证、测试和软件代价。

## 2010s 后发生了什么变化

AI workload 给 CIM/PIM/NMC 提供了更匹配的目标。CNN、DNN、Transformer 中大量核心子图可以降到 MVM/GEMM、dot product、bitwise operation 和 reduction。即使不是整网都适合，某些子图也足够大、足够规整，值得专门优化。

低精度推理改变了 analog/digital trade-off。INT8、INT4、binary/ternary network、quantization-aware training 和后来的 mixed precision 让“硬件数值不完美但模型可补偿”成为现实。Analog CIM 仍然有精度和校准问题，但模型层开始能吸收一部分硬件噪声。

Memory hierarchy 的压力更尖锐。HBM 提供高带宽，但成本、封装和能耗都高；片上 SRAM 很快、但面积贵、容量有限；LLM decode 和 long context 进一步把 KV cache 与权重访问推到系统瓶颈位置。于是“把 compute 靠近 data”从学术想法变成可被客户感知的能耗、延迟和 BOM 问题。

EDA、硅后测量和硬件软件协同能力也更成熟。现代 SoC 设计已经习惯用复杂 memory hierarchy、NoC、DMA、runtime 和 compiler 管理异构执行单元。CIM/PIM 仍然难，但比早期更容易嵌入一个异构 AI system。

## 为什么重生不等于成熟

重新点燃不代表路线已经定型。SRAM-CIM 更接近 CMOS 产品化，但容量和面积限制明显；ReRAM/Flash analog CIM 理论吸引力强，但 device variation、write/verify、retention、ADC/DAC 和校准仍是量产门槛；DRAM/HBM-PIM 更 system-oriented，但需要 memory vendor、controller、host runtime 和 workload 共同配合。

更重要的是，AI workload 也在变化。CNN 让早期 CIM 容易展示，Transformer/LLM 又把问题从固定卷积映射推向 attention、KV cache、decode latency、MoE routing 和软件栈。CIM 的机会不是线性扩大，而是在不同 workload 阶段不断迁移。

## 一条历史判断线

```text
早期 PIM/CIM:
  通用程序 + 高精度 + 软件接口弱 + 工艺收益不闭环

AI 时代 CIM/PIM/NMC:
  规整矩阵子图 + 低精度容忍 + memory-bound 场景 + 异构软件栈
```

这条线解释了为什么今天可以重新研究 CIM，也解释了为什么不能把 CIM 当成已经战胜传统架构的终局路线。

## 常见误解

常见误解：CIM 过去失败只是因为工艺不成熟。实际上，workload、数值精度、软件生态和商业场景同样不成熟。

常见误解：AI 时代 CIM 一定会成为主流。实际上，AI 只是提供了更合适的局部场景，系统收益仍然要逐层证明。

常见误解：ReRAM/analog CIM 的论文进展意味着量产临近。实际上，论文能证明机制成立，产品还要证明一致性、校准、测试、寿命、软件和客户价值。

## 一句话理解

CIM 在 AI 时代重生，是因为 workload 和低精度软件栈终于开始匹配靠近 memory 的计算；它没有在历史上失败一次后突然变简单，难点只是从“能不能算”转移到了“能不能稳定、可编程、可量产地带来系统收益”。
