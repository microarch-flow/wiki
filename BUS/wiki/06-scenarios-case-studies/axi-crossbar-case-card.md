# AXI Crossbar 案例卡

上级：[06 典型系统与案例](./README.md)

相关：[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)、[AXI / AHB / APB 对照](../03-on-chip-protocol-families/axi-ahb-apb-comparison.md)

## 这页在回答什么问题

一个典型 AXI crossbar 设计，应该用什么框架去看它的价值和风险。

## 它通常想解决什么

- 多个 master 并发访问多个 slave
- 减少单共享总线的全局串行化
- 把 CPU、DMA、accelerator、DDR controller 更高效地接起来

## 它带来的好处

- 不同目标之间能获得更高并发
- 主干带宽利用率更高
- 更容易隔离局部热点

## 它带来的代价

- 面积更大
- 控制逻辑更复杂
- 时序压力更高
- response 路径和 ID 处理更难验证

## 看案例时最值得追问的点

- 是否所有 master 到所有 slave 都全连接
- 仲裁是在入口做还是目标端口做
- 是否支持多个 outstanding 和乱序返回
- 哪些地方用了寄存缓冲
- 慢 slave 会不会把快路径也拖慢

## 一句话理解

AXI crossbar 的本质是拿更多面积和实现复杂度，换取更高并发和更少不必要的全局串行化。
