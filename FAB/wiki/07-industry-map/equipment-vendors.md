# 设备厂商版图

上级:[产业地图](README.md)
相关:[材料供应链](materials-supply-chain.md), [TSV](../04-back-end-packaging/3d-routes/tsv-through-silicon-via.md), [Micro-bump vs Hybrid Bonding](../04-back-end-packaging/3d-routes/micro-bump-vs-hybrid-bonding.md)

## 这页在回答什么问题

先进封装设备链为什么关键，哪些设备决定 TSV、RDL、thin die、hybrid bonding、placement、test 和 reliability 的工艺窗口。

## 设备决定量产窗口

先进封装不是“原理可行”就能量产。它需要设备在高精度、高重复性、高吞吐下稳定运行，并和材料、recipe、计量和测试流程配合。

```text
process concept
  -> equipment precision
  -> repeatability
  -> yield and capacity
```

设备短板常表现为良率波动、对位窗口不足、薄 die 破损、RDL 一致性差或测试吞吐不足。

## 关键设备类别

| 类别 | 相关工艺 |
| --- | --- |
| Lithography / plating / dielectric tools | RDL build-up、fine line/space |
| Etch / deposition / Cu fill | TSV、via、barrier/seed |
| Grinding / CMP / dicing | wafer thinning、backside、singulation |
| Temporary bonding / debond | thin wafer and thin die handling |
| Die bonder / TCB | micro-bump、chiplet assembly |
| Hybrid bonding | Cu-Cu/dielectric direct bonding、3DIC |
| Inspection / metrology | overlay、void、warpage、defect detection |
| ATE / reliability | wafer sort、中测、final test、stress test |

## Hybrid bonding 设备

Hybrid bonding 要求表面平坦度、洁净度、对位精度和界面控制都很高。公开设备资料中，Besi 把 hybrid bonding 平台定位在高密度互连和 3D integration，强调洁净概念、光学对位、高精度和高吞吐。

这类设备不是单独决定路线成败，但它会决定高密度 3DIC 的量产窗口能不能稳定打开。

## 设备与材料的耦合

RDL 设备必须配合 dielectric、Cu plating、via 和清洗材料；bonding 设备必须配合表面处理、洁净度和对位标记；thin die handling 必须配合 temporary adhesive、carrier 和 debond 工艺。设备能力脱离材料体系没有意义。

## 一句话理解

先进封装设备把 TSV、RDL、thin die、micro-bump、hybrid bonding 和测试从实验可行变成稳定量产能力。

## 架构师启示

架构师看到某条封装路线时，要问设备窗口是否支撑目标 pitch、die size、stack height 和产能。若路线依赖 hybrid bonding 或超细 RDL，设备和计量能力会直接影响产品节奏。
