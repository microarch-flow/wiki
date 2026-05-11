# MCU / SoC / AI 芯片中的 BUS 对照

上级：[06 典型系统与案例](./README.md)

相关：[BUS vs NoC vs Point-to-Point](../02-fundamentals/bus-vs-noc-vs-point-to-point.md)、[NoC Wiki 首页](../../../NOC/wiki/README.md)

## 这页在回答什么问题

为什么不同系统都在用 BUS，但组织方式差别很大。

## MCU

典型特征：

- master 少
- 外设多
- 软件强控制
- 带宽压力不极端

因此常见做法是：

- 主干相对简单
- AHB/APB 一类分层很常见
- 重点在低成本和易验证

## 通用 SoC

典型特征：

- CPU、DMA、DDR、display、storage 等并存
- 同时有控制面和数据面
- 外设种类多

因此常见做法是：

- 高性能主干 + 外设子总线
- 大量 bridge
- 需要 QoS 和更多 observability

## AI 芯片

典型特征：

- 控制路径仍然需要 BUS
- 数据路径吞吐极高
- 节点分布广

因此常见做法是：

- BUS 保留在寄存器、配置和控制路径
- 大吞吐数据面转向 NoC 或专用通路
- DMA 通过 BUS 或 NI 接入更大的片上数据网络

## 一句话理解

系统越偏控制和低成本，BUS 越居中；系统越偏大规模并发数据面，BUS 越像控制骨架而不是主数据面。
