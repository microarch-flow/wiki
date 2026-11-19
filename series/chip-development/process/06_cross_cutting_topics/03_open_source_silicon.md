# 开放芯片与开放 PDK 的使用边界

<span class="micro-legacy-anchor" id="open-source-silicon开源芯片策略"></span><span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="典型场景"></span>

## 核心概念

开放设计可以提供 RTL、验证、工具、固件、板卡或文档的一部分。工艺数据和配套 IP 另有版本、使用条件和覆盖范围。评估时分别检查设计文件、依赖、工艺支持、可复现工具流和制造服务。

## 开源范围分层

| 对象 | 核对内容 |
| --- | --- |
| RTL 和验证资产 | 版本、顶层、复现脚本、授权、专有 IP 的可访问性 |
| EDA 工具流 | 可用步骤、版本、工具依赖、库和规则 |
| 开放 PDK | 器件模型、规则、层和已验证的库，发布状态和工艺范围 |
| 实物反馈 | 试片或量产采用的工艺、封装、样件、已知工作条件及供应方 |

SkyWater 的 SKY130 社区版文档将当前发布定位为实验性预览，并说明商用制程和开放发布版本的适用范围。IHP 同样单独描述开放 PDK 的 alpha 发布及其商业 PDK。两者可作为核对「工艺存在」与「具体开放套件覆盖什么」的案例。 [SkyWater PDK 发布状态](https://skywater-pdk.readthedocs.io/en/main/status.html) · [IHP 开放设计](https://www.ihp-microelectronics.com/services/research-and-prototyping-service/open-source-design-enablement)

<span class="micro-legacy-anchor" id="工具和生态"></span><span class="micro-legacy-anchor" id="角色周期和成本"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

1. 确定需要公开的对象及其依赖。
2. 固定相应版本和许可条件。由项目方核对第三方和制造资料的访问范围。
3. 用代表性设计复现 RTL、验证、版图生成和适用检查。
4. 需要样片时，确认具体 shuttle、支持的工艺、实际检查以及可测范围。
5. 公开说明实测、工具结果、教学示例和待复核项。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

试跑成功提供对应配置下的证据。商业目标继续查目标工艺认可的提交与量产条件。开源设计、第三方厂商和工艺服务的证据需要分别追溯。 [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html) · [MPW 多项目晶圆策略](04_mpw_shuttle_strategy.md)

## 后续阅读

- [EDA 工具版图](01_eda_tools_landscape.md)
- [代工接入与交接](02_foundry_relationships.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 两套开放 PDK 的状态和工艺范围以各自官方资料为准。
- **行业做法。** 将版本、许可、工具和验证范围逐项记录。
- **待项目核实。** 拟用版本、供应方接受条件、依赖许可及实际制造路径。
