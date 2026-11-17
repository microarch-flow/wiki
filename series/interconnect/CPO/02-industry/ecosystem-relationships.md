# 生态关系图与协作逻辑

上级：[02 产业链与角色](./README.md)

相关：[产业链与角色](./value-chain.md)、[公司与平台图谱](./company-landscape.md)

## 一张图看 CPO 生态

```mermaid
graph TD
    A[AI Cluster / Data Center Demand] --> B[Switch ASIC Vendor]
    A --> C[System OEM / Network Vendor]
    B --> D[SerDes / Electrical IO]
    B --> E[Package / Thermal Co-Design]
    C --> E
    F[Silicon Photonics / Optical Engine Vendor] --> E
    G[Laser / III-V Supplier] --> F
    H[Foundry / OSAT / Assembly] --> E
    I[Test / Reliability / Equipment] --> H
    E --> J[Integrated CPO System]
    J --> K[Deployment / Operations]
    K --> A
```

## 这张图真正想表达什么

CPO 不是简单的上下游串联，而是一个强耦合协作网络：

- 交换芯片和系统厂商共同约束容量、接口与热预算
- 光引擎和光源供应商提供器件方案及其工作条件
- 封装与测试环节影响装配、筛测和可靠性
- 系统厂商、客户和运维团队共同约束替换单元与验收条件

具体职责由项目分配，不能从图中的角色推断某家公司拥有全部决策权。详细供应过程见[供应链分层](../09-supply-chain-geography/supply-chain-stack.md)，公开公司关系见[合作关系图](../10-company-ecosystem/partnership-map.md)。

## 为什么这种协作比 pluggable 更难

在 pluggable 体系里，模块和交换机之间的标准接口更清晰；而在 CPO 里，很多问题必须提前到联合设计阶段解决：

- 热
- 布局
- 光纤引出
- 测试点
- 故障责任边界

## 读公司与论文时的一个简单问法

每看到一个方案，都问：

1. 谁在定义系统问题
2. 谁在承担封装和测试风险
3. 谁在为后期维护负责
