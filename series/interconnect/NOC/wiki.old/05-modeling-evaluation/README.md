# 05 建模与评估

本章面向你的核心目标：基于 workload（工作负载）做片上架构探索。

## 本章入口

- [建模层次](./modeling-layers.md)
- [指标与实验设计](./metrics-experiments.md)
- [架构探索方法](./architecture-exploration.md)
- [QoS（服务质量）、公平性与 Stall Taxonomy（停顿分类体系）](./qos-fairness-stall-taxonomy.md)
- [Simulator（模拟器）设计规格](./simulator-design-spec.md)
- [Simulator 数据结构与伪代码](./simulator-data-structures-pseudocode.md)
- [实验模板与结果模板](./experiment-result-templates.md)
- [Simulator 最小实现路线](./simulator-implementation-roadmap.md)
- [AI Accelerator NoC Case Cards 与论文卡模板](./ai-accelerator-noc-case-cards-templates.md)
- [第一批真实 NoC / Accelerator Case Cards](./first-batch-real-noc-accelerator-case-cards.md)
- [第一批具体论文卡与架构实例卡](./first-batch-concrete-paper-architecture-cards.md)
- [实验结果沉淀模板与状态页](./experiment-results-log-and-status.md)
- [从 Workload 到 Traffic Trace 操作手册](./from-workload-to-traffic-trace.md)
- [架构分析题库 / 决策模板 / 自测清单](./architecture-analysis-playbook.md)
- [推荐阅读顺序：面向 Workload-Based NoC 架构分析](./recommended-reading-path-for-workload-based-analysis.md)
- [NoC 功耗与面积建模](./power-area-modeling.md)

## 读本章前先统一 6 个词

- `modeling layer`：模型保留多少真实细节的层次
- `metric`：你用什么指标判断方案更好
- `trace`：按时间顺序列出的通信事件或 packet 序列
- `first-order insight`：能快速解释主瓶颈的一阶结论，不追求极致精度
- `stall breakdown`：把停顿按原因拆开统计，而不是只看“总共慢了多少”
- `boundary`：结论成立的前提和适用范围；没有边界的结论通常不稳

## 一句话总纲

做 NoC（片上网络）架构探索，不是先追求最复杂模型，而是先建立一套能稳定给出一阶洞察的分层建模方法，再逐步补真实度。
