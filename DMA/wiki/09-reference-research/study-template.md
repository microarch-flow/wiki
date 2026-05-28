# 研究模板

上级：[09 参考资料与研究模板](./README.md)

## 这页在回答什么问题

当你研究一篇论文、一个 DMA IP、一条数据路径或一个性能问题时，应该按什么结构记录，才能让后续分析和横向比较都能接回这套 wiki 的主线。

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
- 完成语义边界：

## 它在解决什么问题

一句话说明核心目标。

## 关键机制

- command / descriptor 组织：
- burst / outstanding 策略：
- completion / synchronization 语义：
- 与 NoC / memory / cache 的关系：
- observability / debug 钩子：

## 关键指标

- 吞吐：
- completion visible latency：
- consumer-ready latency：
- tail latency：
- overlap 成功率：
- buffer / queue 占用：

## 系统瓶颈判断

- 当前最可能卡在：
- 为什么不是别的地方：

## 最值得抄走的设计点

- 

## 最大限制或风险

- 
```

## 为什么模板里必须有“完成语义边界”

很多 DMA 研究记录最容易缺的就是这一项，结果后面做横比时，把完全不同层次的“done”写成同一个 completion。只要这项没写清，后面的 latency、queue depth 和调优结论很容易全部偏掉。

## 常见误解

常见误解：`研究模板只要把功能和带宽记下来就够了`。实际上没有系统位置、完成语义和瓶颈判断，这种记录几乎不能复用。

常见误解：`所有研究对象都能套一份极简模板`。实际上模板应该统一主线，但必须保留 DMA 类型和系统画像差异。

## 一句话理解

研究 DMA 时，最重要的是把“它搬什么、怎么调度、谁能看到完成、真正受谁限制”记录完整。
