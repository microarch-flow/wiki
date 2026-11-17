# CIM Wiki

本目录用于把 `chat.md` 中的 CIM 学习框架沉淀成可持续扩展的知识库。

## 目标

- 建立一套从概念到产业的 CIM 知识树
- 支持后续持续补充论文、公司、产品、指标和分析笔记
- 让技术分析、产业研究、架构建模使用同一套术语和模板

## 建议使用方式

1. 先看 [知识地图](./SUMMARY.md)
2. 再读 [01 概览与问题定义](./01-overview/README.md)
3. 之后沿 `介质路线 -> 电路 -> 架构 -> 软件 -> workload -> 产业` 顺序推进
4. 做论文或公司研究时，统一复用 `09-research` 下的模板

## 推荐起步路径

- [CIM 在解决什么问题](./01-overview/problem-statement.md)
- [CIM / PIM / Near-Memory 分类](./01-overview/taxonomy.md)
- [学习路线图](./01-overview/learning-roadmap.md)
- [SRAM-CIM](./02-memory-technologies/sram-cim.md)
- [DRAM / HBM-PIM](./02-memory-technologies/dram-hbm-pim.md)
- [ReRAM / RRAM-CIM](./02-memory-technologies/reram-cim.md)
- [从 Macro 到 Chip](./05-architecture-system/macro-to-system.md)
- [数据流与算子映射](./05-architecture-system/dataflow-mapping.md)
- [编译器与 Runtime](./06-software-stack/compiler-runtime.md)
- [模型适配与图划分](./06-software-stack/model-adaptation.md)
- [Transformer / LLM](./07-workloads/transformer-llm.md)
- [产业链结构](./08-industry/value-chain.md)
- [从论文到产品的路径](./08-industry/productization-path.md)
- [制造、测试与量产挑战](./08-industry/manufacturing-test-challenges.md)
- [商业化评估清单](./08-industry/commercialization-checklist.md)
- [公司横向比较矩阵](./08-industry/company-comparison-matrix.md)
- [案例库](./09-research/case-studies/README.md)

## 如果你只想先建立判断力

建议先读这一条最短主线：

1. [CIM 在解决什么问题](./01-overview/problem-statement.md)
2. [CIM / PIM / Near-Memory 分类](./01-overview/taxonomy.md)
3. [SRAM-CIM](./02-memory-technologies/sram-cim.md)
4. [DRAM / HBM-PIM](./02-memory-technologies/dram-hbm-pim.md)
5. [ReRAM / RRAM-CIM](./02-memory-technologies/reram-cim.md)
6. [从 Macro 到 Chip](./05-architecture-system/macro-to-system.md)
7. [编译器与 Runtime](./06-software-stack/compiler-runtime.md)
8. [Transformer / LLM](./07-workloads/transformer-llm.md)
9. [产业链结构](./08-industry/value-chain.md)
10. [从论文到产品的路径](./08-industry/productization-path.md)
11. [制造、测试与量产挑战](./08-industry/manufacturing-test-challenges.md)
12. [公司横向比较矩阵](./08-industry/company-comparison-matrix.md)

## 当前框架

- [01 概览与问题定义](./01-overview/README.md)
- [02 存储介质与技术路线](./02-memory-technologies/README.md)
- [03 计算范式](./03-compute-paradigms/README.md)
- [04 电路与 Macro](./04-circuit-macro/README.md)
- [05 架构与系统](./05-architecture-system/README.md)
- [06 编译器与软件栈](./06-software-stack/README.md)
- [07 Workload 与应用](./07-workloads/README.md)
- [08 产业链与商业化](./08-industry/README.md)
- [09 研究模板与方法](./09-research/README.md)

## 维护原则

- 每页尽量只解决一个问题
- 每个主题页统一保留 `核心问题 / 关键指标 / 后续补充` 三部分
- 对论文、公司、产品，尽量使用模板化记录，避免信息散乱

## 当前已补实的重点页面

- 概览与问题定义
- taxonomy 与学习路径
- `SRAM / DRAM-HBM / ReRAM` 三条主路线
- `Digital / Analog / Mixed-Signal` 三类计算范式
- 电路层中的基础对象、ADC / DAC / SA、非理想因素
- 架构层中的 `macro -> tile -> chip -> system` 失真链、数据流映射与性能能耗建模
- 软件栈中的编译、runtime、模型适配与量化映射
- Transformer / LLM 适配分析
- 产业层中的供应链、产品化路径、量产测试挑战与公司横向比较
- 第一批代表性案例页
