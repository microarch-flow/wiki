# BUS vs NoC vs Point-to-Point

上级：[02 基础对象与事务语义](./README.md)

相关：[BUS 在解决什么问题](../01-overview/problem-statement.md)、[BUS 分类框架](../01-overview/taxonomy.md)、[NoC Wiki 首页](../../../NOC/wiki/README.md)、[PCIE Wiki: PCIE vs AXI / NoC：边界与分工](../../../PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)

## 这页在回答什么问题

为什么 BUS、NoC 和 point-to-point 都能被叫作“互连”，但它们解决的约束不同，不能按“谁更高级”来排序。

## 三者的分界不是线多线少

点到点链路、BUS、NoC 的差异不在“用了几根线”，而在连接关系和共享规则。

Point-to-point 把一个发起端和一个接收端直接连起来。连接关系固定，协议可以贴着这两个模块定制，延迟和带宽边界容易推断。代价是复用性弱：一旦第三个模块也要访问同一个目标，就需要额外 mux、仲裁或协议转换。

BUS 把多个 master 对多个 slave 的访问组织成 transaction。它的重点是统一地址语义、仲裁、返回匹配、顺序约束和错误响应。BUS 不一定是一根共享线；它可以由 shared bus、bus matrix、crossbar、bridge 和 adapter 组成。它的边界是：共享规则仍以 transaction 和软件可见地址空间为中心。

NoC 把互连进一步拆成分布式网络：节点通过 router、link、packet/flit、credit、route 和 buffer 组织通信。它的重点是大规模空间分布、多跳路径、局部流控和拓扑可扩展性。代价是端到端延迟更难一眼推断，路由、死锁、QoS、buffer sizing 和验证复杂度都会进入设计主路径。

所以这三者不是代际替换关系，而是不同约束下的组织方式。一个 SoC 可以同时用 point-to-point 做局部专线，用 BUS 做控制和事务骨架，用 NoC 做大规模数据交换。

## Point-to-Point 适合固定关系

Point-to-point 的强项是把不需要共享的路径做简单。两个模块之间的带宽、时序和协议语义都可以被定制：producer 到 consumer 的 streaming path、固定 DSP pipeline、一个 controller 到专用 SRAM、一个 accelerator 内部的本地数据通路，都可以不引入全局地址 decode 和复杂仲裁。

它的设计交易很明确：用低通用性换低延迟、低面积和可预测行为。只要连接两端的角色稳定，点到点链路就不需要回答“第三个 master 怎么访问”“response 怎么路由给不同发起者”“不同 slave 的地址如何统一编址”这些问题。

问题会在需求变化时出现。一个本地 SRAM 如果后来既要被 CPU 配置，又要被 DMA 搬运，又要被 debug master 访问，点到点连接就会开始堆 mux、arbiter 和地址窗口。此时它已经在向 BUS 的问题域移动，只是没有显式承认自己需要事务组织层。

容易误解：点到点一定低级。实际上，在固定低延迟路径中，点到点可以是性能最强的局部专线；它不弱，只是不负责共享访问和软件可见地址空间。

## BUS 适合共享事务语义

BUS 的强项是把共享访问变成可管理的 transaction。CPU、DMA、debug master、外设控制器访问同一批 memory-mapped slave 时，系统需要统一地址空间、decode、权限、仲裁、响应、错误和 timeout。BUS 给这些行为一个共同框架，让硬件、firmware、driver 和调试工具能用同一套语义描述访问。

这也是 BUS 长期存在的原因。控制面、寄存器面、boot/debug 路径、DMA 到 memory 的事务入口，都需要“谁访问了哪个地址、访问是否完成、错误如何返回、顺序如何约束”这些答案。点到点链路可以很快，但它不天然提供这些共享语义；NoC 可以承载更大规模通信，但边界处仍然要把包、路由和 credit 行为映射回软件能理解的事务或消息。

BUS 的代价来自集中语义。地址 decode、仲裁、返回匹配和保序规则让系统可控，也会制造共享瓶颈。master/slave 数量上升后，单共享仲裁点会变成全局串行化；crossbar 和 matrix 可以释放不同路径的并行度，但面积、布线、时序和验证复杂度随端口数上升。

容易误解：BUS 就是低性能共享线。实际上，BUS 是事务语义的组织方式；实现可以从简单 APB 子树到高并发 AXI crossbar，差异来自系统角色和并发压力。

## NoC 适合大规模空间分布

NoC 的强项是把通信压力分散到多跳网络里。当节点数量多、物理距离大、数据流分布在多个 tile、SRAM bank、DMA、HBM port 或 compute cluster 之间时，继续用一个集中 fabric 会遇到布线、时序和全局仲裁问题。NoC 用 router 和 link 把全局问题拆成局部转发问题。

这种拆分换来可扩展性，也引入新的状态。一个 packet 会被切成 flit，经过多个 router，受 virtual channel、credit、buffer、allocator 和 routing policy 影响。单个 transaction 的延迟不再只由一个仲裁器决定，而是由每跳争用、路径选择、下游 credit 和目的端服务共同决定。

NoC 更适合大规模数据面，不代表它只搬“无语义数据”。AI tile dataflow、collective、multicast、DMA 到 HBM、SRAM bank 间交换，都可能需要 NoC；CPU coherent NoC 还会承担 cache coherence 相关语义。区别在于 NoC 的核心问题变成拓扑化通信和分布式流控，而不是单一地址总线上的事务组织。

一个实用边界是：当 bus matrix 或 crossbar 的端口数、长距离布线、全局时序和集中仲裁已经成为主成本，而流量又能被拆成多个空间分布的局部转发问题时，NoC 才开始比继续扩大集中 fabric 更有吸引力。若节点数量有限、访问仍围绕少数 memory-mapped slave，matrix 或 crossbar 可能仍是更低成本的答案。

容易误解：有 NoC 就不需要 BUS。实际上，在带 MMIO 边界或软件控制面的 NoC 系统中，边缘仍需要 BUS/MMIO 风格接口来完成配置、状态读取、doorbell、interrupt 和 debug；NoC 负责大规模传输，BUS 负责软件可见事务边界。

## 选型要看三类约束

第一类约束是连接关系。固定一对一或少数固定 producer/consumer，point-to-point 更直接。多个 master 访问共享 slave，BUS 的事务语义更合适。节点数量多、物理分布广、路径组合多，NoC 才开始体现价值。

第二类约束是软件可见性。如果访问对象是寄存器、状态位、doorbell、interrupt controller 或 memory-mapped buffer，软件需要清楚的地址、完成和错误语义，BUS 更容易表达。如果通信主要来自编译器调度的数据流、tile 间消息或 bulk data movement，NoC 或专用链路可以把软件语义放在更高层。

第三类约束是扩展成本。Point-to-point 的成本随连接数膨胀；BUS 的成本随共享端口、仲裁点、返回路径和时序压力膨胀；NoC 的成本随 router 数、buffer、credit、routing、deadlock avoidance 和可观测性膨胀。没有一种组织方式免费扩展，只是成本曲线不同。

一个 SoC 内部分工可以写成这个构造示例：

| 路径 | 更自然的组织 | 主约束 | 主要风险 |
|---|---|---|---|
| CPU 配置外设寄存器 | BUS | 软件可见地址和错误语义 | 低速外设拖慢控制路径 |
| DMA 搬运连续内存块 | BUS / NoC | 持续带宽和 outstanding | 长 burst 压制短请求 |
| AI tile 间 activation 交换 | NoC | 多节点并发和空间分布 | credit、buffer、热点和死锁 |
| 固定 accelerator 内部流水 | Point-to-point | 低延迟和固定带宽 | 后续共享需求导致重构 |
| Debug / boot 可达性 | BUS / 简单专线 | 初始化前可访问 | 依赖复杂 fabric 导致 bring-up 困难 |

这张表不是选型规则表，而是提醒：同一芯片里不同路径可以有不同答案。把所有通信统一成一种互连，会让低复杂度路径承担过度设计成本，也会让高并发路径缺少扩展空间。

## 和板级 I/O 互连的边界

BUS、NoC 和 point-to-point 在这里讨论的是片内连接。它们关注的是 SoC 内部 agent、slave、地址空间、事务响应、片上流控和微架构实现。

如果问题变成 host 与 device 之间的板级或封装外 I/O，例如 PCIe endpoint、CXL device、NVMe、NIC、GPU 与 CPU host 的连接，核心约束就会变成链路训练、packet/TLP、枚举、BAR、DMA、cache coherency 或 I/O memory model。此时应该切到 [PCIE Wiki](../../../PCIE/wiki/README.md) 或对应 I/O 互连视角，而不是把片内 BUS 经验直接套过去。

## 一句话理解

Point-to-point 解决固定专线问题，BUS 解决共享地址和事务语义问题，NoC 解决大规模分布式通信问题；三者不是谁替代谁，而是在同一系统里承担不同约束。

## 建模启示

建模时不要先问“这是 BUS 还是 NoC”，而要先记录连接关系：端点数量、是否共享目标、是否需要统一地址空间、是否有返回匹配、是否存在多跳路径、是否需要软件可见 completion。连接关系决定模型里要放 mux、arbiter、queue、router、credit，还是简单 service edge。

Point-to-point 模型可以压得很轻：在固定端点、固定服务路径和局部流控条件下，固定 latency、固定吞吐、局部 backpressure、少量 buffer 就能表达主要行为。只要没有共享目标和可变路由，就不需要引入全局仲裁和 response matching。

BUS 模型至少要保留 transaction 状态：address decode、仲裁点、burst beat、outstanding、ordering、response 和 backpressure。它的性能风险来自共享资源和事务闭环之间的等待时间。

NoC 模型必须显式保留网络状态：packet/flit、router pipeline、link 带宽、buffer/credit、routing policy、virtual channel 或 deadlock avoidance 约束。它的性能风险来自每跳争用、热点、路径选择和分布式流控。

最危险的简化是用名称替代约束。例如把 NoC 边缘的 MMIO 配置路径当作普通数据包流，会丢掉软件可见 completion；把一个固定 accelerator 内部专线建成完整 BUS，会把模型复杂度放错地方；把高并发 tile 数据面压成单共享 BUS，会低估热点、路径和多跳 backpressure。
