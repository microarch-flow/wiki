# NoC 检查清单：怎样避免遗漏条件？

<span id="checklists"></span>

上级：[10 查阅与练习](../SUMMARY.md#09-reference)；原章节：[09 Reference](./README.md)

相关：[设计决策路径](./noc-design-decision-tree.md)、[架构探索与实验设计](../07-evaluation-methodology/architecture-exploration-loop.md)、[实现路线](../08-simulator-construction/implementation-roadmap.md)

<span id="这页在回答什么问题"></span>按当前任务选择相关检查项。清单帮助发现缺失信息，不能代替容量计算、正确性证明或实验。

## 输入与目标

### 1. 读一章前的自检

- 当前要回答结构、路由、流控、端点还是工作负载问题？
- 需要输出哪个对象的延迟、吞吐或完成事件？
- 使用的术语和边界能否与相关正文对应？

### 2. NoC 设计评估 checklist

- 是否记录目标、负载、端点、时钟、面积／布线预算和可改变的参数？
- 瓶颈是观测结果、模型推论，还是尚待验证的候选？
- 结论覆盖哪些输入条件，有没有不满足目标或无可行方案的情况？

## 设计与资源

### 3. topology 选择 checklist

- 是否记录实际连接、链路方向、容量、端点及 memory 位置？
- 是否按实际路径或必经切面核算流量，并考虑物理跨度？
- 比较候选时固定了什么预算，哪些成本尚未校准？

### 4. routing / QoS checklist

- 合法路径、VC 映射及资源转换是否明确？是否检查了协议和端点依赖？
- 隔离或调度针对什么流，输入突发、仲裁与端点服务有什么条件？
- 是否区分有限样本中的等待，与有证明条件的服务界？

### 5. memory-centric checklist

- 请求和响应分别到达哪些端点，是否处于任务依赖链？
- memory placement、端口、ejection 和本地写入服务是否已表示？
- 链路平均利用率较低时，是否检查局部热点和供数不足？

## 模型与实验

### 6. workload-to-trace checklist

- 是否记录映射结果，或能重现映射的规则、输入和随机种子？
- 释放时间、依赖、目的集合、class 和完成事件是否明确？
- 分包规则是在 Trace 中还是下游应用，payload／wire 口径能否复现？

字段和 all-of 完成规则以所选 schema 为准；[本专题 v1 契约](../07-evaluation-methodology/from-workload-to-traffic-trace.md#输入输出与完成边界)是一个具体例子。

### 7. simulator 实现 checklist

- 是否固定对象、写入者、拍初／拍末顺序及输出边界？
- 是否区分本地上下文、slot credit 和下游 VC 许可？
- 是否定义端点服务、失败动作、停止条件及未完成对象？
- 是否先为已实现的功能准备手算、不变量和回归？

### 8. 实验结果解读 checklist

- 统计对象、窗口、单位、平均值与分位数是否清楚？
- 注入、网络到达、consumer 完成和 workload 完成是否分开？
- 是否报告未完成任务、种子、重复运行和适用的波动？
- 是否区分实现验证、参数校准和对目标系统的适用性？

## 记录与自测

### 9. 写 case card 前 checklist

- 问题、baseline、候选、共同条件和变化参数是否可复查？
- 是否保存配置、输入、版本、结果及关键证据？
- 是否记录结论边界、未验证假设和下一步？

完整格式见[实验与案例记录](../07-evaluation-methodology/case-card-template.md)。

### 10. 自测 checklist

能否用一个明确例子区分 credit 与空槽、网络到达与消费完成、容量下界与实测完成时间？需要逐拍推导时，使用[练习与参考解答](./exercises-and-worked-solutions.md)；需要查词义时，使用[术语表](./glossary.md)。

<span id="一句话理解"></span><span id="建模启示"></span>检查项应对应可观察的输入、资源或结果；未知项要保留为未知，并安排后续验证。
