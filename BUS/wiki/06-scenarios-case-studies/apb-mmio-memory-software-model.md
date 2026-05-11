# APB、MMIO 与普通内存的软件模型对照

上级：[06 典型系统与案例](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](../04-microarchitecture-integration/mmio-cache-interrupt-view.md)、[AHB-Lite 与 APB 深化](../03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive.md)

## 这页在回答什么问题

为什么从软件视角看，APB 外设访问、MMIO 和普通内存访问不能被当成同一种“load/store”来理解。

## 普通内存访问的典型预期

软件通常更容易默认：

- cache 可能参与
- 在很多架构里重排空间更大
- 带宽和局部性很重要

这更接近“性能对象”。

但这里也要加限定：  
这些行为还会受 ISA 内存模型、cacheability、shareability 和页属性影响，不是所有“普通内存”访问都自动拥有同样的重排和缓存语义。

## MMIO 访问的典型预期

软件必须更在意：

- 副作用
- 顺序
- 可见性
- barrier

这更接近“设备语义对象”。

## APB 外设访问为什么更特殊

APB 常是 MMIO 的一种实现落点，但它首先是总线实现路径，不是软件看到的一种“新内存类型”。它进一步强调：

- 路径更慢
- bridge 更多
- 流控更简单
- 访问闭环更依赖低速外设状态

所以从软件体验上，经常更容易暴露：

- 轮询抖动
- 读寄存器超时
- 初始化顺序依赖

## 一句话理解

普通内存关注的是“高效访问数据”，MMIO/APB 更关注的是“以正确顺序和语义访问设备状态”。
