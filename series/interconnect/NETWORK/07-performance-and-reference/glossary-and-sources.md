# 术语、版本与一手资料：怎样复核系统网络结论？

上级：[性能、诊断与查阅](README.md)

本专题按接口和协议职责解释机制。引用核查日期为 **2026-11-17**。在线文档会更新，复现实验应额外保存实际安装的软件、固件与设备版本。

## 核心术语

| 术语 | 本专题中的含义 |
| --- | --- |
| 消息／包／帧 | 应用或传输对象／网络传输单位／链路传输单位，需明确观察层 |
| NIC／HCA | 网络接口设备／InfiniBand 语境中的主机通道适配器 |
| QP／CQ | 队列对与传输状态／工作完成队列 |
| MR／PD | 注册内存范围及属性／资源保护域 |
| lkey／rkey | 本地／远端访问校验使用的密钥，不等同于加密密钥 |
| RC／UD | 可靠连接／不可靠数据报传输服务 |
| ECMP | 在等价路由路径中选择下一跳，具体散列由实现决定 |
| PFC／ECN／CNP | 按优先级暂停／显式拥塞标记／RoCE 拥塞通知包 |
| SL／VL | InfiniBand 服务等级／虚拟通道资源 |
| Incast | 多个发送者在时间上集中向一个接收方向汇聚 |
| Goodput | 按明确口径计算的应用有效数据速率 |
| UET | Ultra Ethernet Transport，不能直接等同于 RoCE |

## 资料按职责使用

| 来源 | 用于核对什么 | 版本与边界 |
| --- | --- | --- |
| [IEEE 802.3](https://standards.ieee.org/ieee/802/10422/) | Ethernet MAC 与 PHY 范围 | 基础标准与后续修订分开核对 |
| [IEEE PFC](https://1.ieee802.org/dcb/802-1qbb/) | 按优先级链路流控 | 不提供任意设备阈值 |
| [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html)、[RFC 3168](https://www.rfc-editor.org/rfc/rfc3168.html) | TCP、ECN 基础 | 具体算法还需对应文档 |
| [RFC 8257](https://www.rfc-editor.org/rfc/rfc8257.html)、[RFC 7938](https://www.rfc-editor.org/rfc/rfc7938.html) | DCTCP、数据中心路由实践 | 都不能作为所有网络的默认配置 |
| [IBTA](https://infinibandta.org/ibta-specification/)、[RDMA 编程手册](https://docs.nvidia.com/rdma-aware-networks-programming-user-manual-1-7.pdf) | IB、RoCE、传输与操作 | 手册 1.7 为软件机制参考，产品能力另核对 |
| [rdma-core](https://github.com/linux-rdma/rdma-core) | verbs API 与提供者实现 | master 是移动版本，实验需固定版本 |
| [DCQCN 原论文](https://www.microsoft.com/en-us/research/publication/congestion-control-for-large-scale-rdma-deployments/) | 控制算法与提出背景 | 2015 年实验条件不能当作当前硬件表现 |
| [GPUDirect RDMA](https://docs.nvidia.com/cuda/gpudirect-rdma/index.html) | GPU 内存映射与同步 | 检查设备、驱动及通信库适用范围 |
| [UE 1.1 规范](https://ultraethernet.org/wp-content/uploads/sites/20/2026/10/UE-Specification-1.1.pdf) | UE 软件、传输与链路职责 | profile 与可选特性不能混为统一必选能力 |
| [iperf3](https://software.es.net/iperf/invoking.html)、[perftest](https://github.com/linux-rdma/perftest) | 测试选项与指标 | 命令示例未在本专题执行硬件测量 |

## 三类结论分别记录

标准与接口定义支持机制事实；模型支持明确假设下的预算；硬件实验才能支持指定平台的实测性能。本专题的包率、队列、窗口和流量数字均为教学算例，没有进行 NIC/GPU 实测、故障注入或互操作认证。

仍需随具体平台验证的项目包括：拥塞阈值、PFC headroom、重排与重传策略、GPU 数据可见性接口、设备内部资源和 UE profile 支持。未公开实现不以推测补齐。

## 用反例自查

- ping 成功，为何 RDMA Write 仍可能因权限失败？回看[部署条件](../04-roce/deployment-and-isolation.md)。
- 两条 100 Gb/s 上行，为何一个流不一定得到 200 Gb/s？回看[ECMP](../02-ethernet-and-ip/clos-ecmp-and-rails.md)。
- 发送完成，为何不能证明远端 GPU kernel 已消费？回看[完成时序](../01-foundations/host-nic-data-path.md#completion)。
- 无损流控，为何仍不能保证应用永远前进？回看[PFC](../04-roce/pfc-headroom-and-stalls.md)与 [IB 信用](../05-infiniband/vl-credit-routing-and-congestion.md)。
