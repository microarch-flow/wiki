# 研究模板

上级：[09 参考资料与研究模板](./README.md)

## 适用范围

适用于：

- 一篇 DMA 论文
- 一个 DMA IP
- 一条 DMA 数据路径
- 一类 DMA 性能问题

## 推荐结构

```md
# 标题

## 研究对象

- 系统类型：
- DMA 所在位置：
- 主要传输路径：
- 控制模型：
- coherent / IOMMU 假设：

## 它在解决什么问题

一句话说明核心目标。

## 关键机制

- command / descriptor 组织
- burst / outstanding 策略
- completion / synchronization 语义
- 与 NoC / memory / cache 的关系
- observability / debug 钩子：

## 关键指标

- 吞吐
- 尾延迟
- overlap 成功率
- buffer / queue 占用

## 最值得抄走的设计点

- 

## 最大限制或风险

- 
```

## 一句话理解

研究 DMA 时，最重要的是把“它搬什么、怎么调度、受谁限制、如何完成”记录完整。
