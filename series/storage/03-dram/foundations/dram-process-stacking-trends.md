# DRAM 密度扩展：电容、芯片堆叠与封装

上级：<span id="dram-工艺路线平面到堆叠到-3d"></span>[DRAM 单元与阵列](./README.md)

相关：[HBM 集成与 TSV](../../06-system-integration/packaging/hbm-2.5d-3d-tsv.md) · [HBM 成本](../../06-system-integration/packaging/why-hbm-is-expensive.md)

## 这页在回答什么问题

“平面到堆叠到 3D”容易混淆单元结构、芯片内部阵列和封装。它们分别改变什么？堆叠容量是否意味着外部带宽必然增加？

## 密度扩展与电容约束

提高密度需要缩小单元占用，同时维持足够的电容、隔离和制造良率。立体电容结构可以在有限平面面积内增加有效面积；例如 [IBM 关于深沟槽 DRAM 电容的研究](https://research.ibm.com/publications/novel-techniques-for-scaling-deep-trench-dram-capacitor-technology-to-011-mm-and-beyond)展示了特定年代的一条工艺路线，不能由此推断所有后续产品采用同一结构。

芯片内阵列的三维组织、多个 die 的堆叠、以及多芯片封装是不同层次的方案。HBM 通过堆叠与宽接口组合提供高带宽，但其他堆叠产品也可能共享一个外部接口。[Infineon 512 Mbit HyperRAM 资料](https://www.infineon.com/assets/row/public/documents/10/57/infineon-s80ks5122-1.8-v-512-mbit-hyperbus-interface-hyperram-self-refresh-dram-additionaltechnicalinformation-en.pdf)描述了由两个 256 Mbit die 构成的器件，其接口规格仍由产品定义。容量、引脚数、数据率和可并行的内部资源必须分别核对。

堆叠还引入互连、散热、测试和封装成本；它不自动决定有效带宽或每 bit 能耗。HBM 的系统集成与成本在相关专题展开。

## 一句话理解

电容结构改善单元密度，die 堆叠和封装组织多个芯片；它们解决的问题并不相同。

## 建模启示

分别列出每 die 容量、die 数、外部位宽、速率和共享范围。带宽取决于实际可用接口，面积与能耗应使用目标工艺和封装数据。
