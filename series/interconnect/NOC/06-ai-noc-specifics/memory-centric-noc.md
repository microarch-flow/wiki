# Memory-centric NoC：存储端口怎样塑造网络？

上级：[06 AI NOC Specifics](./README.md)

相关：[NoC 与存储系统](../05-system-integration/noc-meets-memory-system.md)、[地址映射与路由表](../05-system-integration/address-map-and-routing-table.md)、[Decode 与 KV Cache](./workload-attention-decode-kv-cache.md)

<span id="memory-centric-noc"></span><span id="这页在回答什么问题"></span>当一组流量主要访问共享存储端点时，端口放置、地址映射和请求/返回资源会共同影响网络。这里比较系统组织；bank、controller 和反压的单路径机制见[NoC 与存储系统](../05-system-integration/noc-meets-memory-system.md)。

## 从一次访问到一组流

<span id="什么叫-memory-centric"></span><span id="request-和-response-的地位不对等"></span>读取包含从发起端到存储的请求，以及从存储到 consumer 的返回数据。哪一段位于关键路径，取决于请求窗口、服务时间、返回容量与后续计算依赖。不能一律认定 response 比 request 更重要。

<span id="哪些-workload-容易进入这种状态"></span>多个 tile 同时 refill、共享权重或读取 KV 数据，都可能集中访问少数端口；具体分布由数据放置和实际请求决定。Decode 的数据量和逐步依赖见[工作负载案例](./workload-attention-decode-kv-cache.md)。

## 两种放置的容量对照

<span id="为什么这不是单靠-hbm-带宽能解释完的"></span>构造两个不同对象 A、B 和两条持续读取流。每流提出每拍 1 个等大的数据单元；两个 memory port 各能每拍服务 1 个单元。假设请求路径和返回路径的总容量足够，两个 consumer 也都能每拍接收 1 个单元，没有其他竞争或固定启动延迟。

| 数据放置 | 每拍需求与端口容量 | 两流的服务上限 |
| --- | --- | --- |
| A、B 都在端口 0 | 端口 0 需求为 2，容量为 1；端口 1 空闲。 | 合计 1 单元/拍。 |
| A 在端口 0，B 在端口 1 | 两个端口各有 1 个需求，容量各为 1。 | 合计 2 单元/拍。 |

第二种放置在上述理想条件下能同时服务两流，但这不是实际系统必然加速两倍。若两条返回流共享容量为 1 的链路，或某个 consumer 每两拍只能接收一次，两端口也不能提供上述合计服务。

## 怎样比较候选组织

<span id="常见系统策略"></span>先固定逻辑访问和数据量，再改变地址映射、port 位置、请求/响应队列或仲裁。分别观察端口服务率、请求与返回路径负载、未完成请求、目的端等待和任务完成时间。

请求和响应分 class、提高部分流优先级、增加路径或端口，都只是候选方案。它们可能改善一种竞争，也可能增加资源或影响其他流；需要在相同约束和流量下比较。[多物理网络](../05-system-integration/multiple-physical-networks.md)进一步比较隔离方式。

<span id="建模启示"></span>模型需保留对象到端口的映射、每个方向的共享路径、服务能力和端点接收条件。平均总带宽不能替代各端口和关键依赖的观察。

<span id="一句话理解"></span>Memory-centric 分析关注多条访问如何汇聚并返回；先找到实际共享的端口和路径，再选择优化对象。
