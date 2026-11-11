# 规范、产品目标与量产进展

上级：[HBF Wiki](./README.md)

**资料核查日期：2026-11-11。** 本页区分规范描述、厂商目标、设计里程碑和实际交付。它们是不同类型的证据。公开路线图会变化；使用具体数字前应重新核查版本和产品资料。

## OCP v0.7 描述了什么

OCP 于 2026-08-03 发布 [HBF High-Level Base Die Specification v0.7.0](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)。它包含架构、UCIe/AXI、软件、可靠性、封装和应用示例。版本号为 0.7.0；其中部分封装参数仍标记为待定或后续修订。

| 规范位置 | 数据 | 适用边界 |
| --- | --- | --- |
| 第 4.1、4.2 节 | 最多 16 个 host channel；NAND page 为 4 KiB | v0.7 的架构和功能描述 |
| 表 3 | 512 GiB | 该表中的 stack 容量计算示例 |
| 表 4，Grade 1 | 0.384 TB/s | 标注的最大用户带宽等级，不是应用实测 |
| 表 4，Grade 2 | 1.536 TB/s | 同上 |
| 表 4，Grade 3 | 3.072 TB/s | 同上 |

规范表 2 以 16 个 channel、每 channel 64 bit、32 GT/s 和 75% 接口效率计算，得到 3072 GB/s，即十进制的 3.072 TB/s。其 4.1 节正文另写有 3.072 TiB/s；这与表 2、表 4 的单位不一致。本页使用表格的计算与单位，并保留该不一致供读者核查，不能把两者视为相同数值。

这些是接口和配置的描述。达到上表上限还需要匹配的实现、请求分布和足够并发，实际有效带宽、延迟和尾延迟需要目标系统测量。

## Sandisk 首代目标与单位

[Sandisk 2025 HBF fact sheet](https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/sandisk/collateral/company/Sandisk-HBF-Fact-Sheet.pdf) 描述首代目标：16 个 256 Gb die、每 stack 512 GB、读取带宽 1.6 TB/s。文档将 GB 定义为十进制：1 GB = 10⁹ B；实际用户可用容量更少。它还把封装尺寸、stack 高度和功耗轮廓与 HBM4 比较。

按该资料的十进制单位计算：**256 Gb × 16 ÷ 8 = 512 GB**。OCP 表 3 的 **512 GiB** 使用二进制单位，约等于 549.8 GB。两个资料描述的对象和容量定义需要分别核实，不能把 512 GiB 与 512 GB 当作相同的精确容量。

Sandisk 的 **1.6 TB/s 读取目标**与 OCP 表格的 **Grade 3 3.072 TB/s 最大用户带宽等级**是不同来源和对象。没有具体产品测试，不能把规范等级当成首代产品的实测值。

## 功耗：公开目标与未知参数

上述 Sandisk fact sheet 使用“接近 HBM4 的功耗轮廓”的定性描述，没有在该文档中给出首代 HBF 的具体 W/stack。这个描述也没有提供足够条件，让我们推导一个可靠的功耗上下限。

建模时可以自行选择多个功率点做敏感性分析，但必须标注为**假设**，并说明活动占空比与边界。`容量 / W` 不能代替读取能耗 `J/bit`；平均功率也不能代替峰值功率和散热设计条件。具体 idle、读、写、ECC、接口和刷新功耗仍需产品数据或测量。

## 从路线图到交付

| 时间与证据 | 可以确认的内容 | 不能由此确认 |
| --- | --- | --- |
| 2025-08，Sandisk 与 SK hynix 合作公告 | 双方宣布合作建立 HBF 规范；Sandisk 当时提出 HBF 内存样品和推理设备样品的目标时间 | 这些目标已经兑现 |
| 2026-08，OCP v0.7 与 SK hynix 公告 | 已公开一个版本的技术规范及容量、带宽等级说明 | 规范内所有等级已有商业产品量产 |
| 2026-10，Sandisk 财年 2027 第一季度材料 | Sandisk 报告首颗 HBF memory die 已 tape-out，并表示首批 HBF 产品样品仍计划在下一日历年提供 | 样品已交付、良率达标或已规模量产 |

来源：[Sandisk 2025 合作公告](https://investor.sandisk.com/news-releases/news-release-details/sandisk-collaborate-sk-hynix-drive-standardization-high)；[SK hynix 2026 规范公告](https://news.skhynix.com/en/hbf-at-fms-2026/)；[Sandisk 财年 2027 第一季度材料，第 5 页](https://investor.sandisk.com/static-files/4ca97b6e-7da4-4d52-b4ac-0e80f462716f)。

较早路线图和较新进展的对象可能分别是 memory die、HBF 产品或包含 HBF 的推理设备；时间不能直接互换。Tape-out 是设计交付制造的里程碑，本身不等于功能验证完成或出货。对量产时间、良率、价格、寿命、实际系统性能和具体功耗，本次核查没有建立可直接用于产品保证的结论。

## 为什么堆叠量产还要看良率和测试

多颗 die 的堆叠需要分别考虑 die 测试、装配、垂直互连、散热和最终 stack 测试。某一环节失败都可能影响可交付数量；预先筛选已知良好 die（KGD）可以改变后续装配的风险，但筛选本身也有成本，测试覆盖率并非天然等于 100%。

只看一个人为构造的算术例子：假设 16 颗参与装配的 die 在组装后各有 99% 的独立可用概率，且必须全部可用，则同时可用的概率约为 **0.99¹⁶ ≈ 85.1%**。这个例子不包含 base die、互连和装配良率，也不包含共享缺陷、冗余修复或筛选策略。它不代表任何 HBF 产品的实际良率，只说明多个条件叠加时为什么需要逐项核算。

资料清单和待核实问题见[术语、资料与自测](./09-reference.md)。
