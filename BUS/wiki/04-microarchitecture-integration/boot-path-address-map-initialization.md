# Boot Path 与地址映射初始化

上级：[04 微架构与系统集成](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[CPU、DMA、外设与内存之间的总线路径](./dma-cpu-peripheral-memory-path.md)

## 这页在回答什么问题

芯片上电之后，BUS 不是天然“已经可用”的；启动阶段到底是怎样把地址空间和访问路径逐步拉起来的。

## Boot 阶段最先依赖什么

通常最早能工作的只有一小部分路径，例如：

- boot ROM
- 最小 CPU fetch path
- 时钟和复位控制寄存器
- 少量 debug / strap / fuse 读取路径

这意味着启动早期的 bus fabric 往往比最终运行态更简单、更受限。

## 地址映射初始化为什么关键

软件和固件必须尽早知道：

- 哪一段地址对应 boot ROM
- 哪一段地址对应 SRAM
- 哪些外设已经可访问
- 哪些区域暂时不能碰

否则很容易出现“访问到了，但系统还没准备好”的错觉。更常见的结果其实是：

- decode error
- slave error
- timeout
- 或因为时钟/复位/隔离未打开而进入 hang

## 启动过程常见的阶段变化

- 先从 ROM 启动
- 初始化时钟、复位和 pinmux
- 打开 SRAM / DRAM / 外设访问路径
- 建立更完整的异常、中断和 DMA 环境

每一步都可能改变 bus fabric 的可访问范围和时序条件。

## 一句话理解

boot path 本质上是“从最小可用互连逐步扩展到完整系统互连”的过程，地址映射和访问次序必须和这个过程匹配。
