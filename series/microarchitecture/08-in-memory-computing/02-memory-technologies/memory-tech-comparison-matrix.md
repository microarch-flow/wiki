# 存储计算路线速查：机制、代价与验证入口

<span class="micro-legacy-anchor" id="三大-memory-路线全景对比"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="不能直接横比的指标"></span>
<span class="micro-legacy-anchor" id="路线选择的第一性问题"></span>
<span class="micro-legacy-anchor" id="常见误解"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>
<span class="micro-legacy-anchor" id="研究启示"></span>


上级：[存储介质与计算路径](./README.md)

这张表用于定位需要深入核查的路径，不给路线排总榜。计算位置的术语口径见[分类页](../01-overview/cim-pim-nmc-taxonomy.md)，analog/digital/mixed-signal 的观察层级见[求值方式](../01-overview/two-axes-memory-and-paradigm.md)。


<span class="micro-legacy-anchor" id="路线对比矩阵"></span>

## 路线对照

| 路线与正文入口 | 可采用的机制 | 必须计入的代价 | 不能由名称推出的结论 |
| --- | --- | --- | --- |
| [SRAM-CIM](./sram-cim-foundation.md) | 阵列读路径中的位逻辑或电流/电荷计算 | cell 面积、端口、感测、累加及转换 | 标准 SRAM 工艺成熟不等于所有 CIM 宏已产品化 |
| [ReRAM-CIM](./reram-as-compute-element.md) | 电导编码与阵列 MVM 等 | 写入验证、非理想性、ADC、校准、差分编码 | 单元密度不等于系统可用权重密度 |
| [Flash-CIM](./flash-cim-niche.md) | 电荷状态与模拟读出路径 | 编程、保持、温漂、转换和模型更新 | 非易失不等于适合所有固定权重任务 |
| [PCM/MRAM](./pcm-mram-for-cim.md) | 按器件分别核查状态、感测与求值 | 写入、漂移或可靠性、读出、外围 | 两类器件不能共用一个精度或耐久结论 |
| [DRAM/HBM/GDDR-PIM](./dram-pim-foundation.md) | 本专题主线讨论 die/bank 内独立 CU | 指令能力、bank 共享、数据重排、host 同步 | 大容量不等于目标程序获得端到端加速 |

这些是需验证的候选机制。具体工艺、精度与数值以各篇列出的器件或论文为准。若研究 DRAM 阵列自身的复制或逻辑操作，需单独标明操作范围，不能套用独立 CU 的模型。

## 比较前统一什么

统一任务、精度、运算计数、包含的外围和能耗边界；分别报告初始化、稳态与尾部。把写入、转换、主机交换及未加速算子的成本计入所选系统范围。

可驻留权重数由可用 cell/bit、每权重编码、差分对、冗余和外围面积共同决定。TOPS/W 的峰值也必须标明哪些操作被计入，不能直接替代任务能量或 token latency。

## 读表后的下一步

沿上表进入对应器件正文，再读[宏到系统](../05-architecture-and-system/from-macro-to-system.md)和[性能能量建模](../05-architecture-and-system/performance-energy-modeling.md)。商业状态需看具体公司卡的证据日期；本表不以缺少同口径数据的“成熟度排名”代替验证。
