# 封装如何进入芯片项目

<span class="micro-legacy-anchor" id="packaging"></span>

## 前置知识

先了解产品的带宽、I/O、供电、热和成本目标。封装结构与键合方式见 [FAB 封装与多芯粒集成](../../FAB/wiki/04-back-end-packaging/README.md)。

<span class="micro-legacy-anchor" id="典型场景"></span>

## 核心概念

封装把裸片、载体和板级系统连接起来。架构与封装团队应在布局早期对齐接口，因为裸片边界的位置、引脚和供电会进入物理实现。项目封装需要同时约束板卡、测试、热机械条件和生产路线。 [OCP 芯粒协同设计流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 常见封装类型

BGA 描述板侧焊球阵列。Flip-chip 描述裸片连接方式。硅中介层、RDL、局部硅桥和垂直键合描述封装内部的不同结构。同一产品可同时具备多个描述。具体分类、结构与候选边界由 [FAB 封装分类](../../FAB/wiki/04-back-end-packaging/packaging-taxonomy.md)说明。

<span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

| 何时 | 责任方共同确认 | 产物 |
| --- | --- | --- |
| 架构选择 | 系统、封装、物理、采购 | 目标带宽、供电、热、制造候选及依赖 |
| 布局前后 | 封装、版图、板卡、IP、测试 | 带坐标和版本的引脚／凸点图、供电及热边界、测试访问 |
| 流片签核 | 设计、封装、测试和供应方 | 可组装的裸片及载体版本，约定的检查、筛测及交接条件 |
| 工程样品 | 封装、测试、硅后与质量 | 工程样件、批次关系、组装记录、终测条件和已知限制 |

封装、板卡、测试夹具和固件准备可以并行。若 I/O 或凸点接口发生变化，先评估受影响的版图、基板、板卡、测试和资格鉴定。

<span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

接口冻结前，检查实际载体的通道、热路径和供电条件。温度升高可缩小工作裕量。若系统有温度驱动的节流，应验证传感器、阈值、动作及测量结果。外部封装和测试团队要确认哪些内容可在组装前检查，哪些只能在组装后得到。 [封装供电](../../FAB/wiki/06-cross-cutting-engineering/power-delivery-pi-pdn-decap.md) · [封装热路径](../../FAB/wiki/06-cross-cutting-engineering/thermal-path-and-management.md)

## 常见坑

同一张引脚图中，裸片、基板、板卡或测试夹具可能采用不同坐标方向。交接应明确对象、单位、原点、视角、镜像规则以及版本。以一组关键电源脚、参考地和测试脚作端到端对照。

<span class="micro-legacy-anchor" id="工具和设备"></span>

## 成本视角

把基板、裸片或堆栈、试制、组装、测试、工装和报废分开。多裸片方案要按采购、筛选、组装和终测的对象分别估算。 [跨阶段良率与成本](../../FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages.md)

## 后续阅读

- [FAB 封装与多芯粒集成](../../FAB/wiki/04-back-end-packaging/README.md)
- [成品终测](../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)
- [首硅启动](04_post_silicon_bringup.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 设计、封装、板卡和测试协同的接口可参考 OCP 多芯粒资料。
- **行业做法。** 表中冻结点及责任划分为示例。
- **待项目核实。** 实际载体、规格、测试访问、散热器及可供应批量。
