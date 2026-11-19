# AMD Versal VC1902 的可编程逻辑怎样给 AI Engine 供数？

在 AMD Versal AI Core VC1902 上，可编程逻辑（PL）可以把 DDR 中的数组转换成数据流，再交给 AI Engine（AIE）计算。AIE 返回结果流，PL 把结果写回 DDR。本文跟踪 VCK190 板上的一个官方算例。输入是一个 4 × 4 整数矩阵和一个 4 × 1 列向量，输出是四个整数。 [VCK190 板卡手册](https://docs.amd.com/r/en-US/ug1366-vck190-eval-bd/Versal-Adaptive-SoC) · [Vitis 2026.1 教程](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_EDF/VCK190/README.md)

## 两条输入流从哪里来

VC1902 把处理器系统（PS）、PL 和 AIE 阵列集成在同一器件。PS 上的主机程序通过 XRT 配置缓冲并启动硬件。高层综合（HLS）把搬运内核编译成 PL 中的电路。AIE 编译器把图中的 `MatMul` 内核映射到器件已有的 AIE tile。每个 tile 提供标量和向量运算、数据存储和流交换资源。 [AIE 架构手册](https://docs.amd.com/r/en-US/ug1079-ai-engine-kernel-coding/AI-Engine-Architecture-Overview) · [AIE 图源码](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/AIE_Kernel/aie_srcs/graph.h)

同一份 `mm2s` 源码在 PL 中生成两个实例。一个读取矩阵 A，另一个读取向量 B。内核从内存读取 32 位字，并通过 AXI4-Stream 逐字送出。链接配置把两个实例接到 AIE 图的 `DataIn1` 和 `DataIn2`，再把 `DataOut1` 接到 `s2mm` 的输入。EDF 教程的 Makefile 从同一版本的 PetaLinux 示例目录取用这些源码。 [构建入口](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_EDF/VCK190/Makefile) · [链接配置](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/vitis_dir/system.cfg) · [输入搬运源码](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/HLS_Kernels/mm2s.cpp)

<figure class="chip-lifecycle-flow" aria-label="两组输入从 DDR 经两个 PL 读内核进入 AIE。输出经过 PL 写内核返回 DDR。">
  <div class="chip-flow-pair">
    <div class="chip-flow-step"><strong>DDR 中的矩阵 A</strong><small>16 个 32 位整数</small></div>
    <div class="chip-flow-step"><strong>DDR 中的向量 B</strong><small>4 个 32 位整数</small></div>
  </div>
  <div class="chip-flow-pair" aria-hidden="true"><span class="chip-flow-arrow">↓</span><span class="chip-flow-arrow">↓</span></div>
  <div class="chip-flow-pair">
    <div class="chip-flow-step"><strong>PL · mm2s_1</strong><small>送到 DataIn1</small></div>
    <div class="chip-flow-step"><strong>PL · mm2s_2</strong><small>送到 DataIn2</small></div>
  </div>
  <div class="chip-flow-pair" aria-hidden="true"><span class="chip-flow-arrow">↓</span><span class="chip-flow-arrow">↓</span></div>
  <div class="chip-flow-step"><strong>AI Engine · MatMul</strong><small>从两块输入缓冲读取，计算四个结果</small></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓ DataOut1</div>
  <div class="chip-flow-step"><strong>PL · s2mm</strong><small>把四个结果写回 DDR</small></div>
  <figcaption>VCK190 矩阵乘向量示例的数据路径。箭头表示数据方向。</figcaption>
</figure>

## 跟踪一次计算和写回

1. **准备输入。** 主机程序在 XRT 缓冲对象中写入 16 个 A 元素和 4 个 B 元素。它把输入同步到设备，提交两个 `mm2s` 实例和一个 `s2mm` 实例，再启动 AIE 图的一次迭代。
2. **计算。** AIE 图的两条输入流把数据交给 `MatMul` 的两个输入缓冲。内核读取 A 和 B，用 `aie::mmul` 计算，再把四个结果存入输出缓冲。第一行的点积是 **1 × 1 + 2 × 2 + 3 × 3 + 4 × 4 = 30**。
3. **收回结果。** `s2mm` 从输出流读取四个字并写入 DDR。主机程序等待 PL 内核完成，然后把输出逐项与预期值 **30、70、110、150** 比较。

这里的有效负载是 A 的 64 B、B 的 16 B 和结果的 16 B。DDR 事务数量和执行时间还取决于地址、突发、流量和工具生成的实现。 [主机程序](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/Host_srcs/host.cpp) · [预期输出](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/Host_srcs/golden_data.h) · [计算内核](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/AIE_Kernel/aie_srcs/MatMul.cpp) · [输出写回源码](https://github.com/Xilinx/Vitis-Tutorials/blob/08ae81dcfdd48d7611c6550d19a5d82e2d0a23de/Getting_Started/Vitis/Versal_w_PetaLinux/VCK190/HLS_Kernels/s2mm.cpp)

## 改动接口时要对齐什么

先对齐每次迭代的**元素宽度、数量和顺序**。例如，若输出端仍只提供四个字，而 `s2mm` 被要求读五个，它会等待缺少的第五个字。若下游暂时读不走，流接口会通过背压限制上游。扩大计算规模时，需要一起检查图的端口、PL 循环长度和缓冲深度。 [AIE 流与 FIFO 深度](https://docs.amd.com/r/2026.1-English/ug1079-ai-engine-kernel-coding/FIFO-Depth?contentId=ailJVWsUm7AwwoVi3NNn5A)

设备写回与主机可见性各有完成条件。在需要显式维护缓冲可见性的平台上，主机要在输出写回完成后按 XRT 的缓冲规则同步，再读映射结果。 [XRT 缓冲区读写与同步](https://xilinx.github.io/XRT/2024.2/html/xrt_native_apis.html)

要继续追踪 PL 发出的内存读怎样进入芯片片上网络，可以从一笔 AXI 读请求看入口、交换和响应。 [AMD Versal NoC 读请求案例](../../interconnect/NOC/07-workload-cases/published-noc-case.md)
