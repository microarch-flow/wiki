# 论文卡模板

上级：[09 参考资料与研究模板](./README.md)

## 这页在回答什么问题

读一篇 DMA 论文时，应该记录哪些信息，才能让它不只是“结果数字摘抄”，而是真正能回流到这套 wiki 的判断框架里。

## 推荐结构

```md
# 论文标题

## 基本信息

- 年份：
- 场景：
- 系统类型：
- 主要路径：
- 控制模型：
- coherent / IOMMU 假设：
- 完成语义边界：

## 它在解决什么 DMA 问题

一句话说明。

## 核心机制

- 地址生成：
- 调度 / outstanding：
- completion / synchronization：
- 与 NoC / memory / cache 的关系：
- observability / debug 方法：

## 关键指标

- 吞吐：
- completion visible latency：
- tail latency：
- overlap 成功率：
- 面积 / 功耗：
- 可扩展性：

## 这篇论文最值得学的点

- 

## 这篇论文没有解决什么

- 
```

## 为什么论文卡不能只记结果数字

DMA 论文最有价值的往往不是“带宽提升了多少”，而是它如何重新组织 descriptor、burst、completion 或 memory interaction。若只抄结果数字，后续几乎无法迁移到别的系统，也很难判断它适不适合自己的场景。

## 常见误解

常见误解：`论文卡就是摘要 + 结论`。实际上对于 DMA 这类系统主题，方法和边界条件往往比结论数字更值钱。

常见误解：`面积/功耗可以不记`。实际上很多 DMA 方案的 trade-off 正是拿状态复杂度去换吞吐和 overlap。

## 一句话理解

DMA 论文最值得记录的，不是结果数字本身，而是它如何组织数据移动、完成语义和系统资源交互。
