# Silicon Revision

## 前置知识

- 建议先读 [Post-silicon Debug](./05_post_silicon_debug.md)。
- 建议先读 [Yield Analysis](./07_yield_analysis.md)。
- 建议理解 [Respin](../00_overview/05_glossary.md#respin)、[ECO](../00_overview/05_glossary.md#eco)、[Mask Cost](../00_overview/05_glossary.md#mask-cost)、[流片 Tapeout](../00_overview/05_glossary.md#流片-tapeout)。

## 核心概念

Silicon revision 是对芯片硅版本进行修正或迭代。触发原因可能是功能 bug、性能不达标、功耗超标、良率差、封装问题、客户需求变化或成本优化。Respin 不是“改代码重新编译”，而是重新走设计修复、验证、后端、signoff、tapeout、制造、封装和 bring-up 的完整闭环。

创业公司应默认第一颗复杂芯片可能需要 revision。计划中没有 respin 预算和时间 buffer，等于把公司押在一次流片完美成功上。

## Revision 类型

- Firmware/compiler workaround：不改硅，用软件避开 bug，最快但有功能/性能边界。
- Package/board revision：修封装、板卡、电源、clock、SI/PI，不改 die。
- Metal ECO：利用 spare cell 或改金属层修小逻辑/连线，成本和周期低于 full respin，但能力有限。
- Base-layer ECO：改晶体管层或底层，接近 full respin 成本。
- Full respin：重新生成完整 mask set，适合大结构、macro、模拟/IP、严重逻辑 bug。
- Product stepping：在修 bug 同时优化 PPA、yield、test、SKU。

## 决策依据

需要综合判断：

- Bug 严重性：数据错误、死锁、安全问题、客户可见问题优先级高。
- Workaround 是否可接受：是否损失性能、功耗、功能、可靠性或客户体验。
- 影响范围：所有样品、某 PVT、某 workload、某 wafer lot、某封装。
- 客户和量产计划：是否阻断 design win、qualification 或 revenue。
- 修改范围：metal-only 是否可行，是否需要 full mask。
- 验证成本：fix 是否容易证明不会引入新 bug。
- 现金和时间：公司是否有资金和 runway 等待下一版硅。

## Respin 流程

1. Root cause closure：不能只凭猜测改硅。
2. Fix proposal：列出 RTL/netlist/metal/package/firmware 方案和副作用。
3. 设计修改：RTL ECO、netlist ECO、metal ECO 或 package/board 修改。
4. Regression：仿真、formal、CDC/RDC、DFT、STA、LEC、power、DRC/LVS。
5. Signoff review：确认只修改必要内容，waiver 更新。
6. Tapeout and fab：按修改类型进入 mask/fab。
7. Bring-up revalidation：证明 bug 修复且没有破坏旧功能。
8. Errata/version management：记录旧版本限制、新版本差异和软件兼容性。

## 角色与典型时长

角色包括 silicon debug lead、RTL/DV、后端、STA/PV、DFT/test、firmware/compiler、product、customer/FAE、foundry/OSAT、项目负责人。Metal ECO 可能是数周到数月量级；full respin 加上 fab、封装、bring-up 通常是数月量级。具体取决于节点、mask 层、foundry slot 和修改范围。

## 成本量级

Firmware workaround 成本主要是工程时间和性能/功能损失。Board/package revision 可能是数千到数十万美元量级，复杂封装更高。Metal-only respin 在先进节点可能是数十万到数百万美元量级。7nm 以下 full mask/full respin 通常可能是数百万到千万美元量级，并叠加 wafer、封装、测试、bring-up、客户延误和机会成本。

这些数字只能做量级判断，具体报价必须向 foundry、OSAT 和服务商确认。

## 先进节点与成熟节点差异

7nm 及以下 revision 的核心难点是 mask 成本高、fab 周期长、signoff corner 多、IP/PDK 版本严格、metal ECO 能力受限且验证成本高。低电压和高功耗密度还会让“看似小修改”影响 timing、IR、EM 和 SI，需要完整回归。先进封装或 HBM 项目中，respins 还可能牵涉 package/substrate/HBM 供应窗口。

28nm/16nm respin 成本和 signoff 难度通常低很多，metal ECO 也相对更可管理，因此适合第一颗芯片或 test chip 学习。但成熟节点 full respin 仍是数月级工程，不是软件 patch。

## 常见坑

- Root cause 不清就 respin，第二版硅仍失败。
- Workaround 能跑 demo，但客户场景不可接受。
- Metal ECO 试图修超出能力范围的大结构问题。
- Fix 只回归 failing testcase，没有全量验证和后端 signoff。
- 忽略软件兼容性，A0/A1/A2 芯片行为不同但 driver 没区分。
- 对客户隐瞒 errata，后续 field failure 伤害信任。
- 融资和客户承诺建立在“零 respin”假设上。

## 上下游接口

上游来自硅后 debug、characterization、yield analysis、customer validation。下游是新的 tapeout、fab、bring-up、datasheet、errata、production ramp。Revision fix list 必须和验证计划、软件版本、ATE test、客户文档同步。

## 创业公司取舍

创业公司要区分“工程上能修”和“商业上该修”。如果 bug 可通过软件 workaround 且不影响目标客户，可以暂缓 respin，把资金用于下一版产品。如果 bug 影响数据正确性、安全、可靠性或核心性能，拖延 respin 可能更贵。

快速迭代芯片公司的现实边界是：架构模型、RTL 生成、验证回归可以快；但每次硅 revision 仍要经历 signoff、mask/fab、封装和 bring-up。真正的优势应是让每一版硅更少不确定性，而不是幻想硅片像软件每天部署。

## 典型场景

首版 NPU 在大多数模型上正确，但某稀疏 attention 模式下结果偶发错误。Debug 发现是某 FIFO full/empty 边界 bug。Compiler 可以避开该模式，但会让目标客户性能下降 30%。团队评估后决定 A0 用 workaround 支撑内部 demo，同时启动 A1 metal ECO；并把该场景加入 pre-silicon formal 和 regression，防止下版复发。

## 后续阅读

- [Tapeout Process](./01_tapeout_process.md)
- [Post-silicon Debug](./05_post_silicon_debug.md)
- [Volume Ramp](../05_production_and_lifecycle/02_volume_ramp.md)
- [第一颗芯片的务实建议](../07_for_software_background_founders/04_first_chip_pragmatics.md)

## 参考公开来源

- [Synopsys Formality](https://www.synopsys.com/implementation-and-signoff/signoff/formality-equivalence-checking.html)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：respin、ECO、metal ECO、full mask、errata、signoff regression 的基本概念。
- **行业惯例（中可信）**：root cause、fix proposal、regression、re-tapeout、bring-up revalidation 和 errata 管理流程。
- **经验性观察（中低可信）**：复杂首版芯片应预留 revision 预算和时间，不能假设一次流片即量产。
- **不确定/需向资深工程师确认（低可信）**：具体 ECO 层数、respin 报价、周期、客户是否接受 workaround 和 foundry mask 修改窗口。
