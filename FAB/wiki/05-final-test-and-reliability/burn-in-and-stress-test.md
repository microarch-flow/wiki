# Burn-in 与应力测试

上级:[终测与可靠性](README.md)
相关:[Final Test 的方法与流程](final-test-methodology.md), [热路径管理](../06-cross-cutting-engineering/thermal-path-and-management.md), [应力、Warpage 与 CTE](../06-cross-cutting-engineering/stress-warpage-cte.md)

## 这页在回答什么问题

Burn-in 和 stress test 为什么要把芯片放到更严苛的温度、电压、功耗或循环条件下，它们如何帮助提前暴露早期失效和可靠性风险。

## Burn-in 的目的

Burn-in 的核心是筛出早期失效。某些缺陷在常温短时间功能测试中不明显，但在高温、偏压、动态负载或较长运行时间下会被加速暴露。

```text
latent defect
  -> accelerated condition
  -> early failure
  -> screened before shipment
```

它不是为了证明芯片在极端条件下性能更强，而是为了避免潜在缺陷进入客户使用阶段。

## Stress test 的范围

Stress test 覆盖更广的应力条件，用来验证产品是否能承受目标环境和寿命要求。

| 应力类型 | 可能暴露的问题 |
| --- | --- |
| 高温 | 漏电、老化、热失控、材料退化 |
| 低温 | 材料收缩、接触异常、时序 margin |
| 温度循环 | bump fatigue、delamination、warpage |
| 高电压/偏压 | 介质可靠性、漏电、击穿风险 |
| 动态功耗 | PI droop、热点、功能不稳定 |
| 湿度相关应力 | 界面、腐蚀、封装防护弱点 |

不同产品会选择不同组合，目标是覆盖真实使用和加速寿命风险。

## 为什么先进封装更需要 stress

先进封装里的高风险对象不是单一晶体管。RDL、micro-bump、TSV、underfill、mold、bonding interface、substrate 都会在温度和机械载荷下发生响应。热循环可以把 CTE mismatch 转化为疲劳、裂纹和界面剥离。

```text
temperature cycle
  -> material expansion mismatch
  -> stress accumulation
  -> fatigue / crack / delamination
```

2.5D 大 package 和 3DIC thin die 对这些问题更敏感。

## Burn-in 与 Final Test 的关系

Final Test 主要判断当前成品是否满足功能、电性和性能要求。Burn-in/stress test 则试图提前暴露潜在缺陷和寿命风险。它们的目标不同，常共同构成 screening 和 qualification 策略。

| 测试 | 关注点 |
| --- | --- |
| Final Test | 当下是否可交付 |
| Burn-in | 潜在早期失效是否会冒出 |
| Stress / reliability test | 是否能承受目标寿命与环境 |

## 代价与风险

Burn-in 和 stress test 会消耗时间、设备和能耗，也可能对产品引入额外应力。因此它们需要根据产品价值、风险等级和失效模式设计，而不是盲目加严。高价值 AI/HPC package 和车规/高可靠产品会更重视这类验证。

## 一句话理解

Burn-in 和 stress test 用加速条件把潜在缺陷提前暴露出来，目标是筛早期失效、验证寿命风险，而不是替代功能测试。

## 架构师启示

架构师定义高功耗、多 die 或 3DIC 产品时，要预判哪些应力最可能暴露问题：热循环、动态电流、HBM 邻近热耦合、bump fatigue 或 bonding interface。可靠性测试策略应从这些架构风险反推，而不是最后套模板。
