# Groq 第一代 TSP 怎样在编译期安排数据和指令

Groq 第一代张量流处理器（TSP）把存储、矩阵、向量和数据重排单元布置成不同的功能切片。编译器安排指令发出时刻和操作数经过切片的方向。对一段已经映射的程序，它需要保证操作数与消费指令在同一地点、同一时刻就绪。本文限定为 ISCA 2020 论文公开的第一代芯片。 [Groq ISCA 2020 论文](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Groq_LPU/tsp-isca20.pdf)

## 片上数据怎样通过切片

MEM 切片使用片上 SRAM，MXM 切片执行矩阵运算，VXM 切片执行向量运算，SXM 切片进行数据重排。指令控制单元（ICU）向相应切片发出指令。数据经流寄存器沿东西方向移动，消费者按流编号和方向取数。

论文的 **superlane 是横跨功能切片的 16 lane**。一条切片在另一维包含 20 个 tile，因此指令可覆盖的最大向量宽度是 320 个元素。这两个数分别描述最小处理粒度和最大向量宽度。芯片上的 MEM 切片合计提供 220 MiB SRAM。 [原论文，第 II 至 III 节](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Groq_LPU/tsp-isca20.pdf)

## 一个编译期安排示例

假设权重已装入矩阵单元。要执行一次“矩阵乘后接激活”，编译器先选择兼容的切片、流编号和方向，再计算操作数经过路径的时间。

| 阶段 | 输入 | 输出和依赖 |
| --- | --- | --- |
| MEM 读入 | SRAM 地址、流编号和坐标 | 在约定时刻把输入送入流。 |
| MXM 计算 | 输入流和已装载的权重 | 在预定周期取数，将片段结果送入下一条流。 |
| VXM 激活 | 从 MXM 路径到达的结果流 | 执行逐元素运算，将结果继续传给能够接收它的切片。 |

用抽象周期表示。如果输入在周期 0 发出、在途耗时 3 个周期，消费者在周期 3 取数。假如换到一条耗时 5 个周期的路径，消费者也要改到周期 5，或者由编译器选择等效的对齐策略。还要检查之前的流占用、算子自身延迟和目标资源的可用时刻。数字是教学假设。原论文给出了利用指令间隔控制具体周期的例子。 [原论文，流与指令时序说明](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Groq_LPU/tsp-isca20.pdf)

## 容量和时延要分别算

假设 70 亿个权重各占 1 B，且全部常驻芯片 SRAM。单片按 220 MiB 公称容量计算，理想均匀分片至少需要 31 颗芯片。这个容量下界只计权重。可用 SRAM 还需容纳程序和其他缓冲，分片与量化布局也可能增加需求。

固定编译结果的设备执行时序可以分析。部署时还需要确定跨芯片传输、同步和实际请求的排队延迟，并分别测量。厂商在 ISCA 2022 另文讨论了多芯片互连和调度。读取那份系统资料时要记录拓扑及所用配置。 [Groq 多芯片原论文存档](https://raw.githubusercontent.com/microarch-flow/chip-architecture-wiki/3086204c049a762eb59033f8141fba9e91f4c669/Groq_LPU/SDTSM.pdf) · [推理时延和测量边界](../../inference-runtime/09-measurement-and-cases/README.md)

## 接下来怎么读

- 对照按阶段协调计算与交换的另一种分布式 SRAM 组织。 [Graphcore GC200](../Graphcore_IPU/README.md)
- 对照编译器如何把算子映射到可配置的流水级。 [SambaNova SN40L](../SambaNova/README.md)
