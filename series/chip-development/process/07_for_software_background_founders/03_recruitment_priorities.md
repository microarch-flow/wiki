# 团队责任与招聘顺序怎样决定

<span class="micro-legacy-anchor" id="recruitment-priorities创业初期招聘优先级"></span><span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="面试重点"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 招聘原则

先列项目中缺乏负责人的关键风险。人员数量与岗位顺序取决于产品、工艺、现有 IP、外包合同和团队能力。一个人可以担多项职责。评审、执行和风险接受需要在责任表中写清楚。

<span class="micro-legacy-anchor" id="第一优先级芯片工程总负责人"></span><span class="micro-legacy-anchor" id="第二优先级验证负责人"></span><span class="micro-legacy-anchor" id="第三优先级后端物理设计负责人或强外部顾问"></span><span class="micro-legacy-anchor" id="第四优先级dfttestproduct-engineering"></span><span class="micro-legacy-anchor" id="第五优先级系统软件编译器负责人"></span><span class="micro-legacy-anchor" id="第六优先级运营供应链质量"></span>

## 招聘顺序建议

| 首版目标 | 先确认的完整职责 | 需要怎样的成果 |
| --- | --- | --- |
| 小型数字试片 | RTL、基础 DV、工具流、工艺接入与硅后测量 | 可布线设计、可复现实验、样片与版本对应 |
| 面向客户的数字 SoC | 产品架构、前端验证、物理、测试、固件、质量和供应 | 规格到出货证据能追溯，失效有负责人 |
| 高速接口与多芯粒 | 封装、SI／PI、时钟电源、PHY、测试访问、供应路线 | 可制造接口和可追溯的多芯粒测试方案 |

项目可能优先补缺架构、DV、物理、量产测试或软件领域。比如核心架构已验证但依赖外购 PHY，需尽早有人负责 PHY 视图、封装与板卡、测试访问及接口验收。

## 分阶段招聘计划

从「当前关键决定」向后排到「何时需要证据」。执行可以由员工、顾问或服务商承担。项目内部明确签字、交付复核、变更和风险管理职责。实际项目工具和节点能力通过历史产物、当前合同或试任务核查。 [各角色和团队职责](../00_overview/02_roles_and_teams.md) · [设计服务与 Turnkey](../06_cross_cutting_topics/05_turnkey_services.md)

<span class="micro-legacy-anchor" id="成本和股权视角"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **工程建议。** 表格给出基于项目风险的责任设置。实际招聘或外包顺序取决于团队能力和项目边界。
- **待项目核实。** 人员能力与可用时间、合作范围、交付数据与批准权限。
