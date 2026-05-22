# 按目标学习 BUS

上级：[01 概览与问题定义](./README.md)

相关：[学习路线图](./learning-roadmap.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

当你的目标不是“从头系统学习”，而是要解决某类工程问题时，应该怎样裁剪 BUS wiki 的阅读路径。

## 先说明边界

[学习路线图](./learning-roadmap.md) 给默认最小闭环，适合从概念依赖开始系统补课。本页给目标导向路径，适合你已经知道当前问题属于 RTL/协议、SoC 集成、DMA/Memory、调试定位或方案评审，需要用最短路径拿到可执行判断。

目标导向阅读一定会牺牲完整性。它的价值是减少无关细节，但代价是容易漏掉前置概念。多数路径会保留必要基础文章；对调试和评审类路径，则必须依靠回跳规则补足前置概念，防止直接把协议字段、案例现象或 checklist 当成结论。

## 目标 1：快速建立系统判断力

当你面对一张 SoC 框图，想先判断“这里为什么用 BUS、哪里应该用 NoC、哪里只需要 point-to-point”时，优先读问题定义和分类框架。不要先读 AXI 细节，因为此时你需要的是互连选型坐标，而不是某个协议的字段能力。

必读路径：

1. [BUS 在解决什么问题](./problem-statement.md)
2. [BUS 分类框架](./taxonomy.md)
3. [BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)
4. [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)
5. [MCU / SoC / AI 芯片中的 BUS 对照](../06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)

这条路径会延后 AXI burst、WSTRB、IOMMU、DDR 细节。它换来的是先建立“控制面、数据面、共享资源、事务闭环”的判断框架。

## 目标 2：做 RTL、协议适配或互连设计

当你要实现 master/slave、bridge、adapter、crossbar 或协议转换时，核心风险不是“字段名记错”，而是通道之间的依赖、outstanding 状态、返回匹配、回压传播和顺序语义没闭合。

必读路径：

1. [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)
2. [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)
3. [AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)
4. [AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)
5. [AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)
6. [AXI Narrow Transfer 与 WSTRB](../03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)
7. [Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)
8. [Shared Bus、Bus Matrix 与 Crossbar](../04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)

这条路径刻意延后软件模型和系统案例。它优先保证你能回答：每个请求什么时候被接受，数据拍如何推进，response 如何回来，哪个 FIFO 满了会把 stall 传到哪里。

## 目标 3：做 SoC 集成、bring-up 或系统软件

当问题发生在 boot、MMIO、debug、interrupt、cacheability 或 IOMMU 上时，协议吞吐不是第一优先级。你更需要知道软件看到的地址、属性、状态和完成通知，如何映射到 BUS transaction。

必读路径：

1. [BUS 在解决什么问题](./problem-statement.md)
2. [MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)
3. [Boot Path 与地址映射初始化](../04-microarchitecture-integration/boot-path-address-map-initialization.md)
4. [Debug Path 与 System Access](../04-microarchitecture-integration/debug-path-system-access.md)
5. [IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
6. [Doorbell、Completion 与 Interrupt Flow](../04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)
7. [AXI 属性、Cacheability 与 Barrier](../04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)
8. [APB、MMIO 与普通内存的软件模型对照](../06-scenarios-case-studies/apb-mmio-memory-software-model.md)

这条路径会少读 AXI 细节。代价是你不会立刻掌握五通道波形分析；收益是能更快判断“访问为什么不可达、为什么 completion 不可见、为什么 barrier 不能替代 cache maintenance”。

如果问题开始涉及 request 是否已经被接受、response 是否返回、backpressure 是否传播，就回跳到 [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md) 和 [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)。

## 目标 4：做 DMA / Memory / 性能分析

当目标是解释吞吐、尾延迟、DDR 抖动或 DMA 数据搬运效率时，阅读路径应该沿数据面走。不要只看理论带宽，因为真实瓶颈经常出现在 outstanding 深度、burst 拆分、memory controller 调度和 return path。

必读路径：

1. [位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)
2. [AXI 与 DMA 的系统接口](../04-microarchitecture-integration/axi-dma-system-interface.md)
3. [DMA Descriptor Fetch、Data Move 与 Writeback](../04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)
4. [AXI 到 DDR Controller 的路径](../04-microarchitecture-integration/axi-to-ddr-controller-path.md)
5. [Read/Write Combine 与 Bus Turnaround](../04-microarchitecture-integration/read-write-combine-turnaround.md)
6. [Row Locality、Return Path 与 AXI 体验](../04-microarchitecture-integration/row-locality-return-path-axi-experience.md)
7. [带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)
8. [Counters、Trace 与观测点设计](../05-performance-debug/counters-trace-observation-points.md)

这条路径会延后 MMIO 和 boot/debug。它适合回答“为什么平均带宽看起来够，某个 master 仍然长尾很差”。

## 目标 5：做调试定位和故障复盘

调试路径要先分类现象，再追事务生命周期。直接看全部波形会让你在五条通道里来回扫，却不知道第一处失去 forward progress 的位置在哪里。

必读路径：

1. [Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)
2. [AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)
3. [AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)
4. [CPU 读 MMIO 卡死案例卡](../06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)
5. [DMA Completion 丢失案例卡](../06-scenarios-case-studies/dma-completion-missing-case-card.md)
6. [IOMMU Fault 案例卡](../06-scenarios-case-studies/iommu-fault-case-card.md)
7. [BUS 故障复盘模板](../07-reference/bus-debug-postmortem-template.md)

这条路径牺牲系统性学习，换取定位效率。它要求你把每个现象翻译成：request 是否被接受、target 是否服务、response 是否生成、return path 是否被堵、软件是否看到了完成。

如果无法解释 `timeout / fault / hang` 分别对应事务生命周期里的哪个断点，就先回跳到 [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)，再看波形。

## 目标 6：做汇报、方案评审或知识沉淀

当你要向别人解释 BUS 方案，或评审一个互连设计，最重要的是把协议能力、系统角色、风险和观测点放在同一张判断表里。此时不需要重读全部机制，而要用 reference 文档统一语言。

必读路径：

1. [BUS 一页版总览](../07-reference/bus-one-page.md)
2. [BUS 设计检查清单](../07-reference/bus-design-checklist.md)
3. [Master/Slave/Bridge 设计清单](../07-reference/master-slave-bridge-checklists.md)
4. [DDR/IOMMU/Debug 集成清单](../07-reference/ddr-iommu-debug-checklists.md)
5. [互连方案评估模板](../07-reference/interconnect-evaluation-template.md)
6. [BUS 协议阅读模板](../07-reference/protocol-reading-template.md)

这条路径的风险是容易只做 checklist，不理解背后的机制。它适合统一语言和评审框架，但不能单独支撑 ordering、outstanding、错误返回、DDR/IOMMU 路径或软件可见性结论。遇到这类争议时，协议问题回跳到 03，系统路径问题回跳到 04，性能和调试问题回跳到 05；否则 checklist 会变成没有证据链的伪结论。

## 一句话理解

按目标学习 BUS 的关键不是少读，而是先读能改变当前判断的文件，把无关机制延后到真正需要时再展开。

## 建模启示

目标导向阅读对应目标导向建模。做 RTL/协议适配时，模型要保留握手、buffer、ID、burst 和 response matching。做 SoC 集成时，模型要保留地址窗口、访问属性、可见性和错误路径。做 DMA/Memory 性能时，模型要保留 burst、outstanding、DDR service、return path 和 counters。做故障复盘时，模型要保留 transaction lifecycle 上每个可观测事件。

如果模型目标只是方案评审，VALID/READY 逐拍行为、payload bit 值和寄存器字段编码可以折叠成能力和风险项；如果模型目标是解释 hang 或长尾延迟，就不能只保留平均服务时间。阅读路径和模型粒度必须绑定：目标越接近实现和调试，越要保留事件、队列、顺序和错误闭环；目标越接近汇报和选型，越要保留约束、取舍和适用边界。
