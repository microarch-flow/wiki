# 量产良率分析怎样找到损失来源

<span class="micro-legacy-anchor" id="yield-analysis"></span>

## 前置知识

良率的分母和缺陷模型见 [FAB 良率与缺陷密度](../../FAB/wiki/03-wafer-test-and-cp/yield-and-defect-density.md)。跨阶段成本见 [FAB 良率经济学](../../FAB/wiki/06-cross-cutting-engineering/yield-economics-across-stages.md)。

## 核心概念

产品工程用分阶段数据定位损失。报告应定义投入对象、通过判据、分档、复测处理和时间窗。晶圆 CP、组装与终测的对象不同。客户现场事件应关联出货批次与观察期，单列退货率或失效率。

## 良率影响因素

真实缺陷、设计裕量、封装损伤、测试错误和过严限值都可能造成下档或淘汰。同一个 fail bin 也可能来自多个原因。利用晶圆图、设备与批次关联、对照测试和失效分析逐步排除。

## Yield Learning Flow

1. 接收晶圆图、CP 和终测测试日志、组装批号与测试条件。
2. 按批次、版次、环境、工装和失败项统计。先检查数据缺失、条件变化或并测导致的假差异。
3. 比较同批不同位置、不同组装批次或版本。将可疑样品和已知良品一同用于复验。
4. 从测试和路径诊断找到候选根因，再用工艺、封装、版图或物理分析复核。
5. 验证改动前后的失败分布、过杀、良品与逃逸。更新规则、工艺、测试或设计。

<span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 典型场景

**教学假设。** 一批同版裸片 CP 正常，终测中某一组装批次大量出现 I/O 失败。先核对测试程序和接触。若失败随组装批次出现，检查组装状态、组装前后同类信号的覆盖，并选样做失效分析。仅凭相关性无法确认是基板、焊点或线材。确认原因后按[量产变更](../05_production_and_lifecycle/03_supply_chain.md)管理。

<span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本视角"></span>

## 上下游接口

输出包括采用同一口径的趋势、经复验的根因、在途风险、处置批次及复测结果。追溯必须从晶圆裸片关联到封装产品和测试条件。剩余风险回到量产放行或硅版本修订。 [FAB 失效分析](../../FAB/wiki/05-final-test-and-reliability/failure-analysis-flow.md) · [OCP 芯粒测试流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 后续阅读

- [量产爬坡](../05_production_and_lifecycle/02_volume_ramp.md)
- [现场支持与退货分析](../05_production_and_lifecycle/04_field_support.md)
- [硅版本修订](08_silicon_revision.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 数据关联、对照复测与失效分析支持定位。统计分析需明确同一总体和测量条件。
- **教学假设。** 组装批次案例仅给出调查步骤。
- **待项目核实。** 供应商数据完整性、测试覆盖、分档及具体失效机制。
