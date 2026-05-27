# 公司横向比较矩阵

## 为什么需要单独做横评页

单张公司卡片适合记录事实，但不适合训练判断力。

如果没有横向比较页，很容易发生三种问题：

- 把 `macro`、`chip`、`card`、`system` 混在一起比
- 把 `startup`、`memory vendor`、研究样片放在同一维度看
- 只记住公司名字，却没有形成“路线差异”的直觉

因此，这一页的目的不是扩充公司名录，而是建立一套统一比较框架，让你看任何一个对象时都能回答：

1. 它到底卖的是什么层级的东西
2. 它最强的不是哪项指标，而是哪种系统价值
3. 它最脆弱的环节是在软件、供应链、产品化还是客户导入

## 横评前先统一口径

做 `CIM` 公司横评时，至少要先统一五个口径：

- 路线口径：`SRAM-CIM`、`ReRAM / analog CIM`、`DRAM / HBM-PIM`、`GDDR / AiM`
- 产品口径：`macro`、`chip`、`card/module`、`system`
- 指标口径：`macro-level`、`chip-level`、`system-level`
- 客户口径：`edge`、`mobile`、`auto`、`data center`、`HPC`
- 成熟度口径：研究样片、原型产品、可部署产品

如果这些口径不统一，表格越大，误导反而越强。

## 一张实用的比较矩阵

| 对象 | 角色 | 技术路线 | 产品形态 | 主要卖点 | 目标场景 | 软件依赖 | 供应链依赖 | 当前更像处于哪一层 | 主要风险 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Mythic](./company-cards/mythic-analog-cim.md) | startup | `analog CIM` | inference chip | 固定权重阵列内计算、低功耗推理 | edge、auto、robotics | 高，需要 compiler / runtime / model conversion | 中高，依赖制造、测试、校准与系统验证 | `chip -> product` | 精度、校准、量产一致性、客户验证 |
| [Samsung HBM-PIM](./company-cards/samsung-hbm-pim.md) | memory vendor | `DRAM / HBM-PIM` | memory-side product / system route | 减少 data movement、提升带宽利用率 | HPC、training、inference、AI infra | 中高，依赖 host、controller、runtime 协同 | 很高，依赖 memory、advanced packaging、系统接口 | `system route / platform capability` | workload 是否真 memory-bound、系统协同复杂度 |
| [SK hynix GDDR6-AiM / AiMX](./company-cards/sk-hynix-gddr6-aim-aimx.md) | memory vendor | `GDDR / PIM / AiM` | memory component -> accelerator card | memory-centric solution、面向 LLM / KV-cache 的系统切入 | AI infra、generative AI、HPC | 中高，依赖 runtime、host 协作与系统软件 | 很高，依赖 memory、board/card、集成与验证 | `card / demo system` | demo 到可部署产品的落差、系统接口与客户导入 |
| [TSMC 16nm CIM Macro](../09-research/case-studies/tsmc-16nm-cim-macro.md) | foundry-related research case | `CMOS-compatible SRAM / digital-friendly CIM` | macro / test chip | 工艺兼容、片上集成潜力 | edge、SoC integration research | 中，目前更偏研究工具链 | 中，主要依赖标准逻辑工艺路径 | `macro / research silicon` | 宏到 chip 的收益衰减、系统价值尚未被产品化验证 |

## 怎么读这张表

这张表最重要的不是“哪个公司更强”，而是看三组差异。

## 1. 谁在卖系统价值，谁在卖技术可能性

### 更偏系统价值

- Samsung HBM-PIM
- SK hynix AiM / AiMX

这两条路线的重点不是阵列本身，而是：

- memory-side processing
- 降低数据搬运
- 把产品推进到 module、card 或更接近系统的层级

### 更偏技术可能性或产品化尝试

- Mythic
- TSMC 16nm CIM Macro

前者更像 startup 试图把阵列原生计算做成产品，后者更像工艺兼容路径的研究样板。

## 2. 谁在控制供应链

### 控制力更强的

- Samsung
- SK hynix

原因不是它们“技术一定更好”，而是它们天然控制：

- memory 制造
- 高带宽产品路线
- 一部分接口与系统演进方向

### 控制力更弱但更灵活的

- Mythic

它的优势是路线鲜明、叙事集中，但劣势是：

- 对制造与验证伙伴依赖更强
- 量产链条控制力不在自己手里

### 研究价值强于产品控制力的

- TSMC 16nm CIM Macro

它对理解工艺兼容与宏设计非常有价值，但不应直接看成一个成熟商业对象。

## 3. 谁最容易被“漂亮指标”误导

### 最容易被宏级指标误导的

- TSMC 16nm CIM Macro
- 很多 `analog / ReRAM-CIM` 路线

因为它们更容易停留在：

- `macro`
- 局部 kernel
- 局部硅后结果

### 最容易被 system demo 误导的

- SK hynix AiMX

因为 card 或 demo system 的展示很容易让人高估可部署程度。

### 最容易被 marketing claim 误导的

- Mythic

不是因为它不重要，而是因为它代表的正是“技术叙事”和“工程现实”张力最大的那类对象。

## 用同一框架再看四个对象

## Mythic

更像：

- `startup + chip productization attempt`

最值得学的不是它的单项指标，而是：

- analog CIM 为什么有强吸引力
- 为什么软件、校准、验证和客户场景会成为真正门槛

## Samsung HBM-PIM

更像：

- `memory vendor + platform capability extension`

最值得学的是：

- 对大工作集和大模型来说，减少 processor-memory 数据往返本身就是路线价值

## SK hynix AiM / AiMX

更像：

- `memory vendor + solution posture`

最值得学的是：

- memory vendor 如何从 component 卖到 card / solution
- 为什么这类路线更适合用系统口径判断，而不是阵列口径

## TSMC 16nm CIM Macro

更像：

- `CMOS-compatible macro research benchmark`

最值得学的是：

- 什么样的路线更容易接近现实芯片流程
- 为什么工艺兼容性会显著影响产品化难度

## 这张表背后的三条结论

### 1. 技术路线不等于商业路线

`analog CIM`、`SRAM-CIM`、`HBM-PIM` 说的是技术路径，不直接等于：

- 谁更容易卖出去
- 谁更容易量产
- 谁更容易被客户接受

## 2. 产品形态决定判断口径

如果对象是：

- `macro`

就更该看工艺兼容、外围成本、系统潜力。

如果对象是：

- `card / system`

就更该看 host 协同、软件接入、部署摩擦和客户价值。

## 3. 供应链主导权会强烈影响路线成败

在 `HBM / GDDR-PIM` 这类路线里，主导权往往天然偏向 `memory vendor`。

在 `analog CIM startup` 这类路线里，真正难的是：

- 设计之外的制造、测试、验证与交付链

## 读到新公司时，建议按这张表补字段

- 角色
- 技术路线
- 产品形态
- 主要卖点
- 目标场景
- 软件依赖
- 供应链依赖
- 成熟度层级
- 主要风险

## 一个最实用的判断原则

如果一个对象：

- 讲的是很新的技术路线
- 给的是很强的峰值指标
- 但没有说清楚产品形态、软件接入、供应链依赖和当前成熟度

那么它大概率更适合放进“技术观察名单”，而不是“可部署产品名单”。

## 后续可补充内容

- 增加更多 startup / memory vendor / system company 对象
- 增加时间维度，形成路线演化表
- 增加按 `edge / auto / data center` 的场景横评
