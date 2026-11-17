# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[完整学习路线](../16-learning-navigation/study-navigation.md)、[术语表](../08-research/glossary.md)

## 建议学习路径

### 阶段 1：先搞清系统问题

先看[系统问题](./problem-statement.md)：电通道、面板密度和功耗何时约束目标配置。

### 阶段 2：先分清相邻概念

用[分类框架](./taxonomy.md)区分集成位置、光源位置和器件工艺；同一方案可以同时落在多个维度。

### 阶段 3：建立系统栈视角

沿[系统栈](../03-architecture-platform/system-stack.md)追踪数据和可选供光支路；retimer 与 gearbox 是否存在取决于实现。

### 阶段 4：进入光引擎

阅读[光链路基础](../04-optical-engine/optical-link-basics.md)，明确各器件的输入、输出和预算参考面。

### 阶段 5：进入共性工程问题

从[功耗与热](../05-electrical-thermal-reliability/bandwidth-power-thermal.md)进入，再看[制造与良率](../06-manufacturing/README.md)和[测试与可靠性](../05-electrical-thermal-reliability/reliability-test.md)。

### 阶段 6：再看产业与商业化

从[产业角色](../02-industry/value-chain.md)进入；公司关系和产品状态以[来源表](../18-sources-and-updates/company-ecosystem-sources.md)为准。

## 常见误区

### 误区 1：CPO 只是“更高级的光模块”

不准确。它改变的是系统边界、测试边界和维护边界，不只是模块形态升级。

### 误区 2：只要把电改成光，功耗就一定更低

错误。系统总功耗取决于 SerDes、driver、TIA、laser、热设计和封装损失，不是“光”三个字自动获胜。

### 误区 3：CPO 的主要难点只是硅光器件

错误。真正决定量产难度的往往是热、封装、测试、维修和供应链协同。

### 误区 4：CPO 一定会全面替代 pluggable

错误。它更可能先在超高带宽、超高密度、功耗敏感的特定场景落地，而不是一步替代全部数据中心互连。
