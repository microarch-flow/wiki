# Packaging

## 前置知识

- 建议先读 [Mask Making and Wafer Fab](./02_mask_making_and_wafer_fab.md)。
- 建议理解 [Package](../00_overview/05_glossary.md#package)、[OSAT](../00_overview/05_glossary.md#osat)、[HBM](../00_overview/05_glossary.md#hbm)、[Chiplet](../00_overview/05_glossary.md#chiplet)、[ATE](../00_overview/05_glossary.md#ate)。

## 核心概念

封装不是“芯片外壳”。它提供机械保护、电气连接、供电路径、散热路径、信号完整性、测试访问和系统集成边界。对 AI 芯片，封装可能是成本、性能和供应链的核心瓶颈，尤其涉及高功耗、大 die、HBM、高速 SerDes 或 chiplet 时。

封装选择必须在架构和后端早期介入。IO 数量、bump map、power rail、thermal sensor、JTAG/debug pin、HBM 位置、substrate 层数、board 走线都会反过来影响 floorplan 和产品成本。

## 常见封装类型

- QFN：成本低、适合小芯片和低 pin count，不适合高功耗高带宽 AI SoC。
- BGA：常见于中等复杂 SoC，提供较多 IO 和较好板级连接。
- FC-BGA：flip-chip BGA，适合高性能芯片，供电和散热能力更强。
- 2.5D interposer / CoWoS 类封装：用于 HBM、高带宽 chiplet 互连，成本和供应链复杂度高。
- Fan-out / advanced packaging：可改善 IO 密度和系统集成，但良率、工艺和供应链需专门管理。

## 关键活动顺序

1. 根据产品功耗、IO、内存带宽、成本目标选择封装方向。
2. 与 OSAT、substrate vendor、foundry、board/SI/PI 团队定义 bump map、substrate、power rails、thermal path。
3. 做 package SI/PI/thermal 仿真，评估高速接口、电源噪声和散热。
4. 与后端 floorplan 对齐 pad/bump、PHY、HBM、power grid、ESD 和 test access。
5. 设计封装基板、assembly flow、test socket、handler、probe/ATE 方案。
6. wafer sort 后送 OSAT assembly，进行封装、检查、final test。
7. 将封装样品交给 bring-up 和 characterization。

## 工具和设备

常见工具和能力包括 Cadence Sigrity、Ansys SIwave/HFSS、Keysight ADS、thermal simulation 工具、package layout 工具、substrate design flow。设备包括 wire bonder/flip-chip bonder、underfill、molding、X-ray inspection、C-SAM、thermal chamber、ATE handler、test socket。

## 角色与典型时长

角色包括 package engineer、SI/PI engineer、thermal engineer、board engineer、OSAT、substrate vendor、test engineer、foundry interface、system architect。成熟封装可在数周到数月完成设计和样品；先进封装、HBM、2.5D/chiplet 可能需要更长 lead time，并受产能和 substrate 供应影响。

## 关键决策点

- 是否使用 HBM/先进封装：可获得高带宽，但 NRE、供应链、测试和良率风险大。
- 封装热设计：散热能力不足会让芯片降频，影响产品承诺。
- Power rail 和 decoupling：供电路径差会造成 IR drop、noise 和 bring-up 不稳定。
- Debug/test access：封装若不给 JTAG、mode strap、power measurement 留足访问，会严重影响硅后。
- 首版封装是否保守：成熟封装可降低风险，但可能限制性能和 IO。

## 先进节点与成熟节点差异

先进节点芯片功耗密度更高、供电电压更低、IO 和内存带宽需求更高，封装对性能影响更明显。AI 芯片若使用 HBM 或 2.5D，封装不再是后段服务，而是系统架构的一部分。成熟节点或小 test chip 可以用较简单封装验证核心逻辑，降低 NRE 和供应链风险。

## 常见坑

- Tapeout 后才开始考虑封装，发现 bump map、power rail、PHY 位置不合理。
- 只看 die 功耗，不看 package thermal resistance 和系统散热。
- 没有准备 debug pins、strap、JTAG、电流测量点。
- 选择先进封装但没有锁定产能、substrate 和 HBM 供应。
- Final test socket 和 board 设计滞后，封装样品回来后无法高效 bring-up。
- 把 OSAT 报价当全成本，忽略 substrate、socket、test program、reliability 和失效分析。

## 成本视角

简单封装单位成本可能是美元以下到数美元量级；FC-BGA、高 pin count、大 substrate 会进入数十美元甚至更高；HBM/2.5D/CoWoS 类先进封装可能让单颗封装和内存成本成为系统 BOM 大头。NRE 还包括基板设计、mask/tooling、test socket、thermal solution、可靠性验证和工程样品。

具体价格高度动态，受封装厂、substrate 产能、HBM 供应、良率和订单量影响。创业公司必须实时询价，不应拿公开历史数字做融资模型。

## 上下游接口

上游接口是 floorplan、bump map、IO/PHY、power grid、thermal target、wafer sort。下游接口是 final test、bring-up board、系统散热、客户平台和量产供应链。

封装问题可能被误判为 silicon bug，例如电源噪声、焊点开路、substrate SI 问题、热降频。bring-up team 必须能区分 board/package/silicon/test program 问题。

## 创业公司取舍

第一颗芯片如果目标是验证架构和软件，尽量避免同时挑战先进封装、HBM、chiplet 和先进节点。可以先用成熟封装验证核心 compute tile、NoC 和软件栈，再在后续版本引入高带宽内存或先进封装。

如果商业目标必须使用 HBM，则封装、内存供应、OSAT、热设计和板级系统要从立项阶段进入关键路径，而不是流片后补。

## 典型场景

团队设计了一颗高端 AI 芯片，后端完成后才发现 HBM 封装 substrate 交期远超预期，test socket 也未准备。样片虽然按时制造完成，却无法及时封装和 bring-up。另一个团队选择首版不用 HBM，而是用外部 DDR 验证 NPU 架构和编译器，性能不如最终产品，但项目风险显著降低。

## 后续阅读

- [Post-silicon Bring-up](./04_post_silicon_bringup.md)
- [Characterization](./06_characterization.md)
- [Yield Analysis](./07_yield_analysis.md)
- [供应链](../05_production_and_lifecycle/03_supply_chain.md)

## 参考公开来源

- [ASE Technology packaging overview](https://www.aseglobal.com/en/technology/packaging)
- [Amkor advanced packaging overview](https://amkor.com/technology/advanced-packaging/)
- [TSMC 3DFabric overview](https://www.tsmc.com/english/dedicatedFoundry/technology/3DFabric)
- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：QFN、BGA、FC-BGA、2.5D、HBM、OSAT、SI/PI/thermal 的基本概念和供应链角色。
- **行业惯例（中可信）**：封装早期参与、bump map、substrate、test socket、thermal 和 board 协同是高性能芯片常见实践。
- **经验性观察（中低可信）**：创业公司首版应避免同时承担先进节点、HBM、先进封装和复杂软件栈所有风险。
- **不确定/需向资深工程师确认（低可信）**：具体 CoWoS/先进封装产能、报价、交期、HBM 可得性、封装良率和可靠性要求。
