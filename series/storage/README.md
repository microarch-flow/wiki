# 存储系统

程序先读数组里的一个整数 `A[0]`，等它返回，再读旁边的 `A[1]`。两次各要 4 个字节。为什么第一次可能要让八颗内存芯片一起工作，第二次却连一笔请求都没有发给内存？

## 第一次读，从哪个地址出发？ {#first-load}

假设处理器发出了这两笔读取，每个整数占 4 B。数组位于普通的、允许缓存的内存中。我们先跟着 `A[0]` 走到能提供数据的地方，再看看 `A[1]` 在哪里停下。想从器件或 NPU 案例读起，也可以直接[按问题选专题](#topics)。

在这个程序里，`A[0]` 的地址是 `0x00403000`。这是**虚拟地址**。操作系统可以把不同程序中编号相同的虚拟页放在不同的物理页里，所以处理器还需要知道当前程序的那一页映射到了哪里。

假设页大小为 4 KiB（4096 B），页表里已有一条允许读取的映射：虚拟页号 `0x403` 对应物理页号 `0x1`。处理器在保存近期地址翻译结果的 **TLB** 中找到了这条记录。虚拟页的起点是 `0x00403000`，物理页的起点是 `0x1000`。`A[0]` 正在页首，翻译后的地址就是 **`0x1000`**。旁边的 `A[1]` 距页首 4 B，翻译后的地址就是 `0x1004`。翻译保留了页内偏移。到这一步，处理器只算出了地址，还没有取到整数。[RISC-V 特权规范中的 4 KiB 页地址翻译](https://docs.riscv.org/reference/isa/v20260120/priv/supervisor.html#sv32)

[![从 A[0] 的虚拟地址追踪一次读取。页号翻译得到物理地址，L1 命中便取出 4 B；只有各级缓存都不能供数时，本例才继续到 DRAM 开行取数。](./assets/first-load-through-memory.svg)](./assets/first-load-through-memory.svg)

## 已经知道物理地址，为什么还要查 Cache？ {#cache-stop}

处理器附近的一级缓存（L1 Cache）可能已经留了一份副本。假设这块 L1 分成 64 组，每组有两个位置，每个位置能放一条 **64 B 的缓存行**，用物理地址选组。把物理内存每 64 B 编一个号，从 0 开始。`0x1000` 是十进制的 4096，恰好是编号 64 的缓存行起点。这条缓存行覆盖 `0x1000` 到 `0x103F`，一共装得下 16 个这样的整数。

这份副本可能在哪里？把缓存行按组轮流分配，编号 0 到 63 各去一组，编号 64 就回到第 0 组。编号 0 和 64 都去那里，单凭组号分不清两者。因此每个位置还保存一个地址标记（tag）。编号 64 绕过一轮，在这个例子里的 tag 是 1。

现在沿图选一条路。如果第 0 组里有一路有效、可读，tag 又等于 1，L1 就从这一行的偏移 0 到 3 取出 4 B。`A[0]` 的读取到这里便完成了。如果两路都不匹配，L1 要向下一级取这一行。下一级有可读的副本，就可以用它返回数据。图中画的是数据从哪里取得，地址翻译和查缓存的部分电路在实际处理器中也可以同时工作。[Cache 怎样比较两路并选出字节](./01-memory-hierarchy/02-access-paths/cache-hit-lookup.md)

## 如果一直找到主存，八颗芯片实际做了什么？ {#dram-read}

现在选另一条路。假设各级缓存都没有这条缓存行，也没有在途请求或其他处理器能提供副本。这笔 64 B 读取来到主存。刚才的“第 0 组”属于 L1，内存控制器还要根据同一物理地址选择自己的通道、bank 和行。**Bank** 是芯片中可以维持自身开行状态的一部分。

用一个能手算的配置看这次选择。主存地址从 0 开始，编号为偶数的 64 B 段给通道 0，奇数段给通道 1。在各自的通道里，连续分到的段再轮流给 16 个 bank。于是每分完 32 段，每个通道的每个 bank 恰好收到一段。本例每个 bank 的一行可容纳 128 个这样的段，填满才换下一行。从编号 0 开始数，**段 0、32、64 都分给通道 0 的 bank 0**，分别占它的行 0 内编号为 0、1、2 的位置。`A[0]` 所在的是段 64，所以要取的是行 0 内的第 3 个 64 B 段。这里的轮流分配是教学选择，实际控制器可以采用别的地址映射。[用同一串地址比较两种映射](./04-dram-controller/address-mapping-channel-rank-bank-row-col.md)

本例每个通道连着八颗共同响应的 DDR4 芯片，这一组称为一个 **rank**。每颗的数据接口是 x8，也就是每次传输 8 bit。假设目标 bank 已预充好，还没有打开行。控制器先发激活命令，八颗芯片各自在自己的 bank 0 打开行 0。每颗这一行有 1 KiB，八颗合计 **8 KiB**，数据暂存在芯片内部的行缓冲中。接着发列读命令，选择刚才算出的那一段。每次传输，八颗各送 1 B，合计 8 B。一次突发连续传 8 次（BL8），恰好 **64 B** 穿过外部数据总线。本例等整条缓存行填好，L1 再从中交给处理器 **4 B**。[DDR4 器件组织表](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_AS4C512M16D4B_AS4C1G8D4B_8Gb_DDR4_Datasheet_Rev1.0_Sep2024.pdf#page=2) · [看开行、选列与返回的阵列图](./03-dram/foundations/1t1c-cell-destructive-read.md#access-granularity)

## 再读 A[1]，可以在哪一步停下？ {#second-load}

让第一次读取完成，再让控制器关掉刚才的 DRAM 行。假设对应缓存行仍在 L1、有效且可读。现在读 `A[1]`，还需要重开 DRAM 行吗？

沿原图再走一次。虚拟地址 `0x00403004` 仍在同一页，翻译得到 `0x1004`。它也在编号 64 的缓存行里，仍然查第 0 组、比对 tag 1。这次只把行内偏移从 0 改为 4，L1 就能拿出偏移 4 到 7 的字节。**请求停在 L1。** DRAM 关掉了自己的行，L1 中那份 64 B 副本仍然可以用。回头看这几个数字，4 KiB 决定哪些地址共用一条翻译，64 B 决定哪些相邻字节一起留在缓存，8 KiB 是这组芯片同时打开的数据。程序每次只要求其中的 4 B。

**接下来读**　把开头的条件改一条：允许处理器在第一笔读取完成前就发出第二笔。如果所需字节还在路上，第二笔算命中 L1 吗？再跟着一次真正的缺失，看请求怎样返回。[读 A\[1\] 时，Cache 怎样知道它在这里？](./01-memory-hierarchy/02-access-paths/cache-hit-lookup.md) · [Cache miss 的处理](./01-memory-hierarchy/02-access-paths/cache-dram-coordination.md)

## 按问题选专题 {#topics}

| 我想弄懂什么 | 从哪里读起 |
|---|---|
| **存储层级与数据路径**　程序、缓存和主存怎样交接数据？到了 NPU，权重怎样送到计算单元？ | [存储系统概览](./01-memory-hierarchy/README.md) · [系统架构](./01-memory-hierarchy/01-system-basics/README.md) · [Cache 与 scratchpad](./01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md) · [NPU 数据路径](./01-memory-hierarchy/04-npu-case/README.md) |
| **SRAM 器件与应用**　几个晶体管怎样保住一个 bit？怎样把许多 bit 组织成可以寻址的阵列？ | [SRAM 基础](./02-sram/foundations/README.md) · [SRAM 应用](./02-sram/applications/README.md) |
| **DRAM 器件与接口**　为什么要开行？芯片内部怎样把数据送到引脚？ | [DRAM 单元与阵列](./03-dram/foundations/README.md) · [DRAM 命令与接口](./03-dram/protocols/README.md) · [HBM 接口](./03-dram/protocols/hbm-stacked-wide-io.md) |
| **DRAM 控制器与请求调度**　几笔读写同时排队，下一条命令该发给谁？ | [控制器导读](./04-dram-controller/README.md) · [命令调度](./04-dram-controller/command-scheduling-fr-fcfs.md) |
| **HBF 高带宽闪存**　NAND 按块擦除，SSD 更新 A 页后，为什么同一块里的 B 页还能读？换成 HBF，主机又要负责什么？ | [SSD 怎样在 NAND 中更新一页](./05-hbf/02-nand-foundations.md) · [HBF 写入与可靠性](./05-hbf/06-write-and-reliability.md) · [HBF 专题导读](./05-hbf/README.md) |
| **存储系统集成与选型**　同样的推理任务，需要多少外存带宽？怎样权衡封装、容量与成本？ | [专题导读](./06-system-integration/README.md) · [封装与集成](./06-system-integration/packaging/README.md) · [HBM 与 LPDDR 选型](./06-system-integration/hbm-vs-lpddr-for-npu.md) · [CXL 与近存计算](./06-system-integration/future-packaging-cxl-near-memory.md) |

想动手算一算，可从[查阅与练习](./reading-and-reference/README.md)挑一道题。需要逐章翻原来的笔记，可沿用[原 RAM 阅读路线](./reading-and-reference/01-reading/README.md)。跨到其他系列时，[芯片制造与封装](../chip-development/FAB/wiki/README.md)解释这些器件怎样做出来，[DMA 双缓冲](../microarchitecture/05-dma/04-programming-model/tiling-double-buffering.md)接着解释数据搬入时计算能否继续。
