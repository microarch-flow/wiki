# 首硅怎样从上电走到最小事务

<span class="micro-legacy-anchor" id="post-silicon-bring-up"></span>

## 前置知识

准备与芯片版本匹配的样品、封装、板卡、固件和测试访问。核对引脚、时钟、复位、供电范围及限流方案。 [封装如何进入芯片项目](03_packaging.md)

## 核心概念

Bring-up 让样品进入可控、可观测、可运行的状态。每一步的输出都应能支持下一步或缩小故障范围。工程样品可以从实验室或 ATE 的基础检查开始，起点取决于产品和实际可用的测试访问。 [OpenTitan 硅后里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

## Bring-up 前准备

在样片返回前准备电源与复位检查、工装、启动软件、已知数据、样片和板卡记录。尽早在仿真或可获得的平台上验证可移植的测试。准备基础寄存器读取和目标接口测试，并说明测试访问何时可用。 [OpenTitan 顶层软件测试](https://opentitan.org/book/sw/device/tests/index.html)

## 典型顺序

| 步骤 | 通过证据 | 失败时隔离对象 |
| --- | --- | --- |
| 样品与板卡核对 | 裸片／封装、板卡、工装和配置版本可追溯 | 装配、短路、供电、配置 |
| 受控上电 | 按指定顺序观测电压、电流、时钟与复位 | 电源源端与负载端、时钟和复位 |
| 基础访问 | 工程配置下可读得到预期设备或寄存器状态 | 调试权限、strap、接口和启动 |
| 最小功能 | 固件走完事先定义的一条事务 | 存储、设备接口、时钟域和软件 |
| 记录结果 | 样品、输入、条件、观测和失败原因可复现 | 补齐可观测点，进入调试流程 |

JTAG、scan 和 MBIST 按芯片设计与测试模式使用。有些测试需要测试器或专用访问。有些系统在产品生命周期的不同状态中关闭部分接口。记录实际可用的状态。 [OpenTitan 设备配置流程示例](https://opentitan.org/book/doc/security/specs/device_provisioning/index.html)

<span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 典型场景

**教学假设。** 沿用[SRAM＋DMA 规格](../01_product_definition_and_architecture/02_spec_definition.md#典型场景)。先用控制域读取已知标识，再写入规定的源和目的参数。提交一笔 16 B 搬运。检查 SRAM 内容、DMA 状态和完成中断。如果数据正确而中断缺失，记录寄存器与事件，转入[硅后调试](05_post_silicon_debug.md)。

<span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本视角"></span>

## 上下游接口

交付启动步骤、样片和软件编号、通过项目、失败复现方法以及可使用的配置。后续按需要进入故障定位和系统测量。

## 后续阅读

- [硅后调试](05_post_silicon_debug.md)
- [硅片特性化](06_characterization.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** OpenTitan 公开了部分硅前可移植测试与硅后里程碑。
- **行业做法。** 基础检查顺序依据电源、时钟、访问和功能的依赖调整。
- **教学假设。** 16 B 搬运对应本文贯穿用例。
- **待项目核实。** 目标器件的工作条件、调试权限、启动顺序和设备接入。
