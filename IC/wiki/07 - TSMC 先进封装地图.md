# TSMC 先进封装地图

上级：[[00 - 先进封装 Wiki 索引]]

相关：[[04 - Si Interposer]]、[[05 - Fan-out RDL]]、[[06 - Embedded Bridge]]、[[08 - 3D IC]]、[[14 - 为什么台积电领先先进封装]]、[[18 - CoWoS-S、CoWoS-R、CoWoS-L 的真正差别]]

## 总图

可以把 TSMC 的先进封装/集成体系放到 3DFabric 框架下理解：

- SoIC：前端 3D silicon stacking
- CoWoS：2.5D / interposer 家族
- InFO：fan-out RDL 家族

## InFO

本质：

- TSMC 的 fan-out RDL 平台

主要分支：

- InFO-PoP
- InFO-oS

大方向上可理解为 chip-first 哲学，即 chips embedded before interconnection。

典型定位：

- mobile
- 薄型化
- 中高密度 chiplet 集成
- 某些 HPC / networking

## CoWoS

CoWoS = Chip on Wafer on Substrate。

共同点：

- 先形成中间互连平台
- 再把 chip 放到该平台上
- 再装到 substrate

大方向上可理解为 chip-last 平台级哲学。

## CoWoS-S

本质：

- silicon interposer 2.5D

特点：

- density 最高
- 很适合 logic + HBM
- 可集成 DTC/eDTC
- 成本高，面积扩展压力大

## CoWoS-R

本质：

- RDL interposer 2.5D

特点：

- 更偏 RDL-based 大面积扩展
- 成本和机械顺从性通常优于 full Si interposer
- 局部极限密度不如 CoWoS-S

## CoWoS-L

本质：

- RDL interposer + LSI

注意：

LSI 在这里指 Local Silicon Interconnect，不是泛义上的“大规模集成”。

可以把它理解成：

- 全局用 RDL interposer 扩尺寸、控成本
- 局部用硅互连单元提高 D2D 高密度连接能力

它的技术本质接近 [[06 - Embedded Bridge]]。

## SoIC

本质：

- TSMC 的真正 3D IC 路线

关键点：

- 属于前端 wafer-level 3DIC platform
- 支持 CoW 与 WoW
- 支持 Face-to-Back / Face-to-Face 等结构
- SoIC 集成后的芯粒还可再进入 CoWoS / InFO 做更大系统
