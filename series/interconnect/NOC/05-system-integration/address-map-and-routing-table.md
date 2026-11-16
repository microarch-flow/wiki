# 地址怎样映射到端点和路径？

上级：[05 端点与系统集成](./README.md)

相关：[网络接口 NI](./ni-network-interface-design.md)、[事务拆分、顺序与完成](./transaction-ordering-and-completion.md)、[Source Routing](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)

<span id="address-map-and-routing-table"></span><span id="这页在回答什么问题"></span>一次内存访问需要先确定**访问哪个资源**，再确定消息怎样经过网络。数据放置、地址映射和选路相互影响，但它们不是同一张表。

## 从地址到目的端

<span id="地址空间最终要落到物理-node"></span>请求可能先使用设备地址，再由可选的 IOMMU 或其他映射转换；系统随后按地址和访问属性选择目标资源。设备地址不一定等于 CPU 物理地址，也不是每个系统都具有 IOMMU。[Linux DMA 地址说明](https://docs.kernel.org/core-api/dma-api-howto.html)

<span id="ni-decode-和-router-decode"></span><span id="routing-table-不是孤立存在的"></span>在一种设计中，源 NI 将地址解析为目的节点，再由路由规则选择输出；另一种设计可以在网络或后续桥中继续解码。网络或类别也可能由请求类型、权限或配置选择，不一定只由地址决定。

## 交错映射能怎样改变流量

<span id="address-map-为什么会决定热点"></span><span id="interleaving-是典型的系统级调压手段"></span>构造一个四端口区域。区域起始地址为 0，按 64 B stripe 轮转；只对区域内有效地址使用：

> 端口 = ⌊地址 ÷ 64 B⌋ mod 4。

| 访问地址 | 目的端口 |
| --- | --- |
| 0 B | 0 |
| 64 B | 1 |
| 128 B | 2 |
| 192 B | 3 |

若访问地址依次为 0、256、512 B，则都落到端口 0。均匀交错没有保证任意步长的流量均匀；实际并行度还取决于地址范围、服务速率和连接路径。改变粒度可能改善某些并发，也可能改变局部性和重组开销。

## 跨目标请求怎样处理

假设实现允许将一次读取拆到不同端口：从地址 32 B 读取 96 B，可以分为端口 0 上的地址 32–63 B 和端口 1 上的地址 64–127 B。分片、响应匹配和交付仍须满足上层接口与属性；也有系统在后续控制器内部完成交错，不一定由源 NI 拆分。

不能把该例推广为任意 MMIO、原子或独占操作都可拆分。错误、访问权限、未对齐和协议边界也需按具体接口检查。AMD 文档描述了其 NMU 按控制器交错粒度处理事务的实现。[AMD NMU](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Master-Unit)

## 映射更新与在途事务

<span id="deterministic-npu-为什么更依赖它"></span><span id="它和多网络的关系"></span>修改地址映射或 route table 前，要明确哪些包携带已解析目的、哪些会在途中继续查表。一种方案是停止相关新请求并排空旧事务；另一种方案使用版本标识，并在所有旧版本引用完成之前保留相应映射。错误或超时后的迟到响应也要纳入释放规则。

<span id="常见误区"></span>交错不自动用满所有链路；固定 route 也不自动保证目标地址映射稳定。修改任一规则后，要重新检查允许路径、端点和事务顺序。

<span id="建模启示"></span>记录地址域、区域规则、目标端点、类别、路由选择及映射版本。按实际请求地址展开访问，再统计各端口和共享链路的负载；DRAM 内部映射见[存储控制器地址映射](../../../storage/04-dram-controller/address-mapping-channel-rank-bank-row-col.md)。

<span id="一句话理解"></span>地址映射决定访问落点；路由决定怎样到达落点。二者共同影响流量，但需要分别定义和验证。
