# Tenstorrent Wormhole n150s 怎样协调读、算、写？

Wormhole 的一个 Tensix 核可以同时安排读、计算和写三个内核。它们通过本地 SRAM 中的环形缓冲传递张量分块。每个缓冲槽都有两个交接条件。生产者等空槽，消费者等数据。本文按 TT-Metalium `v0.67.4` 源码跟踪一次逐元素加法。 [架构与编程指南](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/METALIUM_GUIDE.md) · [官方算例主机程序](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/eltwise_binary.cpp)

## 一次加法用了哪些资源

n150s 装有一颗 Wormhole 芯片，提供 72 个 Tensix 核和 12 GB GDDR6。算例只用其中一个 Tensix 核。两个数据搬运 RISC-V 核分别运行读内核和写内核，由它们发起片上网络（NoC）传输。计算内核负责解包、逐元素加法和打包。芯片文档将 Tensix 的本地 SRAM 称为 L1。 [n150s 板卡规格](https://docs.tenstorrent.com/aibs/wormhole/) · [Tensix 编程指南](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/METALIUM_GUIDE.md#tt-metalium) · [内核配置](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/eltwise_binary.cpp#L110-L146)

主机程序为输入 A、B 和输出 C 各分配 64 个分块。一个分块（tile）有 32 × 32 个 BF16 元素，每元素 2 B，所以一个分块占 **2 KiB**。程序在同一个核的 L1 中创建三个环形缓冲，每个缓冲放两个分块，合计 **3 × 2 × 2 KiB = 12 KiB**。这是分块的存储量。核内寄存器和控制状态另计。 [缓冲配置](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/eltwise_binary.cpp#L45-L108)

| L1 环形缓冲 | 写入者 | 读取者 |
| --- | --- | --- |
| A、B 各一个输入缓冲 | 读内核 | 计算内核 |
| C 的输出缓冲 | 计算内核 | 写内核 |

## 一个分块怎样交接

1. **读入 A 和 B。** 读内核用 `reserve_back` 等到两条输入队列各有一个空槽，再发起两次 NoC 读。等 `noc.async_read_barrier()` 返回后，才用 `push_back` 发布两块输入。 [读内核](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/kernels/dataflow/read_tiles.cpp)
2. **计算 C。** 计算内核用 `cb_wait_front` 等两块输入就绪，将对应元素相加，结果先存入目标寄存器。它申请一个输出槽，把结果打包进去并发布。随后用 `cb_pop_front` 归还两块输入占用的槽。 [计算内核](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/kernels/compute/tiles_add.cpp)
3. **写回 C。** 写内核等到输出就绪，发起 NoC 写，将结果送回设备内存。它等 `noc.async_write_barrier()` 返回，再用 `pop_front` 归还输出槽。这样计算内核再次使用这个槽时，前一轮传输已完成。 [写内核](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/kernels/dataflow/write_tile.cpp)

官方算例把 B 的每个元素设为 −1。若 A 的某个值为 0.5，对应结果就是 −0.5。主机程序读回结果，逐项检查与参考值的绝对误差是否在 0.01 以内。按源码的分块次数计算，三个设备内核合计读 256 KiB、写 128 KiB 的 DRAM 有效载荷。主机上传和读回是另外的传输。 [主机输入与校验](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/eltwise_binary.cpp)

## 写内核跟不上时会在哪里等

假设前两个结果仍占着输出槽，第三组输入也已就绪。第三次相加可以先把结果放进寄存器，随后会在 `cb_reserve_back` 等空槽。由于计算内核要等输出发布后才归还输入槽，如果输入缓冲也填满，读内核接着会在申请输入槽时等待。这条等待链就是此算例的背压路径。缓冲能容纳多少分块可由配置复算。停顿持续多久取决于实机完成各步的速度。 [计算内核中的申请与释放顺序](https://github.com/tenstorrent/tt-metal/blob/d840499730e9c76f98e4d4da718d273ed0c372cc/tt_metal/programming_examples/eltwise_binary/kernels/compute/tiles_add.cpp)

## 接下来怎么读

- 从可编程逻辑和 AI Engine 的接口看另一种背压。 [AMD Versal VC1902](../amd-versal-vc1902/README.md)
- 把观察范围扩大到多个 tile，查看 BSP 屏障怎样划分本地计算和数据交换。 [Graphcore GC200](../Graphcore_IPU/README.md)
- 查看硬件命令怎样用信号量等待输入就绪和输出槽。 [Microsoft Maia 100](../microsoft-maia-100/README.md)
