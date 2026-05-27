# CIM 产业全景：Startup、IDM、IP 公司、学术孵化的分工

上级：[08 产业与产品](README.md)
相关：[公司比较矩阵](company-comparison-matrix.md), [商业化路径](value-chain-and-commercialization.md), [CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md)

## 这页在回答什么问题

这页回答：CIM/PIM/NMC 产业里不同参与者到底在卖什么，以及它们为什么会走向不同路线。

**Startup** 的优势是可以重做计算范式。Mythic 选择 Flash-based analog CIM，是因为 analog array 可以把权重存储和矩阵乘法放在同一物理平面内，适合追求极端能效的 edge inference；代价是 calibration、良率、模型适配和客户信任都要自己证明。Axelera 选择 SRAM-based digital CIM，是因为它更接近标准 CMOS、标准 foundry 和数字验证流程，牺牲一部分 analog 极限能效，换来更可控的软件栈和产品形态。

**Memory vendor** 的优势是掌握 DRAM/HBM/GDDR 供应链、封装和客户入口。Samsung HBM-PIM 与 SK hynix GDDR6-AiM/AiMX 的产业逻辑不是替代 AI accelerator，而是把部分 memory-bound 运算推到 memory die/bank 近侧，减少 [RAM wiki 的 DRAM/HBM 数据搬移](../../../RAM/wiki/05-dram-protocol-families/README.md)。这类路线的弱点是 memory die 面积、功耗、标准接口、controller 支持和客户软件栈都受既有 memory ecosystem 约束。

**Foundry/IP 公司** 不一定直接卖 CIM 产品，却控制工艺节点、SRAM bitcell、embedded NVM、3DIC、DFT 和良率模型。SRAM-CIM 如果想商业化，需要和 [FAB wiki 的 process node 与 DFT/test](../../../FAB/wiki/README.md) 绑定；ReRAM/PCM/Flash CIM 如果想商业化，还要解决新器件集成、retention、endurance 和 inline test。foundry/IP 的产业价值是把“论文 macro”变成可复用 PDK/IP/测试方法，而不是做一次性 demo。

**System company** 关注的是部署路径。PCIe card、M.2 module、DIMM module、edge box、server appliance 会把问题从电路转成 [BUS wiki 的 PCIe/DMA/MMIO](../../../BUS/wiki/README.md)、driver、runtime、thermal、field update 和运维。系统公司采购时优先看模型能否跑在可维护的软件栈上、能否在客户现场稳定工作，而不是某个 macro 的峰值能效。

**Academic spin-off** 的优势是能从器件、电路、模型协同设计切入；弱点是缺少产品验证和供应链控制。很多 ReRAM/PCM/MRAM CIM 方案在 09 章更有价值，因为它们回答的是“未来可能的器件-计算耦合方式”，不是“当下客户可以买到什么”。

按技术路线看，产业格局可以压缩成四类：

| 路线 | 产品化优势 | 产业脆弱点 |
| --- | --- | --- |
| SRAM-CIM | 标准 CMOS、数字验证友好、可做 chip/card/module | SRAM 面积大，片上容量限制模型规模 |
| Flash/ReRAM analog CIM | 权重密度和 MAC 能效潜力高 | 器件一致性、写入校验、ADC、校准、良率难 |
| DRAM/HBM/GDDR-PIM | memory vendor 可复用现有内存客户和封装能力 | 需要 controller/runtime/标准接口配合，部署慢 |
| NMC/module-side near-data | 更容易接入 host/server 生态 | 不具备 cell-level CIM 的能效上限，受总线和同步限制 |

## 一句话理解

产业里的路线差异，本质上是“谁控制 supply chain、谁承担软件接入、谁为量产测试买单”的差异。

## 产业启示

CIM startup 可以快速证明新计算范式，但最难跨过客户部署和量产测试；memory vendor 可以把 PIM 放进既有内存路线图，但必须让 host、controller、compiler/runtime 一起变化；NMC 更像系统集成路线，牺牲物理同混程度，换取更清晰的部署边界。
