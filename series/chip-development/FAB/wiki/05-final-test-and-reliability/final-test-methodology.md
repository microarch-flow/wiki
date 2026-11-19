# 成品终测怎样筛选与分档

<span class="micro-legacy-anchor" id="final-test-的方法与流程"></span>

上级：[成品终测与可靠性](README.md)
相关：[晶圆筛测与 CP](../03-wafer-test-and-cp/README.md) · [KGD 的筛选判据与残余风险](../03-wafer-test-and-cp/kgd-known-good-die.md)

<span class="micro-legacy-anchor" id="为什么先进封装更难测"></span><span class="micro-legacy-anchor" id="测试成本与覆盖率"></span>

## 这页在回答什么问题

封装后的生产测试携带哪些输入，按什么条件决定器件通过与档位，又有哪些测试仍需在其他阶段完成？

<span class="micro-legacy-anchor" id="final-test-的位置"></span>

## Final Test 测什么

生产测试按目标产品和配置选择电性、结构、存储、功能、速度、功耗、接口和分档。具体条件受封装引脚、测试模式、温度、测试设备、工装和允许时间限制。芯粒组装后可以重测有访问能力的内部裸片，并检查装配后的 D2D 连接。 [OCP 多芯粒测试流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 典型流程

1. 接收可追溯的封装件，确认版本、工装、程序及限值。
2. 按计划建立测试条件并检查接触、供电和基础电性。
3. 执行向量与功能测试，按条件测速度、功耗或接口。
4. 依据测试结果分档。记录失败项目、复测、批号及设备和程序版本。
5. 按质量规则隔离异常。将结果反馈给产品工程和失效分析。

产品数据手册与特性化提供范围与保护裕量依据。测试程序选择在产线能够稳定测量的量，并验证对目标规格的筛选能力。若限值、工装或程序变化，对照样件重跑，检查良品淘汰、漏检和分档转移。 [硅片特性化](../../../process/04_tapeout_and_post_silicon/06_characterization.md)

<span class="micro-legacy-anchor" id="与-cpkgd-的关系"></span>

## 和 CP、KGD 的关系

| 位置 | 对象 | 结果 |
| --- | --- | --- |
| 晶圆筛测 | 晶圆上的裸片 | 初筛、分档、晶圆图 |
| 接收和中间测试 | 已筛裸片、堆栈或子装配体 | 指定条件下可进入下一工序 |
| 成品终测 | 已封装器件 | 按生产条件给出通过、失败和档位 |
| 资格鉴定 | 代表性样本或配置 | 按应力、样本与判据评价可靠性证据 |

系统级测试可另行验证板级或产品使用情形。对每一阶段记录测试对象、实际条件与覆盖。 [项目放行](../../../process/05_production_and_lifecycle/01_qualification_and_reliability.md)

<span class="micro-legacy-anchor" id="架构师启示"></span>

## 一句话理解

终测确定指定条件下的成品分档与放行记录。晶圆筛测和中间测试减少昂贵工序中的损失。三者的统计分母随对象变化。
