# 按目标学习 BUS

上级：[01 概览与问题定义](./README.md)

相关：[学习路线图](./learning-roadmap.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你的目标不同，BUS 的阅读顺序也应该不同。这页给出按目标切分的最短学习路径。

## 目标 1：先建立系统判断力

1. [BUS 在解决什么问题](./problem-statement.md)
2. [BUS 分类框架](./taxonomy.md)
3. [BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)
4. [地址、数据、响应与事务语义](../02-fundamentals/transaction-address-data-response.md)
5. [分层总线与协议分工](../03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles.md)
6. [MCU / SoC / AI 芯片中的 BUS 对照](../06-scenarios-case-studies/mcu-soc-ai-bus-comparison.md)

## 目标 2：做 RTL、协议适配或互连设计

1. [仲裁、顺序性与 Backpressure](../02-fundamentals/arbitration-ordering-backpressure.md)
2. [AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)
3. [AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)
4. [AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)
5. [AXI Narrow Transfer 与 WSTRB](../03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)
6. [Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)
7. [Shared Bus、Bus Matrix 与 Crossbar](../04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md)

## 目标 3：做 SoC 集成、bring-up 或系统软件

1. [MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)
2. [Boot Path 与地址映射初始化](../04-microarchitecture-integration/boot-path-address-map-initialization.md)
3. [Debug Path 与 System Access](../04-microarchitecture-integration/debug-path-system-access.md)
4. [IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)
5. [Doorbell、Completion 与 Interrupt Flow](../04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)
6. [AXI 属性、Cacheability 与 Barrier](../04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)
7. [APB、MMIO 与普通内存的软件模型对照](../06-scenarios-case-studies/apb-mmio-memory-software-model.md)

## 目标 4：做 DMA / Memory / 性能分析

1. [AXI 与 DMA 的系统接口](../04-microarchitecture-integration/axi-dma-system-interface.md)
2. [DMA Descriptor Fetch、Data Move 与 Writeback](../04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md)
3. [AXI 到 DDR Controller 的路径](../04-microarchitecture-integration/axi-to-ddr-controller-path.md)
4. [Read/Write Combine 与 Bus Turnaround](../04-microarchitecture-integration/read-write-combine-turnaround.md)
5. [Row Locality、Return Path 与 AXI 体验](../04-microarchitecture-integration/row-locality-return-path-axi-experience.md)
6. [带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)
7. [Counters、Trace 与观测点设计](../05-performance-debug/counters-trace-observation-points.md)

## 目标 5：做调试定位和故障复盘

1. [Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)
2. [AXI Waveform Debug 方法](../05-performance-debug/axi-waveform-debug-method.md)
3. [CPU 读 MMIO 卡死案例卡](../06-scenarios-case-studies/cpu-mmio-read-hang-case-card.md)
4. [DMA Completion 丢失案例卡](../06-scenarios-case-studies/dma-completion-missing-case-card.md)
5. [IOMMU Fault 案例卡](../06-scenarios-case-studies/iommu-fault-case-card.md)

## 目标 6：做汇报、评审或知识沉淀

1. [BUS 一页版总览](../07-reference/bus-one-page.md)
2. [AXI vs TileLink 对照](../06-scenarios-case-studies/axi-vs-tilelink-comparison.md)
3. [AI 芯片里的 BUS vs NoC](../06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)
4. [BUS 设计检查清单](../07-reference/bus-design-checklist.md)
5. [互连方案评估模板](../07-reference/interconnect-evaluation-template.md)
6. [BUS 协议阅读模板](../07-reference/protocol-reading-template.md)

## 一句话理解

学 BUS 最怕平均用力。先按目标选路径，更容易把这套知识变成真正能用的系统判断。
