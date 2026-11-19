# MPW 怎样用一批样片验证局部风险

<span class="micro-legacy-anchor" id="mpw-shuttle-strategympw-多项目晶圆策略"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

MPW（多项目晶圆）让多项设计共享制版和晶圆。它可降低单项目的制版投入，并提供指定工艺的实物反馈。项目应先定义要关闭的风险，再选择能测到它的样片、工装和验证方式。 [TSMC CyberShuttle](https://www.tsmc.com/english/dedicatedFoundry/services/cyberShuttle)

## 适合 MPW 的内容

示例目标包括验证 SRAM wrapper 和 MBIST、局部 DMA 或计算通路、时钟复位方案、特定 PHY 或模拟电路。前提是相应 IP、测试模式、封装、板卡与设备可用。若问题依赖整机热、复杂封装、完整接口或多个量产批次，应确认 MPW 能覆盖哪一部分，并规划补充验证。

<span class="micro-legacy-anchor" id="工具角色和成本"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

1. 写出假设、测量对象、通过条件和能区分失败原因的观测。
2. 查具体 shuttle 的工艺及 PDK 版本、入场资格、面积、I/O、提交日期、样片数量、封装和测试选项。
3. 设计测试载体。为目标功能准备时钟、观测与控制路径。
4. 提交和接收样片后，按版本执行计划。将数据回写到下一次设计决策。
5. 若样片与最终产品的库、封装或边界不同，记录可以迁移的结论及未来需要复验的条件。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

FPGA 或仿真便于反复验证软件与功能。指定工艺的 MPW 样片可测硅层面的局部行为。两者对真实产品的约束不同。使用 MPW 时重点识别测试权限、样品数、可用频率、电源边界和实际封装。 [IHP 开放设计与 MPW](https://www.ihp-microelectronics.com/services/research-and-prototyping-service/open-source-design-enablement)

## 典型场景

**教学假设。** 目标是验证 SRAM＋DMA 在选定开放工艺中的单事务路径。测试片包含可读写的配置、16 B 搬运与 MBIST 访问。预先记录允许频率和每项测量条件。样品能验证该工艺、封装以及限制范围内的行为。迁到其他节点或扩大产品并发时，应补充验证。

## 参考公开来源

- [ChipFoundry 现行 chipIgnite 服务](https://chipfoundry.io/chipignite)
- [ChipFoundry 关于 Efabless 资产收购的公告](https://chipfoundry.io/efabless)
- [Tiny Tapeout 已发布的期次和估计时间](https://tinytapeout.com/chips/)
- [TSMC CyberShuttle](https://www.tsmc.com/english/dedicatedFoundry/services/cyberShuttle)

## 后续阅读

- [开放芯片与开放 PDK](03_open_source_silicon.md)
- [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [第一颗芯片的范围](../07_for_software_background_founders/04_first_chip_pragmatics.md)

## 内容可信度说明

- **公开事实。** 多项目共享制版的方式与所列服务由供应方披露。
- **教学假设。** 16 B 的例子用于说明测试载体如何绑定验收目标。
- **待项目核实。** 适用期次、资格、工艺、面积、报价、封装、设备和交期。
