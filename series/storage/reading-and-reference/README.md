# 查阅与练习：学习路径、参考工具与自测

这里是存储系统六个技术专题的共同入口。先按问题选择路线，再查术语、检查设计或用题目检验理解；不必按顺序读完全部材料。

## 按任务选择入口

| 目标 | 建议入口 | 能得到什么 |
| --- | --- | --- |
| 手算一条数据路径 | [CPU 读一个整数](./01-reading/first-read-practice.md#cpu-read) · [NPU 搬一块权重](./01-reading/first-read-practice.md#npu-move) | 判断读取会停在哪一层，或核对同一块权重在不同接口穿过多少次。 |
| 找到学习次序 | [按目标选择学习路径](./01-reading/learning-roadmap.md) | 按系统全貌、DRAM 模型、NPU buffer 和性能分析选择前置知识。 |
| 检验理解 | [自测问题](./01-reading/self-test-questions.md) | 按章节挑选 82 道题，每题链接到参考正文，包含可靠性和 HBF 综合题。 |
| 查概念 | [术语表](./02-reference/glossary.md) · [高频问答](./02-reference/high-frequency-questions.md) | 区分介质、接口、控制、系统角色和封装。 |
| 核查设计 | [SRAM 选型清单](./02-reference/sram-design-checklist.md) · [DRAM 性能排查清单](./02-reference/dram-debug-checklist.md) | 记录问题、条件和证据，并选择下一步检查。 |
| 建立模型 | [DRAM 时序速查](./02-reference/timing-parameter-cheatsheet.md) · [存储系统建模模板](./02-reference/memory-modeling-template.md) | 选择模型边界，记录约束、观测点和验证方法。 |

[参考资料与工具](./02-reference/README.md)列出全部查阅页面。[跨层分析要点](./02-reference/first-principles.md)适合在比较方案前统一问题和观察边界。

## 六个技术专题

1. [存储层级与数据路径](../01-memory-hierarchy/README.md)：系统角色、访问路径、瓶颈与 NPU 案例。
2. SRAM 器件与应用：[基础](../02-sram/foundations/README.md) · [应用](../02-sram/applications/README.md)。
3. DRAM 器件与接口：[单元与阵列](../03-dram/foundations/README.md) · [命令与接口](../03-dram/protocols/README.md)。
4. [DRAM 控制器与请求调度](../04-dram-controller/README.md)：地址映射、请求排队、调度和刷新。
5. [HBF 高带宽闪存](../05-hbf/README.md)：NAND、访问路径、可靠性及工作负载。
6. [存储系统集成与选型](../06-system-integration/README.md)：封装、系统约束和选型。

[原 RAM 章节阅读路线](./01-reading/README.md)保留了原 01—09 的组织方式和旧地址，便于从历史链接继续阅读。它不是当前六专题的完整目录，也不覆盖整个 HBF 专题。[Cache 与 scratchpad 原入口](./01-reading/cache-scratchpad-introduction.md)保留历史搜索入口，并指向合并后的主文。
