# 代工厂版图:TSMC/Intel/Samsung

上级:[产业地图](README.md)
相关:[全球产业链全景图](industry-chain-overview.md), [OSAT 版图](osat-landscape-ase-amkor-jcet-tongfu.md), [大陆 vs 台积电](mainland-china-vs-tsmc-real-gap.md)

## 这页在回答什么问题

TSMC、Intel、Samsung 在先进封装中的位置分别是什么，它们为什么不能只按“封装厂”理解，而要看先进逻辑、封装平台、设计生态和客户导入的组合。

## 厂商平台与证据

| 厂商及对象 | 公开结构与时间 | 证据边界 |
| --- | --- | --- |
| TSMC CoWoS-S / SoIC | [2025 年报](https://investor.tsmc.com/static/annualReports/2025/english/pdf/2025_tsmc_ar_e_ch5.pdf)称 CoWoS-S 使用 silicon interposer；SoIC 为 3D 芯片堆叠平台 | 厂商平台与生产阶段表述；具体客户产品、良率及交付量另查 |
| Intel EMIB / Foveros-S / R / Direct | [Intel 封装页](https://www.intel.com/content/www/us/en/foundry/packaging.html)，核阅 2026-11-09：EMIB 用局部硅桥；Foveros-S 用硅 interposer；R 用 RDL interposer；Direct 在 active base 上采用 Cu-Cu hybrid bonding | Intel 将 Foveros-R 的 2027 可生产列为规划；不能把它当作既有出货 |
| Samsung I-Cube4 | [2021-05-06 公告](https://news.samsung.com/global/samsung-electronics-announces-availability-of-its-next-generation-2-5d-integration-solution-i-cube4-for-high-performance-applications)描述一颗逻辑 die 与四个 HBM 在硅中介层集成 | 仅支持该日期和实例；其他 I-Cube/H-Cube/X-Cube 变体需独立查证 |

平台名称覆盖多个配置和不同阶段。比较时应固定具体产品、水平与垂直接口、载体、工艺版本、测试和供货时间，不能以家族名称直接推导客户良率或性能。

## 一句话理解

TSMC、Intel、Samsung 的先进封装竞争不是单个 package 名词竞争，而是先进逻辑、2.5D/3D 平台、HBM 协同、设计生态和量产导入的系统能力竞争。

## 架构师启示

架构师选平台时，应把平台名翻译成结构能力：全局 interposer、局部 bridge、RDL interposer、3D hybrid bonding、HBM 协同和测试支持。不同 foundry 的平台组合会改变 chiplet 切分、NoC 形态、热路径和良率策略。
