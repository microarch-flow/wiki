# 06 典型系统与案例

这一章把 BUS 放回具体系统里看。前面章节讨论 transaction、协议、微架构和调试方法；第 06 章用 MCU/SoC/AI、AXI crossbar、APB 子系统、MMIO hang、DMA completion、IOMMU fault、AXI/TileLink、BUS/NoC 等案例，把抽象概念落到系统判断。

## 本章入口

1. [MCU / SoC / AI 芯片中的 BUS 对照](./mcu-soc-ai-bus-comparison.md)
2. [AXI Crossbar 案例卡](./axi-crossbar-case-card.md)
3. [APB Peripheral Subsystem 案例卡](./apb-peripheral-subsystem-case-card.md)
4. [CPU 读 MMIO 卡死案例卡](./cpu-mmio-read-hang-case-card.md)
5. [DMA Completion 丢失案例卡](./dma-completion-missing-case-card.md)
6. [IOMMU Fault 案例卡](./iommu-fault-case-card.md)
7. [AXI vs TileLink 对照](./axi-vs-tilelink-comparison.md)
8. [AI 芯片里的 BUS vs NoC](./bus-vs-noc-in-ai-chip.md)
9. [APB、MMIO 与普通内存的软件模型对照](./apb-mmio-memory-software-model.md)

## 本章主线

脱离系统场景谈 BUS，容易把协议能力和系统需求错配。真正的判断来自具体场景里的 Resource、Topology、Interaction、Capability：共享什么资源，互连如何组织，事务如何闭环，需要哪些协议和调试能力。

| 案例 | 关键判断 |
| --- | --- |
| MCU / SoC / AI | BUS 角色随控制语义和数据规模变化 |
| AXI crossbar | 局部并发受目标端口、ID slot 和 return path 限制 |
| APB 子系统 | 低成本控制路径需要明确错误、side effect 和 PREADY 行为 |
| CPU MMIO hang | device read 必须返回数据、错误或 timeout |
| DMA completion 丢失 | data done 与 software-visible done 必须分开 |
| IOMMU fault | fault 要按 stream/context、IOVA 和子事务阶段归因 |
| AXI vs TileLink | 协议选择取决于生态边界和生成式能力 |
| BUS vs NoC | 控制语义与大规模数据交换要有清晰边界 |
| APB / MMIO / memory | 同样 load/store 形式下的软件语义不同 |

## 建模启示

第 06 章给模型提供案例化校验。每个案例都要回答四个问题：Resource 是否被正确抽象，Topology 是否解释了阻塞范围，Interaction 是否闭环到 response/completion/error，Capability 是否匹配系统规模、软件语义和可诊断性。

事件模型要能跨案例复用。例如 `doorbell_accept`、`descriptor_fetch_done`、`completion_visible`、`interrupt_assert`、`timeout_fire`、`fault_recorded`、`id_slot_release`、`apb_access_done`、`noc_packet_inject`。这些事件让案例不是孤立故事，而是对前面章节模型的压力测试。
