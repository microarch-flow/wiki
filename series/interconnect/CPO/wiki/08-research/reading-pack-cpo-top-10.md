# CPO 入门必读 10 篇

上级：[08 研究模板与术语](./README.md)

相关：[论文卡片库](./paper-cards/README.md)、[学习路线图](../01-overview/learning-roadmap.md)

## 这页和其他论文页怎么分工

- 这页只负责：告诉你“先读哪 10 篇”
- [4 天学习计划与阅读提问清单](./4-day-study-plan.md) 负责：把这 10 篇排成执行顺序
- [案例库](./case-studies/README.md) 负责：告诉你不同类型论文应该怎么读
- [论文卡片库](./paper-cards/README.md) 负责：按主题沉淀具体论文
- [完整论文卡](./detailed-cards/README.md) 负责：把少数关键论文展开成深读笔记

如果你只想快速进入文献世界，这页最合适。  
如果你已经开始读具体论文，就应该更多跳转到后面几层。

## 这 10 篇怎么选的

这不是“引用最多的 10 篇”，而是更适合系统学习的 10 篇。筛选原则是：

- 先建立全局问题地图
- 再理解系统为什么需要更近的光 I/O
- 再看 chiplet / 光引擎 / 外置激光
- 最后进入封装、连接和可靠性

## 推荐阅读顺序

### 1. `Co-packaged optics (CPO): status, challenges, and solutions`

- 类型：综述
- 为什么先读：这是最适合建立全局问题空间的一篇入口文献
- 你要记住：CPO 不是单一器件问题，而是系统、光引擎、封装、DSP、测试、标准化一起耦合的问题
- 链接：https://link.springer.com/article/10.1007/s12200-022-00055-y

### 2. `In-Package Optical I/O: Bridging the Gap Between Moore's Law and Amdahl's Law in Modern Compute Systems`

- 类型：系统动机 / OFC 报告
- 为什么第二篇读：它把 optical I/O 放回现代计算系统和分布式扩展的语境
- 你要记住：更近的光 I/O 解决的不是“模块形态升级”，而是计算系统扩展性问题
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2024-Tu2F.4

### 3. `TeraPHY: A High-density Electronic-Photonic Chiplet for Optical I/O from a Multi-Chip Module`

- 类型：光 I/O chiplet / OFC 论文
- 为什么第三篇读：它帮助你从“概念上的 CPO”进入“可被封装的 chiplet 光 I/O”
- 你要记住：真正进入系统的 optical I/O 往往会以 chiplet 或可共封装部件的形式出现
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2019-M4D.7

### 4. `Connectorized Optical I/O Chiplet with V-groove for AI and High Performance Computing`

- 类型：连接工程 / OFC 论文
- 为什么接着读：它把 chiplet 光 I/O 推到连接、KGD 和工程可制造性层面
- 你要记住：当论文开始讨论 connectorized、V-groove、known good chiplet 时，说明问题已经进入量产工程区
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2025-Th3H.2

### 5. `Optoelectronic Glass Substrates for Co-packaging of Optics and ASICs`

- 类型：封装平台 / OFC 论文
- 为什么第五篇读：它把你从“器件封装”带到“封装基板本身成为光平台”的视角
- 你要记住：CPO 有时不仅重构光引擎位置，也会重构 substrate 平台定义
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2020-Th3I.5

### 6. `Photonic Modules with High Density Polymer Waveguide Interface`

- 类型：模块接口 / OFC 论文
- 为什么第六篇读：这是从平台概念走向高密度光模块接口实现的一步
- 你要记住：高密度 polymer waveguide interface 是提高 optical lane density 的现实路径之一
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2025-Th3H.4

### 7. `Co-Packaged Optics (CPO) Technology Full Module Test Vehicle Demonstrations`

- 类型：模块验证 / ECTC 论文
- 为什么第七篇读：它开始认真回答“完整模块能不能装出来并过可靠性测试”
- 你要记住：full module、reflow compatibility、JEDEC stress 这些词，是判断论文工程含量的重要信号
- 链接：https://research.ibm.com/publications/co-packaged-optics-cpo-technology-full-module-test-vehicle-demonstrations

### 8. `Co-packaged optics module with single mode polymer waveguide`

- 类型：模块集成 / IEDM 报告
- 为什么第八篇读：它把单模 polymer waveguide、lane density 和 optics-last assembly 放到同一页里
- 你要记住：只要开始讨论 optics-last assembly，作者就在认真面对量产装配窗口
- 链接：https://research.ibm.com/publications/co-packaged-optics-module-with-single-mode-polymer-waveguide

### 9. `Improved connectorization of compliant polymer waveguide ribbon for silicon nanophotonics chip interfacing to optical fibers`

- 类型：连接与装配 / ECTC 论文
- 为什么第九篇读：它让你看到光学高精度对准，怎样被转化成可制造连接流程
- 你要记住：很多 CPO 难题，不在峰值带宽，而在“如何把实验室对准变成高吞吐装配”
- 链接：https://research.ibm.com/publications/improved-connectorization-of-compliant-polymer-waveguide-ribbon-for-silicon-nanophotonics-chip-interfacing-to-optical-fibers

### 10. `Experimental Identification of the Failure Modes and Failure Mechanisms of Fiber to Waveguide Couplings Under Cyclic Tensile Loading`

- 类型：可靠性 / ECTC 论文
- 为什么最后读：它把你从“能做出来”拉回“长期运行会不会坏”
- 你要记住：真正拖慢 CPO 落地的，往往是 attach、stress、aging 和失效边界，而不是光链路 demo 指标
- 链接：https://research.ibm.com/publications/experimental-identification-of-the-failure-modes-and-failure-mechanisms-of-fiber-to-waveguide-couplings-under-cyclic-tensile-loading

## 读完这 10 篇后，你应该能回答什么

1. 为什么 CPO 不是“更高级的光模块”
2. 为什么 AI / HPC 比通用数据中心更可能率先推动 CPO
3. 为什么 external laser、chiplet optical I/O、polymer waveguide interface 会反复出现
4. 为什么封装、连接和可靠性论文对判断落地性比器件峰值指标更重要

## 不建议的读法

- 不要按年份顺序硬读
- 不要把综述和产品方案页当成最终定论
- 不要只看系统文献，不看连接和可靠性文献
- 不要只看器件峰值，不看 assembly 和 test

## 一条最实用的阅读路径

- 第 1 天：先读第 1、2 篇，建立问题地图
- 第 2 天：读第 3、4、5 篇，理解 chiplet、封装平台和外部连接
- 第 3 天：读第 6、7、8 篇，进入模块与装配
- 第 4 天：读第 9、10 篇，理解为什么可靠性会决定商业化边界
