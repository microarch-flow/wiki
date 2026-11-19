# RTL 设计与集成

<span class="micro-legacy-anchor" id="02_frontend_design_and_verification前端设计与验证"></span>逻辑前端把体系结构细化成可综合的硬件。主要输入是有版本的规格、IP、时钟和复位要求、综合与物理预算。主要输出是 RTL、约束、验证证据和设计交付包。

<span class="micro-legacy-anchor" id="前置知识"></span>

## 本目录的作用

先确定时序、状态和硬件资源，再写 RTL。设计与验证并行推进。低功耗、跨域、可测性和物理约束随集成反馈逐步确认。功能、时序和制造测试各有具体判据。 [OpenTitan 开发阶段](https://opentitan.org/book/doc/project_governance/development_stages.html)

<span class="micro-legacy-anchor" id="文件索引"></span><span class="micro-legacy-anchor" id="前端主流程"></span><span class="micro-legacy-anchor" id="关键交付物"></span><span class="micro-legacy-anchor" id="角色分工"></span><span class="micro-legacy-anchor" id="典型场景"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 阅读顺序

1. [微架构设计](02_microarchitecture_design.md)规定资源、流水线、状态和接口。
2. [RTL 设计工程实践](01_rtl_design_practices.md)把行为变成寄存器、组合逻辑和握手。
3. [功能验证](03_verification_methodology.md)追踪需求和检查证据。
4. [CDC 与 RDC](06_cdc_and_rdc.md)审查跨时钟域和复位域的交互。
5. [低功耗设计](07_low_power_design.md)定义电源状态、切换协议与边界单元。
6. [综合准备](04_synthesis_preparation.md)检查映射、约束和等价验证的输入。
7. [DFT 与制造测试](05_dft_introduction.md)确定可测结构及测试约束。
8. [前端交接评审](08_signoff_criteria.md)评审下游基线。
9. [软件背景工程师常见误区](09_software_engineer_pitfalls.md)按设计检查项回顾典型问题。

## 相关专题

- [物理设计与签核](../03_backend_physical_design/README.md)给出实现反馈、最终版图和签核证据。

<span class="micro-legacy-anchor" id="创业公司视角"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 章节按常见数字项目的交付对象组织。正式交接点和检查范围以项目规则为准。
