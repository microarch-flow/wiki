# 开发流程导读与术语

<span class="micro-legacy-anchor" id="00_overview芯片开发流程总览"></span>这组文章从设计公司的角度回答三个问题。产品怎样从需求变成可交接的设计？哪个角色负责确认结果？制造和交付的成本怎样形成？

<span class="micro-legacy-anchor" id="前置知识"></span>

## 本目录的作用

先读[芯片开发生命周期](01_full_lifecycle.md)，理解设计、制造和量产之间的依赖。遇到「前端」和「后端」时，先确认上下文。逻辑前端包括 RTL 设计和功能验证。物理设计后端负责从网表到版图的实现。制造语境的晶圆前道和封装后道另有自己的对象和工序。 [FAB 前道与后道](../../FAB/wiki/01-overview/front-end-vs-back-end.md)

<span class="micro-legacy-anchor" id="本目录文件索引"></span><span class="micro-legacy-anchor" id="芯片开发总流程图"></span><span class="micro-legacy-anchor" id="推荐阅读方式"></span><span class="micro-legacy-anchor" id="本目录不会做什么"></span><span class="micro-legacy-anchor" id="软件背景创始人的核心提醒"></span><span class="micro-legacy-anchor" id="典型场景"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 阅读顺序

1. [芯片开发生命周期](01_full_lifecycle.md)沿规格、签核和首硅串起交接。
2. [各角色和团队职责](02_roles_and_teams.md)查谁提供证据、谁接收和评审。
3. [芯片项目成本结构](03_cost_structure.md)核对投入、分档和交付的分母。
4. [小团队怎样组织芯片项目](04_startup_vs_bigcompany.md)按复杂度和团队能力安排职责。
5. [开发流程术语表](05_glossary.md)用于按名词查阅。

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法**以典型数字 ASIC/SoC 为背景。项目所需的交接物和放行判据由产品范围、合同和制造流程确定。
- **阅读路线**按读者问题编排。工艺、封装和测试机制详见 [FAB 导读](../../FAB/wiki/README.md)。
