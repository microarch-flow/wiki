# SL、VL 与信用：InfiniBand 怎样分配链路资源？

上级：[InfiniBand](README.md)

Service Level（SL）表达服务分类，Virtual Lane（VL）组织链路上的独立流量资源。SL 到 VL 的映射及 VL 仲裁决定哪些流共享等待，信用则决定下游是否有接收空间。

## 从报文分类到输出队列

端点按路径和服务配置发送带有 SL 的包。交换机结合输入端口、输出端口与 SL，把包映射到输出 VL，再由仲裁选择可发送的流量。因此，SL 与 VL 不必一一对应，也不能把某个 SL 数字永久绑定到某个物理队列。

可用 VL 数量和仲裁能力取决于设备。管理用 VL15 具有特殊规则，不应把普通数据 VL 的信用和无损描述不加区分地套到管理流量。[InfiniBand QoS 文档](https://docs.nvidia.com/doca/archive/3-1-0-core-update/InfiniBand-QoS/index.html)、[管理与 VL15 说明](https://docs.nvidia.com/networking/display/nvidia-infiniband-security-overview-and-guidelines.pdf)

## 信用怎样限制发送

对采用信用流控的数据 VL，下游通告可用接收资源，上游只能在获准范围内发送。下游释放资源并更新信用后，上游才获得新的发送机会。这样可以防止设计条件内因接收缓冲不足而溢出，但不能避免物理错误、端点退出或永久阻塞。

假设某 VL 下游已经满，上游即使物理链路空闲也可能不能发送。如果另一个 VL 有信用且获得仲裁，它可以使用链路。若两个业务映射到同一受阻资源，它们仍会相互影响。

## 路由与流控共同决定前进性

信用避免溢出，不自动消除循环等待。路由及 SL/VL 映射需要满足对应拓扑的前进条件。例如某些 torus 路由使用不同 SL/VL 避免信用依赖环，不能在不理解路由约束时任意覆盖 QoS 映射。[OpenSM 配置说明](https://docs.nvidia.com/networking/display/mlnxofedv23102131201lts/features-overview-and-configuration.pdf)

端到端拥塞管理还需要影响源端注入。链路信用与发送端调速的观察位置不同，因此不能说“有信用就不需要拥塞控制”。具体拥塞算法和自适应路由能力应固定到协议与产品版本。

## 计数器需要结合语义解释

XmitWait 增长可能与缺少信用或仲裁等待有关，不单独证明远端内存慢。VL15 丢弃则可能指向管理资源压力，不能用普通数据吞吐来解释全部现象。应同时检查端口流量、路径、队列和业务停顿。[端口计数器定义](https://docs.nvidia.com/networking/display/nvidia-ufm-enterprise-user-manual-v6-19-1-lts-2024-lts-u1.1%20LTS%20%282024%20LTS%20U1%29.pdf)
