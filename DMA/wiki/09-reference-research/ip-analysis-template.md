# IP 分析模板

上级：[09 参考资料与研究模板](./README.md)

## 推荐结构

```md
# IP 名称

## 定位

- 用于什么系统：
- 主要传输路径：
- 总线/互连环境：

## 功能能力

- descriptor/queue 模型：
- scatter-gather：
- coherent/IOMMU：
- channels/QoS：

## 微架构能力

- outstanding：
- reorder/completion：
- stride/2D/3D：
- observability：

## 软件与系统接入

- driver 模型：
- interrupt/polling：
- virtualization/isolation：

## 最适合的场景

- 

## 主要短板

- 
```

## 一句话理解

分析 DMA IP，最重要的是把“功能、微架构、系统接入和观测能力”放在同一张卡片里看。
