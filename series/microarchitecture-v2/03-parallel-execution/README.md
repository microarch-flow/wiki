# 并行执行与 GPU

并行执行将多项运算安排到多个硬件执行资源。SIMD、向量和 SIMT 等机制让硬件可以组织具有独立性的工作，而交错安排不同的执行上下文还可以减少资源空闲的时间。

十个加法互不依赖，如果芯片有四条执行通道，至少需要几个执行批次才能完成？当一组线程需要等待数据，而另一组仍有工作可做时，硬件又怎样安排它们使用运算单元？

本路线先解释一条指令或一组线程怎样使用多条物理执行通道，再观察调度器怎样处理等待和分支，最后比较线程驻留数量、存储资源与实际吞吐，理解为什么增加 GPU 线程并不必然加速计算。

## 知识关系

<figure class="micro-v2-map" markdown="1">

[![共同基础的数据通路、流水线和独立运算 → C01 标量、SIMD 与向量；C01 → C02 SIMT 与调度；指令、上下文、就绪与发射 → C02 SIMT 与调度；C02 → C03 驻留与资源](assets/knowledge-map.svg)](assets/knowledge-map.svg)

<figcaption>知识衔接示意。点击可查看大图。</figcaption>
</figure>

## 计划阅读顺序

本专题沿用同一组十个独立加法：先由一个和四个物理通道执行，随后把各个元素的工作组织为线程，最后观察计算、线程状态与访存资源的相互限制。正文尚未发布的条目不提供文章链接。

| 编号 | 文章 | 阅读重点 | 状态 |
| --- | --- | --- | --- |
| C01 | [十个独立的加法，怎样交给四条执行通道？](c01-scalar-simd-and-vector-execution.md) | 标量、SIMD、向量、物理 lane、分批、掩码与尾部；区分指令宽度与物理吞吐 | 已发布 |
| C02 | [一组线程还在等待数据，另一组线程能否先执行？](c02-simt-and-warp-scheduling.md) | SIMT、warp/wavefront、线程上下文、分支发散、谓词执行、硬件发射、延迟隐藏、组内交换与同步 | 已发布 |
| C03 | 为什么 GPU 中的线程越多，计算不一定越快？ | 线程块驻留、寄存器容量、occupancy、执行端口、访存合并、bank conflict | 未发布 |

## 与其他路线的关系

- [共同计算基础](../01-foundations/README.md)：理解运算单元、寄存器、流水线、依赖与发射。
- [指令执行与 CPU](../02-cpu/README.md)：从 [B01 的指令接口](../02-cpu/b01-instructions-and-architectural-state.md)、[B03 的发射](../02-cpu/b03-dynamic-issue-and-out-of-order-execution.md) 及 [B08 的硬件多线程](../02-cpu/b08-hardware-multithreading-and-resource-sharing.md) 衔接。无需先掌握完整 CPU 乱序执行。
- [计算阵列与数据流](../04-compute-arrays/README.md)：换一种并行组织，追踪多个乘加单元之间的数据传递。
- [专用计算与稀疏计算](../07-specialized-compute/README.md)：继续了解逐元素运算、归约以及不规则数据的处理。

- [存储系统](../../storage/README.md)：理解寄存器文件、bank、访问粒度与存储带宽；本专题仅观察它们怎样约束执行。
- [芯片与系统互连](../../interconnect/README.md)：请求传输和跨设备互连的具体机制由该系列负责。
- [芯片架构实例](../../chip-architectures/README.md)：考察具体 GPU 产品的组织与参数；本专题先建立通用机制。

[返回计算微架构系列](../README.md)
