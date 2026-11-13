# 系统视角

<span id="这页在回答什么问题"></span>
<span id="从组件到系统访问路径"></span>
<span id="一句话理解"></span>

上级：[存储层级与数据路径](../README.md)

“系统基础”从工作负载和数据路径出发，介绍存储系统中的角色、取舍与复用。可以按下面的顺序阅读，也可以根据问题直接选择文章。

## 阅读顺序

1. [存储系统为何难设计](./problem-statement.md)：从一次读取出发，理解工作负载、共享资源和设计约束如何相互影响。
2. [RAM 分类与命名](./taxonomy.md)：区分存储技术、系统角色、接口协议和集成方式。
3. [存储层次与系统角色](./memory-hierarchy-as-system.md)：了解 register file、cache、scratchpad 和外存各自承担的职责。
4. [速度·容量·成本·功耗](./memory-hierarchy-tension.md)：了解比较存储方案时需要考虑的目标与代价。
5. [局部性与数据搬运](./locality-working-set-data-movement.md)：理解访问顺序、工作集和数据复用如何影响搬运。
6. [SRAM 与 DRAM 的分化](./sram-dram-divergence.md)：比较两种常见存储单元的保持、读取和系统应用。

<span id="建模启示"></span>

需要建立模型时，可参考[存储系统为何难设计](./problem-statement.md#建模启示)中的模型边界，也可查阅[存储器建模模板](../../reading-and-reference/02-reference/memory-modeling-template.md)。
