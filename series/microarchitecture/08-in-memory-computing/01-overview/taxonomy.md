# 如何完整记录一个存内或近存计算方案

<span class="micro-legacy-anchor" id="维度一计算位置"></span>
<span class="micro-legacy-anchor" id="维度二memory-technology"></span>
<span class="micro-legacy-anchor" id="维度三compute-paradigm"></span>
<span class="micro-legacy-anchor" id="一张总图"></span>


<span class="micro-legacy-anchor" id="cim-整体分类体系"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>


上级：[问题、术语与分类](./README.md)

一项方案不能只写“SRAM-CIM”或“PIM”。要让读者能比较和复查，至少记录以下五个维度。

| 维度 | 要填写的事实 | 主要来源 |
| --- | --- | --- |
| 位置与阵列参与 | memory die、base die、模块等位置；cell/array 是否求值 | 电路图、芯片组织、原始论文 |
| 存储介质 | SRAM、DRAM、ReRAM、Flash、PCM、MRAM 等 | 器件与工艺说明 |
| 执行机制 | CIM 的求值与转换路径，或独立 CU 的指令和数据通路 | 电路与架构文档 |
| 证据层级 | cell、macro、tile、chip、system/product | 测量对象、包含的外围、测试方法 |
| 工作负载 | 形状、精度、数据驻留、读写频率和软件映射 | 评估配置、程序与数据集 |

术语只在[位置与命名口径](./cim-pim-nmc-taxonomy.md)中定义；介质与求值的区别由[两种坐标](./two-axes-memory-and-paradigm.md)解释。这里负责把记录补齐。


<span class="micro-legacy-anchor" id="维度四系统层级"></span>

## 为什么必须写证据层级

Cell 证明某种物理行为可用；macro 加入了阵列和一部分外围。Tile、chip 和 system 继续引入 buffer、互连、host 和软件。局部结果不能自动证明更大层级的收益。

例如，某宏的能量只包含阵列与 ADC，就不能直接与包含片外内存和 host 的任务能量比较。需要补齐统计范围，或把结论限定在同一局部边界。


<span class="micro-legacy-anchor" id="维度五workload-适配"></span>

## 工作负载决定哪些成本暴露

固定权重与频繁更新权重，对写入和校准的要求不同。大 GEMM 与小矩阵向量运算，对利用率和加载摊销也不同。应先识别目标瓶颈，再检查搬运减少是否超过转换、同步、fallback 和额外控制的成本。

公司卡记录产品、证据日期和可验证状态；论文卡记录机制、实验条件与边界。原型、产品发布和规模部署是不同证据，不能合并成一个“已量产”判断。
