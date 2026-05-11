# 互连组件与数据路径分解

上级：[04 微架构与系统集成](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[AXI Crossbar 案例卡](../06-scenarios-case-studies/axi-crossbar-case-card.md)

## 这页在回答什么问题

一个片上总线互连通常由哪些组件组成，以及瓶颈通常藏在哪。

## 常见组件

### Address decoder

负责判断目标 slave。  
它影响：

- 地址空间规划
- decode 延迟
- 错误返回路径

### Arbiter

负责在多个 master 之间决定先后。  
它直接影响：

- fairness
- latency jitter
- QoS 能力

### Mux / Demux / Crossbar

负责把多个输入连接到多个输出。  
从单总线到 crossbar，换来的不是“更高级”，而是：

- 更高并发
- 更多面积
- 更复杂的路由和控制

### FIFO / Buffer

负责吸收 burst、桥接节拍差和局部回压。  
它是性能和时序收敛的重要缓冲层。

## 看总线结构时最该追问什么

- 哪些资源是共享的
- 哪些路径可以并行
- 哪些地方一堵会把 stall 传播回 master

## 一句话理解

互连不是一根线，而是一组负责 `解码、仲裁、连接、缓冲` 的微架构组件。
