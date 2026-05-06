# 硅光与光引擎类论文卡片

上级：[论文卡片库](./README.md)

相关：[光链路基础](../../04-optical-engine/optical-link-basics.md)

## 这一类论文主要看什么

这一类论文更偏器件与光引擎实现，常见主题包括：

- PIC 结构
- 调制器和探测器实现
- driver / TIA 与 PIC 协同
- 光引擎尺寸、功耗和带宽

## 阅读时必须防止的误读

- 不要把器件层成功，自动等价成系统级可落地
- 不要把实验室带宽结果，自动等价成量产光引擎

## 论文卡片槽位

### 卡片 A：`TeraPHY: A High-density Electronic-Photonic Chiplet for Optical I/O from a Multi-Chip Module`

- 标题：TeraPHY: A High-density Electronic-Photonic Chiplet for Optical I/O from a Multi-Chip Module
- 作者 / 单位：Roy Meade 等 / Ayar Labs
- 时间：2019
- 类型：OFC 论文
- 链接：https://opg.optica.org/abstract.cfm?URI=OFC-2019-M4D.7
- 核心问题：怎样把电子-光子 chiplet 放进标准多芯片模块，形成可用的 optical I/O
- 关键贡献：明确把 optical I/O 做成 chiplet 形态来讨论，并把 SiP 集成、热和 fiber attach 拉进同一工程问题里
- 关键代价：更偏平台方向展示，公开摘要能看到的是思路和集成目标，细节仍需要结合更多实现材料理解
- 我最该记住的一句话：光 I/O 真正进入系统，不是单个器件变强，而是变成能被封装和组装的 chiplet

### 卡片 B：`Connectorized Optical I/O Chiplet with V-groove for AI and High Performance Computing`

- 标题：Connectorized Optical I/O Chiplet with V-groove for AI and High Performance Computing
- 作者 / 单位：Chong Zhang 等
- 时间：2025
- 类型：OFC 论文
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2025-Th3H.2
- 核心问题：如何把 optical I/O chiplet 做成更稳健、可扩展的连接方案，并引入 known good chiplet 思路
- 关键贡献：把 connectorized in-package optical I/O chiplet 和被动光纤连接、KGD 流程联系起来，直接对接 AI/HPC 的可制造性问题
- 关键代价：仍然主要集中在连接与封装工程，并不自动证明系统级部署问题已经都解决
- 我最该记住的一句话：chiplet 级 optical I/O 的关键，不只是带宽，还有连接和已知良品流程

### 卡片 C：如何理解这类论文

- 这类论文是“从器件走向工程产品”的中间层
- 它们最值得你看的，不是峰值指标，而是 chiplet、connector、KGD、assembly 这些词什么时候开始出现
