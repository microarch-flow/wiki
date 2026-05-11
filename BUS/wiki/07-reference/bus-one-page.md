# BUS 一页版总览

上级：[07 术语与检查清单](./README.md)

## BUS 是什么

BUS 本质上是片上事务互连层，用来把：

- CPU
- DMA
- memory
- peripheral
- accelerator

放进同一套 `地址、请求、响应、顺序、流控` 规则里。

## 它为什么重要

BUS 的价值不只是“把模块接起来”，而是让系统回答这些问题：

- 谁可以访问谁
- 谁先走
- 数据怎么回来
- 下游慢时谁被反压
- 软件什么时候能相信结果已经可见

## 它最核心的对象

- transaction
- address / control / data / response
- arbitration
- ordering
- backpressure
- bridge / CDC / width adaptation

## 协议主线怎么分

- `APB`：低复杂度寄存器/外设访问
- `AHB/AHB-Lite`：中等复杂度主干或子系统总线
- `AXI`：高性能多通道事务协议
- `TileLink`：参数化 SoC 生态中的统一事务框架

## 系统里最常见的真实分工

- BUS：控制骨架、寄存器、状态、boot、debug
- DMA：把数据搬运需求组织成总线事务
- DDR controller：把 AXI 请求重新调度成受阵列约束的命令流
- NoC：承担大规模并发数据面

## 最常见的性能问题

- 仲裁导致尾延迟变长
- bridge / CDC 形成隐藏瓶颈
- read/write turnaround 拉低有效吞吐
- row locality 差导致返回流抖动
- response path 比 request path 更早堵住

## 最常见的正确性问题

- MMIO 顺序和副作用没处理好
- descriptor 可见性没建立就敲 doorbell
- completion 写回和 interrupt 顺序错位
- IOMMU/SMMU 映射或权限出错
- timeout / error / hang 没有明确闭环

## 最常见的调试路径

1. 先分清是 `timeout / fault / hang`
2. 再分清是 `request 没发到 / slave 没收 / response 没回来`
3. 再看是 `协议问题 / 互连问题 / DDR 问题 / IOMMU 问题 / 软件可见性问题`

## 一句话结论

BUS 不是“线网细节”，而是把 `协议语义、系统集成、性能瓶颈、软件可见性` 串在一起的片上基础设施。
