# 失效模式：RDL Cracking

上级：[[48 - 失效模式层：先进封装常见失效总览]]

相关：[[05 - Fan-out RDL]]、[[26 - RDL 的截面结构和制造流程]]、[[43 - 工艺深水区：RDL]]

## 这是什么

RDL cracking 指的是：

- RDL 金属线本体开裂
- RDL 邻近介质层开裂
- via / trace 交界处出现裂纹

它是 advanced packaging 里非常典型的一类失效，尤其常见于：

- Fan-out / RDL
- 大尺寸多层 build-up 平台
- 高应力 heterogeneous package

## 为什么会发生

核心原因通常不是单一电问题，而是热机械问题累积：

- 多层 RDL build-up 带来应力
- polymer / Cu / die / mold 的热膨胀不一致
- 大尺寸封装 warpage
- 热循环导致疲劳

一句话：

`RDL cracking 往往是“细线 + 多层 + 热机械应力”共同作用的结果。`

## 最容易出问题的地方

- line 转角
- via 附近
- 不同材料界面邻近区域
- 高应力集中区

## 哪些路线更怕它

### Fan-out / RDL

最典型。因为：

- 平台本体就依赖多层 RDL
- 材料体系更复杂
- 大尺寸时更容易叠加应力

### CoWoS-R / CoWoS-L

也很相关，因为这两条路线同样把 RDL 当核心平台能力。

## 工程上怎么理解它

如果系统要：

- 更细 line/space
- 更多层 RDL
- 更大 package

那么就要同时接受：

- cracking 风险上升
- 工艺窗口变窄
- 材料和应力控制变得更重要

## 它最常提醒你的事

当你看到某个平台大讲：

- fine-pitch RDL
- 大尺寸 fan-out
- 大型异构 package

你就应该立刻想到：

`RDL cracking 和相关可靠性会不会成为瓶颈？`

