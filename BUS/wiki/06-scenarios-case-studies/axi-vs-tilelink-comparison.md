# AXI vs TileLink 对照

上级：[06 典型系统与案例](./README.md)

相关：[AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)、[TileLink 概览](../03-on-chip-protocol-families/tilelink-overview.md)

## 这页在回答什么问题

AXI 和 TileLink 都能做片上事务互连，但它们更适合被放在什么语境里比较。

## AXI 更像什么

AXI 更像：

- 行业通用高性能事务协议
- 商用 IP 生态的默认选项
- 强调多通道、高 outstanding 和广泛兼容性

它的优势在于：

- 工具和 IP 生态成熟
- 与大量 CPU、DMA、DDR、外设 IP 对接直接
- 适合需要强兼容性的 SoC

## TileLink 更像什么

TileLink 更像：

- 参数化 SoC 生成流程里的统一事务框架
- 更贴近 RISC-V / Chisel / 开源互连生态
- 从简单外设到一致性扩展都能在同一体系里表达

它的优势在于：

- 模块化组合自然
- 在生成式设计里扩展体验更好
- 与开源 SoC 基础设施耦合更紧

## 不该怎么比

不要把它们简单比成：

- 谁“更先进”
- 谁“性能一定更高”

更准确的问题是：

- 你需要的是生态兼容，还是生成式可组合性
- 你面对的是商用 IP 拼装，还是自定义 SoC 构建

## 一句话理解

AXI 更像成熟工业生态里的通用语言，TileLink 更像参数化 SoC 世界里的原生组织语言。
