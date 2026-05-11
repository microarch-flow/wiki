# TileLink 概览

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)

## 这页在回答什么问题

TileLink 相比传统 ARM bus family，提供了什么不同的组织思路。

## TileLink 的几个关键词

- 参数化
- 模块化
- 支持从简单外设到一致性扩展
- 与生成式 SoC 设计流程更贴近

## 和 AXI 的关注点差别

AXI 更像一套行业通用、生态极强的高性能事务协议。  
TileLink 更强调：

- 在同一套框架里覆盖不同复杂度节点
- 更自然地服务可组合的开源 SoC 生成流程
- 对外交互时再通过 bridge 连接其他协议

## 什么时候值得关心它

- 你在看 RISC-V / Chisel / RocketChip 一系设计
- 你需要理解开源 SoC 里的总线组织
- 你要比较“生成式 fabric”与“标准商用总线 IP”两种路线

## 一句话理解

TileLink 不是为了取代所有总线，而是提供一套更适合参数化 SoC 生成和扩展的一致化事务框架。
