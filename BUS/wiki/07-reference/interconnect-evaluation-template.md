# 互连方案评估模板

上级：[07 术语与检查清单](./README.md)

## 推荐结构

```md
# 方案名称

## 场景定位

- 面向什么系统：
- 主要 master / slave：
- 控制面还是数据面：

## 拓扑与协议

- shared bus / bus matrix / crossbar：
- AXI / AHB / APB / TileLink：
- 是否含 coherent 路径：

## 关键能力

- outstanding：
- burst / narrow transfer：
- bridge / CDC / width adaptation：
- observability：

## 性能判断

- 理论瓶颈：
- 热点 slave：
- read/write 混合风险：
- return path 风险：

## 集成判断

- software model：
- DMA / IOMMU / DDR 接入：
- boot / debug / low-power 约束：

## 最适合的场景

- 

## 最大风险

- 
```

## 一句话理解

评估互连方案时，最重要的是把 `场景、拓扑、性能、集成风险` 放在同一张表里看。
