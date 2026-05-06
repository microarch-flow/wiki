# 术语表

上级：[06 术语与检查清单](./README.md)

## 基础对象

- `Node`：接入 NoC 的计算、存储或 I/O 模块
- `Router`：负责 packet / flit 转发的网络节点
- `NI`：Network Interface，tile 与 NoC 的协议转换与注入/弹出接口
- `Link`：router 之间的数据通路

## 传输单位

- `Packet`：一次完整通信事务的语义单位
- `Flit`：flow control unit，router 流控和仲裁的基本单位
- `Phit`：physical transfer unit，物理链路每周期实际传输单位

## 控制与资源

- `VC`：Virtual Channel，共享物理链路的逻辑队列
- `Credit`：下游剩余 buffer slot 的计数
- `Backpressure`：由于下游阻塞导致的反向停发传播
- `HOL blocking`：队头阻塞导致后续无关流量也被堵住

## 路由与切换

- `Topology`：网络连接结构
- `Routing`：为 packet 选择路径的方法
- `Arbitration`：多个请求竞争一个资源时的选择机制
- `Wormhole`：header 牵引 body/tail 逐跳流水前进的 switching 模式

## 性能与风险

- `Latency`：从注入到送达的延迟
- `Throughput`：单位时间完成的数据传输量
- `Saturation point`：网络从近线性增长进入明显拥塞的转折点
- `Deadlock`：资源循环等待导致无前进状态
- `Livelock`：持续移动但长期无法到达目的地
- `Starvation`：某类请求长期得不到服务
