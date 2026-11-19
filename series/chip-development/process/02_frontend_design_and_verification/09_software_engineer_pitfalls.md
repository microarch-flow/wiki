# 软件背景工程师怎样审查 RTL

<span class="micro-legacy-anchor" id="软件背景人在前端容易踩的坑"></span>

## 前置知识

先读 [RTL 设计工程实践](01_rtl_design_practices.md)。项目层面的取舍见[软件背景创始人导读](../07_for_software_background_founders/README.md)。

## 典型场景

**教学假设。** 仿真中一个 DMA 请求能跑完。若目的端突然撤回 ready，发送端仍需保持有效载荷。此外还要定义复位取消、缓存占用和完成事件怎样跨域。用两个先后到达的请求、一段背压和一次复位做对照。

<span class="micro-legacy-anchor" id="坑-1把-rtl-当并发软件"></span><span class="micro-legacy-anchor" id="坑-2相信-c-model-等于硬件规格"></span><span class="micro-legacy-anchor" id="坑-3过度相信-agent-生成-rtl"></span><span class="micro-legacy-anchor" id="坑-4把仿真通过当完成"></span><span class="micro-legacy-anchor" id="坑-5低估-reset-和-x"></span><span class="micro-legacy-anchor" id="坑-6不尊重-clock-domain"></span><span class="micro-legacy-anchor" id="坑-7忽视-dft-和量产测试"></span><span class="micro-legacy-anchor" id="坑-8把性能指标写成峰值"></span><span class="micro-legacy-anchor" id="坑-9把参数化当复用"></span><span class="micro-legacy-anchor" id="坑-10低估工具和流程"></span><span class="micro-legacy-anchor" id="给-biao-的行动建议"></span>

## 工程检查

| 检查 | 要问的问题 | 正文 |
| --- | --- | --- |
| 状态与时钟 | 哪些数据跨拍保存，哪条路径必须在一拍内完成？ | [微架构设计](02_microarchitecture_design.md) |
| 协议与资源 | 背压时输入和状态如何保持？访问能否被端口接受？ | [RTL 设计](01_rtl_design_practices.md) |
| 复位与跨域 | 复位时有哪些事务被取消？事件太密时是否会丢？ | [CDC 与 RDC](06_cdc_and_rdc.md) |
| 数值与模型 | 位宽、舍入、截断、溢出和非法输入的判据来自哪里？ | [功能验证](03_verification_methodology.md) |
| 综合与测试 | 综合能否映射预期结构？是否留出测试模式和访问？ | [综合准备需要哪些输入与检查](04_synthesis_preparation.md) · [DFT](05_dft_introduction.md) |
| 生成和参数化 | 允许哪些配置，哪些经过回归，如何重现结果？ | [前端交接评审](08_signoff_criteria.md) |

## 后续阅读

- [项目评审的常见误区](../07_for_software_background_founders/01_common_misconceptions.md)
- [EDA 工具版图](../06_cross_cutting_topics/01_eda_tools_landscape.md)

<span class="micro-legacy-anchor" id="角色节奏成本与接口"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **工程建议。** 检查表用于发现待验证假设，正式覆盖范围由项目定义。
- **教学假设。** DMA 场景只是一个最小接口反例。
