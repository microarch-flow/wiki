# 01 · 总览:算力单元为何长成这样

本章把整个 COMPUTE 域的问题、主线和路线立起来。三篇必读,顺序如下:

1. **[算力单元要解决什么:计算很少,搬运很多](./problem-statement.md)**
   用一个门数账(24p 搬运 : 4p 计算)钉死"分母才是主体"。全域的出发点。

2. **[计算 / 通信比:贯穿 COMPUTE 全域的不变量](./compute-communication-ratio.md)** ⭐ 纲领
   定义全域唯一主线,给出六层级统一表格。其余每一篇都回指这里。

3. **[学习路线与域边界:原语 → 阵列 → 流水 → 布局](./taxonomy-and-roadmap.md)**
   自底向上的阅读顺序,以及 COMPUTE 与 BUS/RAM/NOC/DMA/FAB/CIM/Workload 的边界划分。

---

## 一句话抓住本域

> 芯片面积里真正做乘加的逻辑是零头,绝大部分面积花在把数据搬到能算的地方。每一层的设计动作,本质都是在抬高"有用计算 / 数据搬运"这个比值。

读完本章,你应该能拿着[那张六层级表](./compute-communication-ratio.md#2-同一个-trade-off-在六个层级各出现一次)去读后面任何一章,并在每章收尾处自答:**本章的机制在主线上处于哪一行、把比值推向哪边。**

---

## 后续章节

- [02 · datapath 基础](../02-datapath-foundations/) — 从门搭 MAC、压缩树、位宽二次缩放、数字格式、mux 成本
- [03 · systolic array](../03-systolic-array/) — 上提循环翻转比值
- [04 · 时钟与流水](../04-clocking-and-pipeline/) — 同步的代价
- [05 · FPGA vs ASIC](../05-fpga-vs-asic/) — 可配置性的 10× 税
- [06 · 存储 discipline](../06-memory-discipline/) — cache vs scratchpad
- [07 · 芯片顶层组织](../07-chip-organization/) — CPU/GPU 核、脑 vs 芯片、GPU=平铺 TPU
- [08 · 面向 archax 的建模](../08-modeling-for-archax/) — 7 条建模启示
