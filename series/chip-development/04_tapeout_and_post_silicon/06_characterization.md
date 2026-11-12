# Characterization

## 前置知识

- 建议先读 [Post-silicon Bring-up](./04_post_silicon_bringup.md)。
- 建议理解 [Characterization](../00_overview/05_glossary.md#characterization)、[PVT Corner](../00_overview/05_glossary.md#pvt-corner)、[ATE](../00_overview/05_glossary.md#ate)、[Final Test](../00_overview/05_glossary.md#final-test)。

## 核心概念

Characterization 是系统测量芯片在电压、温度、频率、工艺、功耗、接口 margin、真实 workload 下的行为。Bring-up 证明“能跑”，characterization 证明“在什么条件下稳定跑、性能和功耗是多少、datasheet 应该怎么写”。

对 AI 芯片，characterization 不能只跑峰值 TOPS。真实指标包括 memory bandwidth、latency、utilization、batch size、compiler-generated workload、模型推理吞吐、功耗效率、热降频、软件栈稳定性。

## 关键活动顺序

1. 定义 characterization matrix：电压、频率、温度、workload、接口速率、样品数量。
2. 选择样品：不同 wafer、die location、package lot、速度 bin、异常样品。
3. 搭建实验平台：thermal chamber、programmable power supply、power analyzer、ATE、EVB、host software。
4. 做 shmoo：扫描电压/频率/温度，观察 pass/fail 边界。
5. 测功耗：idle、typical、peak、scan/BIST、real AI workload。
6. 测性能：microbenchmark、kernel、模型、端到端延迟和吞吐。
7. 测接口 margin：PCIe/SerDes/DDR/HBM training、眼图、误码率、SI/PI 条件。
8. 生成 operating condition、guardband、datasheet、binning 和 test limit。

## 工具和设备

常见设备包括 thermal chamber、ATE、power analyzer、oscilloscope、protocol analyzer、BERT、logic analyzer、programmable power supply。软件工具包括 lab automation scripts、Python data pipeline、dashboard、compiler/runtime benchmark suite、ATE data analysis 工具。

## 角色与典型时长

角色包括 characterization engineer、test engineer、silicon validation、firmware/software、architecture、power/thermal、PHY/IP vendor、product。基本 characterization 可能数周；完整 PVT、接口、功耗、性能和 binning 可能数月，并持续到量产爬坡。

## 关键决策点

- Datasheet 规格如何定：太激进会增加 field failure，太保守会损失性能和 ASP。
- Guardband 多大：要平衡可靠性、良率、性能和客户承诺。
- Binning 策略：按频率、功耗、功能、接口能力分档销售。
- Workload 代表性：benchmark 是否代表客户真实场景。
- 是否降频/禁用功能：如果某些 corner 不稳定，需决定规格调整还是 respin。

## 先进节点与成熟节点差异

先进节点 variation、leakage、IR drop、thermal 和接口 margin 更敏感，characterization 样品和场景需要更系统。HBM/SerDes/高速 IO 会增加实验复杂度。成熟节点 test chip 的 characterization 可以更轻，但如果目标是量产产品，仍要建立 datasheet 和 guardband。

## 常见坑

- 只测室温典型电压，不测高温低压或低温高压 corner。
- 用 synthetic TOPS benchmark 代替真实模型和软件栈。
- 没有记录样品来源，无法关联 wafer map 和 yield。
- Characterization 数据没有回到 ATE test limit 和 datasheet。
- 过早发布性能数据，后续 guardband 后达不到宣传指标。
- 忽略 thermal throttling，客户系统中无法维持实验室峰值。

## 上下游接口

上游输入是 bring-up 可用样品、firmware、benchmark、ATE program、power/thermal setup。下游输出是 datasheet、binning、operating conditions、test limits、errata、customer guide、production ramp criteria。

Characterization 结果会反向修改产品规格。若某频率在高温低压 fail，可能需要降低 datasheet max frequency、限制 workload、改 test program 或进入 respin。

## 创业公司取舍

创业公司应把 characterization 当作产品定义的一部分，而不是工程收尾。AI 芯片尤其要让 compiler/runtime 团队参与，否则硬件测出来的峰值和客户可用性能会脱节。

可以先做少量样品的快速 characterization 支撑 early customer demo，但不能把它当量产规格。客户承诺应等足够样品、PVT、功耗、接口和 workload 数据闭环后再锁定。

## 典型场景

芯片在实验室跑 INT8 GEMM 达到目标 TOPS，但真实 transformer inference 只有一半性能。Characterization 发现瓶颈是 compiler tiling 导致 SRAM bank conflict 和 NoC 拥塞，功耗也因数据搬运偏高。最终 datasheet 不再只写峰值 TOPS，而增加推荐 batch/shape、功耗模式和 compiler 版本要求。

## 后续阅读

- [Yield Analysis](./07_yield_analysis.md)
- [Silicon Revision](./08_silicon_revision.md)
- [Volume Ramp](../05_production_and_lifecycle/02_volume_ramp.md)
- [AI 芯片特有考虑](../06_cross_cutting_topics/06_ai_chip_specific.md)

## 参考公开来源

- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)
- [Keysight semiconductor test resources](https://www.keysight.com/)
- [Tektronix measurement resources](https://www.tek.com/)
- [Teradyne semiconductor test overview](https://www.teradyne.com/)

## 内容可信度说明

- **公开信息（高可信）**：PVT、shmoo、power measurement、ATE、thermal chamber、datasheet/guardband 的基本概念。
- **行业惯例（中可信）**：characterization matrix、binning、test limits、datasheet 更新和客户规格锁定流程。
- **经验性观察（中低可信）**：AI 芯片真实性能高度依赖 compiler/runtime/workload，峰值 TOPS 容易误导。
- **不确定/需向资深工程师确认（低可信）**：具体 binning 规则、guardband、样品数、workload 代表性和客户规格接受标准。
