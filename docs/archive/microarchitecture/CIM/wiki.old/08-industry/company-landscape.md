# 公司与路线图谱

## 这一页的作用

这一页不是简单罗列公司名，而是帮助把不同路线放进同一张产业地图里，避免把：

- 器件研究团队
- 存储厂商
- 芯片创业公司
- 系统集成商

混成一类对象来比较。

## 建议分类方式

- SRAM-CIM 公司
- ReRAM-CIM 公司
- DRAM / HBM-PIM 路线
- Flash-CIM 路线
- 学术 spin-off
- memory vendor 主导路线

## 更实用的分类框架

### 按技术路线

| 类别 | 代表问题 | 关注点 |
| --- | --- | --- |
| SRAM-CIM | 如何与 SoC 深度集成 | 工艺兼容、片上面积、推理能效 |
| ReRAM-CIM | 如何把阵列潜力变成可用产品 | 精度、校准、可靠性、量产 |
| DRAM / HBM-PIM | 如何减少大工作集的数据搬运 | 带宽利用率、host 协同、接口 |
| Flash-CIM | 如何做超低功耗固定模型推理 | 待机功耗、成本、端侧场景 |

### 按公司角色

| 角色 | 典型形态 | 关注点 |
| --- | --- | --- |
| Memory vendor | HBM / DRAM / GDDR memory-side 路线 | 能否扩展现有内存产品线 |
| Chip startup | 专用加速器或边缘芯片 | 场景切入、差异化、软件栈 |
| Academic spin-off | 从论文到样片再到产品 | 技术成熟度、供应链能力 |
| System / product company | 把 CIM 嵌入终端产品 | 成本、功耗、用户场景闭环 |

## 当前可以先挂的代表性样板

### Memory vendor 主导路线

- [Samsung HBM-PIM](../09-research/case-studies/samsung-hbm-pim.md)
- [Samsung HBM / HBM-PIM 公司卡片](./company-cards/samsung-hbm-pim.md)

判断重点：

- 它证明的是 system-level 的 memory-side 价值
- 不是阵列级 analog CIM 的直接代表

### CMOS-compatible 研究路线

- [TSMC 16nm CIM Macro](../09-research/case-studies/tsmc-16nm-cim-macro.md)

判断重点：

- 它代表了先进工艺下 SRAM / CMOS-friendly 路线的研究吸引力
- 更适合拿来理解片上宏设计，不应直接等同于成熟产品

### ReRAM-CIM 研究路线

- [东京大学 ReRAM-CiM](../09-research/case-studies/u-tokyo-reram-cim.md)

判断重点：

- 它代表的是阵列潜力和可靠性挑战并存的路线
- 更适合作为研究与产品落地之间张力的观察对象

### GDDR / AiM 产品化路线

- [SK hynix GDDR6-AiM / AiMX 公司卡片](./company-cards/sk-hynix-gddr6-aim-aimx.md)

判断重点：

- 它展示了 memory vendor 如何从 memory device 往 AI accelerator card 延伸
- 更适合放在 `PIM / solution` 而不是纯器件路线里

### Analog CIM startup 路线

- [Mythic Analog Compute-in-Memory 公司卡片](./company-cards/mythic-analog-cim.md)

判断重点：

- 它代表的是 startup 主导的 analog CIM 商业化尝试
- 适合观察“技术叙事”和“工程现实”之间的距离

## 每家公司建议统一记录

- 技术路线
- 产品形态
- 目标场景
- 指标口径
- 量产阶段
- 主要风险

## 建议增加的统一字段

- 公司角色：memory vendor / startup / spin-off / product company
- 主要卖点：能效 / 带宽 / 容量 / 待机功耗 / 集成性
- 目标客户：edge / wearable / auto / data center / HPC
- 软件依赖：compiler / runtime / model conversion
- 供应链依赖：foundry / memory / packaging / test

## 做路线图谱时最容易犯的错误

### 把不同层级的对象直接横比

例如把：

- 一个 `macro` 研究结果
- 一颗边缘芯片
- 一个 HBM-PIM 内存产品

放进同一张性能表直接比较，这通常没有意义。

### 把技术路线当成商业路线

技术可行不等于商业可行。必须再问：

- 谁来买
- 为什么现在买
- 要改多少现有系统

### 只看峰值指标

更应该看：

- 指标层级
- 场景匹配度
- 供应链复杂度
- 软件和客户验证成本

## 后续建议扩展成的结构

- 公司列表
- 时间线
- 路线-场景二维矩阵
- 同路线竞品比较

## 后续可补充内容

- 具体公司卡片
- 分年份路线演化
- 各路线成熟度标签
