# 术语表

上级:[参考资料](README.md)
相关:[分类框架](../01-overview/taxonomy.md), [封装分类](../04-back-end-packaging/packaging-taxonomy.md), [关键指标速查表](key-metrics-table.md)

## 这页在回答什么问题

芯片制造与先进封装里常见缩写和术语分别是什么意思，应该回到哪些章节继续理解。

## 产业角色

| 术语 | 含义 | 继续阅读 |
| --- | --- | --- |
| Fabless | 无晶圆厂芯片设计公司 | [产业地图](../07-industry-map/README.md) |
| Foundry | 晶圆代工厂 | [Foundry 版图](../07-industry-map/foundry-landscape-tsmc-intel-samsung.md) |
| IDM | Integrated Device Manufacturer，设计制造一体厂 | [Foundry 版图](../07-industry-map/foundry-landscape-tsmc-intel-samsung.md) |
| OSAT | Outsourced Semiconductor Assembly and Test，外包封装测试 | [OSAT 版图](../07-industry-map/osat-landscape-ase-amkor-jcet-tongfu.md) |

## 制造对象

| 术语 | 含义 | 继续阅读 |
| --- | --- | --- |
| Wafer | 晶圆，前道制造的圆片载体 | [晶圆](../02-front-end-fabrication/wafer-the-substrate.md) |
| Die | 从 wafer 切割出的裸芯片 | [从晶圆到产品](../01-overview/from-wafer-to-product.md) |
| KGD | Known Good Die，经过筛选的已知良品裸 die | [KGD](../03-wafer-test-and-cp/kgd-known-good-die.md) |
| Package | 封装后的芯片产品形态 | [后道封装](../04-back-end-packaging/README.md) |
| Substrate | 封装基板，连接 package module 与 board | [基板与载板](../04-back-end-packaging/key-components/substrate-and-carrier.md) |
| Carrier | 制程中的临时承载平台 | [基板与载板](../04-back-end-packaging/key-components/substrate-and-carrier.md) |

## 封装路线

| 术语 | 含义 | 继续阅读 |
| --- | --- | --- |
| 2.5D | 多 die/HBM 横向集成在高密度中间层上 | [2.5D 路线](../04-back-end-packaging/2.5d-routes/README.md) |
| 3DIC | die 沿垂直方向堆叠并高密度互连 | [3D 路线](../04-back-end-packaging/3d-routes/README.md) |
| Si interposer | 硅中介层，高密度 routing + TSV 平台 | [Si Interposer](../04-back-end-packaging/2.5d-routes/si-interposer-fundamentals.md) |
| Fan-out / RDL | polymer/Cu 重布线封装平台 | [Fan-out RDL](../04-back-end-packaging/2.5d-routes/fan-out-rdl-overview.md) |
| Embedded bridge | 局部硅桥 + 外围 substrate/RDL 平台 | [Embedded Bridge](../04-back-end-packaging/2.5d-routes/embedded-bridge-emib-and-cowos-l.md) |

## 关键组件

| 术语 | 含义 | 继续阅读 |
| --- | --- | --- |
| RDL | Redistribution Layer，重布线层 | [RDL](../04-back-end-packaging/key-components/rdl-redistribution-layer.md) |
| TSV | Through-Silicon Via，硅通孔 | [TSV](../04-back-end-packaging/3d-routes/tsv-through-silicon-via.md) |
| Micro-bump | 微凸点连接 | [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md) |
| Hybrid bonding | Cu-Cu 与介质直接键合的高密度连接 | [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md) |
| Underfill | 填充连接间隙并分散应力的材料 | [Molding 与 Underfill](../04-back-end-packaging/key-components/molding-and-underfill.md) |
| Molding | 包覆和保护 die/RDL 结构的封装材料体系 | [Molding 与 Underfill](../04-back-end-packaging/key-components/molding-and-underfill.md) |

## 系统与可靠性

| 术语 | 含义 | 继续阅读 |
| --- | --- | --- |
| HBM | High Bandwidth Memory，高带宽 3D memory stack | [HBM 案例](../04-back-end-packaging/hbm-as-case-study/README.md) |
| PI | Power Integrity，供电完整性 | [PI/PDN/Decap](../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) |
| PDN | Power Delivery Network，供电网络 | [PI/PDN/Decap](../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) |
| Decap | Decoupling capacitor，去耦电容 | [PI/PDN/Decap](../06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) |
| SI | Signal Integrity，信号完整性 | [封装内 SI](../06-cross-cutting-engineering/signal-integrity-in-package.md) |
| CTE | Coefficient of Thermal Expansion，热膨胀系数 | [CTE/Warpage](../06-cross-cutting-engineering/stress-warpage-cte.md) |
| Warpage | 翘曲，热机械耦合导致的结构形变 | [CTE/Warpage](../06-cross-cutting-engineering/stress-warpage-cte.md) |

## 一句话理解

术语表的目标不是背缩写，而是把每个缩写放回制造对象、封装路线、系统约束和可靠性问题中理解。

## 架构师启示

架构师讨论封装方案时，要先统一术语边界。TSV、2.5D、3DIC、HBM、RDL、interposer 这些词如果混用，后续对带宽、热、PI、良率和产业链的判断都会偏。
