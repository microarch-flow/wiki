# 加速器互连：多颗加速器怎样访问对端资源？

当一个任务分布在多颗加速器上，计算之外还要交换数据、等待对端结果，并协调资源使用。互连需要定义允许的操作、请求与返回路径，以及软件如何观察完成。物理连接只是其中一个条件。

本专题用六章建立从远端访问到多卡任务性能的理解路径。全文共 30 页：本导读、六篇章节导读和 23 篇正文。案例固定到明确协议或平台；教学预算与硬件测量分开说明。

## 六章分别解决什么

1. [访问语义](01-access-semantics/README.md)：访问需要哪些条件，哪些事件允许程序继续执行？本章从通信对象开始，建立地址、权限、操作和完成之间的关系。
2. [交换结构](02-fabric-architecture/README.md)：请求通过链路和交换节点到达目标，再带着结果返回。路径中的每个端点、队列和端口都可能限制吞吐或前进性。
3. [协议与系统案例](03-protocols-and-systems/README.md)：通用机制需要放回具体协议和产品配置。这里用 UALink、NVLink／NVSwitch 和 AMD xGMI 展示不同的事务、版本和拓扑组织。
4. [软件与集体通信](04-software-and-collectives/README.md)：硬件连接通过运行时和通信库向应用提供能力。程序必须先建立有效资源，再正确表达数据依赖和完成条件。
5. [负载与性能](05-workloads-and-performance/README.md)：互连的价值体现在任务完成时间。先从计算切分得到通信，再分析依赖和资源，最后选择能验证这些判断的指标与测试。
6. [建模、诊断与查阅](06-modeling-and-reference/README.md)：模型用于排除不可能的性能目标，测量用于检验真实系统，诊断用于解释二者的差距。三者需要共享同一套对象、单位与观察边界。

## 按目标选择阅读路线

- **建立机制理解**：访问语义 → 交换结构 → 软件与集体通信 → 负载与性能。
- **研究具体系统**：先读前两章，再选 UALink、NVLink／NVSwitch 或 AMD xGMI 案例，最后核对指标和测试条件。
- **分析任务瓶颈**：先明确完成边界，再读通信映射、TP／PP／DP、MoE、重叠和性能下界。

## 先看一条访问路径

假设 A 读取 B 的一段数据。系统先建立有效地址与访问权限；A 为请求保留上下文，经链路和交换结构到达 B；B 处理请求并返回数据；A 匹配返回，完成规定的数据交付。共享端口排队、目标内存服务和在途窗口都会影响时间。

这是构造案例。它不假设所有互连都支持同一操作，也不把返回、缓存可见性和消费者同步视为同一事件。详细过程见[远端读取](02-fabric-architecture/remote-read-path.md)，软件保证见[操作、排序与完成](01-access-semantics/operations-ordering-and-completion.md)。

## 以 UALink 200G 1.0 为例

UALink 200G 1.0 是本专题保留的标准案例。它面向 pod 内加速器与交换组件，公开说明了读、写、原子以及分离的请求／响应机制。[联盟概览](https://ualinkconsortium.org/blog/ualink-200g-1-0-specification-overview-802/)

[1.0 事务文章](03-protocols-and-systems/ualink-200g-transactions.md)解释分层职责；[规范组件文章](03-protocols-and-systems/ualink-specification-family.md)补充 Common 2.0、DL/PL、Chiplet 与 Manageability 的关系。规范能力不等于具体产品性能，相同速率也不等于协议互通。

## 与其他专题的关系

| 专题 | 主要职责 | 本专题如何衔接 |
| --- | --- | --- |
| [NoC](../NOC/README.md) | 路由、缓冲、流控和集体通信基础 | 复用基础推导，补多卡端点、软件与真实路径 |
| [PCIe](../PCIE/README.md) | 配置、地址、事务、DMA 与 P2P 平台条件 | 解释加速器对端访问及主机侧路径 |
| [一致性与内存互连](../COHERENCE/README.md) | 缓存副本、内存顺序、CHI 与 CXL | 核对具体加速器接口的保证范围 |
| [系统网络](../NETWORK/README.md) | Ethernet、RDMA、RoCE 与 InfiniBand | 连接多个通信域，承载域间流量 |
| [D2D](../D2D/README.md)、[SerDes](../SERDES/README.md)、[CPO](../CPO/README.md) | 封装内承载、物理信号和集成 | 提供物理基础，不单独决定上层访问语义 |

[推理运行时的并行基础](../../inference-runtime/07-distributed-execution/11-cluster-parallelism.md)解释 TP、PP、DP 的执行与状态布局；本专题进一步按具体通信量、时延、带宽和任务目标分析互连需求。

资料与验证范围见[术语、版本与一手资料](06-modeling-and-reference/glossary-and-sources.md)。
