# RAM Wiki：从电路到系统

这份原 RAM 阅读路线横跨 SRAM、DRAM、控制器和系统等多个专题。它不覆盖 HBF 的全部内容。它区分单元的电气行为、宏接口、DRAM 命令以及系统调度。架构模型应保留影响可见延迟和资源竞争的边界，并用目标器件数据校准参数。

## 先修次序和章节入口

| 顺序 | 章节 | 输入知识与主要问题 |
|---|---|---|
| 1 | [01 概览](../../01-memory-hierarchy/README.md) | 区分物理单元、接口、系统角色与封装。 |
| 2 | [02 SRAM 基础](../../02-sram/foundations/README.md) | 从 6T 单元到阵列、端口和宏时序。 |
| 3 | [03 SRAM 应用](../../02-sram/applications/README.md) | 用 SRAM 基础解释 cache、scratchpad 和 buffer。 |
| 4 | [04 DRAM 基础](../../03-dram/foundations/README.md) | 从 1T1C 单元到 row buffer、bank 和 refresh。 |
| 5 | [05 DRAM 协议](../../03-dram/protocols/README.md) | 用阵列行为解释命令、时序和 DDR 家族。 |
| 6 | [06 Memory Controller](../../04-dram-controller/README.md) | 在协议约束下调度请求，并建模资源竞争。 |
| 7 | [07 系统架构](../../01-memory-hierarchy/01-system-basics/README.md) | 分析多级存储、有效带宽和系统访问延迟。 |
| 8 | [08 封装与集成](../../06-system-integration/packaging/README.md) | 连接封装、接口距离、带宽与成本。 |
| 9 | [09 AI 芯片存储](../../01-memory-hierarchy/04-npu-case/README.md) | 将上述知识用于 NPU buffer、数据流和外存。 |
| 查阅 | [10 参考](../02-reference/README.md) | 使用术语、时序速查和建模清单。 |

需要按原 RAM 章节顺序学习时，可按 01→02→03→04→05→06→07→08→09 阅读。这是阅读路线，不是当前网站的专题分组。更详细的依赖关系见[学习路线](./learning-roadmap.md)。只做 DRAM 命令仿真时，可先读 01→04→05→06，再查 [timing 速查](../02-reference/timing-parameter-cheatsheet.md)。只做片上 buffer 时，可先读 01→02→03→09。

电气阶段不自动等于一个时钟周期；协议时序也必须注明起止参考边沿。阅读和建模时，请先确定接口、时钟、工作点及来源，再区分示意例子与器件规格。

## 自测

阅读后可用[自测问题](self-test-questions.md)检查概念、迁移和架构判断。题目不附答案，每题链接到参考正文。
