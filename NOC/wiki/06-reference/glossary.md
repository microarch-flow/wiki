# 术语表

上级：[06 术语与检查清单](./README.md)

## 基础对象

- `Node`：接入 NoC 的计算、存储或 I/O 模块
- `Router`：负责 packet / flit 转发的网络节点，内部包含 input buffer、crossbar、allocator 和控制逻辑
- `NI`：Network Interface，endpoint 与 NoC 的协议转换与注入/弹出接口；endpoint 可以是 tile、DMA、HBM port、共享 SRAM 节点等
- `Link`：router 之间的数据通路，物理上是一组信号线，每周期可传输一个 phit
- `Tile`：AI 加速器中的基本计算单元，通常包含 MAC 阵列、本地 SRAM 和控制逻辑；多个 tile 通过 NoC 互连构成完整的计算阵列
- `Crossbar`：router 内部的全连接交换矩阵，在每个周期根据 allocator 的结果将某个 input port 的 flit 送到对应的 output port
- `Endpoint`：NoC 中的数据源或数据目的地，如 tile、HBM 端口、DMA 引擎等
- `Source`：一笔通信的发送端；可以是 tile、DMA、memory node 或控制单元
- `Sink`：一笔通信的接收端；在 many-to-one 流量里通常是最容易形成热点的一侧
- `Memory node`：承接存储请求的网络端点，如共享 SRAM 组、HBM controller port 或专用 memory tile

## 传输单位

- `Packet`：一次完整通信事务的语义单位，包含 header（路由信息）、body（有效载荷）和 tail（结束标记）
- `Flit`：flow control unit，router 流控和仲裁的基本单位；一个 packet 由多个 flit 组成，flit 是 buffer 分配和 credit 计数的粒度
- `Phit`：physical transfer unit，物理链路每周期实际传输单位；当 link 宽度与 flit 宽度相同时 phit = flit，否则一个 flit 需要多个周期传完
- `Header flit`：packet 的第一个 flit，携带目的地址、路由信息和消息类型等控制字段
- `Body flit`：packet 中间的 flit，承载有效载荷数据
- `Tail flit`：packet 的最后一个 flit，标记 packet 结束，释放沿途占用的 VC 和路由资源

## 控制与资源

- `VC`：Virtual Channel，共享物理链路的逻辑队列；多个 VC 共享同一条物理 link，但各自独立维护 buffer 和 credit，从而减少 HOL blocking 并支持消息类型隔离
- `VN`：Virtual Network，更高一级的逻辑网络隔离；常用于按协议或消息类型分隔流量。它通常提供较强隔离，但是否完全物理独立、是否完全无资源耦合，取决于具体实现
- `Credit`：下游剩余 buffer slot 的计数；发送方每发出一个 flit 消耗一个 credit，下游释放 buffer slot 后返回一个 credit
- `Credit round-trip`：从发送一个 flit 到收回对应 credit 所经过的周期数，决定了 buffer 深度的最低需求
- `Backpressure`：由于下游阻塞导致的反向停发传播；当下游 buffer 满（credit 耗尽）时，上游被迫暂停发送，这种停顿会沿路径逐跳向上游蔓延
- `HOL blocking`：Head-of-Line blocking，队头阻塞；当 FIFO 队列头部的 flit 因目的端口被占而无法前进时，排在后面的、去往其他端口的 flit 也被堵住
- `Flow control`：流量控制，协调发送方和接收方速率的机制，确保接收方 buffer 不溢出；常见形式有 ready/valid 握手和 credit-based 两种
- `Ready/Valid`：一种简单的握手式流控协议，发送方通过 valid 信号表示数据有效，接收方通过 ready 信号表示可以接收；适合短距离、低延迟场景
- `Credit stall`：因 credit 耗尽（下游 buffer 已满）导致发送方无法继续发 flit 的停顿
- `Switch stall`：因 crossbar 端口被其他 flit 占用（arbitration 竞争失败）导致的停顿
- `Traffic class`：按优先级、语义或延迟敏感性分组的一类流量，如 control、response、bulk DMA
- `Plane`：彼此隔离的一组物理或逻辑传输资源；常用来把不同 traffic class 放到不同网络平面上
- `Memory request`：从计算端或 DMA 侧发往 memory node 的请求类流量，如 read request、某些 write request
- `Memory response`：从 memory node 返回消费者的响应类流量；在 decode-like 场景里常更接近关键路径
- `Bulk DMA`：以吞吐为主、包较长、持续时间较长的大块 DMA 数据流量

## Router 流水线

- `RC`：Route Computation，路由计算阶段；header flit 到达后根据目的地址计算应走的 output port
- `VA`：Virtual channel Allocation，VC 分配阶段；为 packet 分配下游 router 的一个空闲 VC（整个 packet 生命周期内持续占用）
- `SA`：Switch Allocation，交换分配阶段；每个周期为竞争同一 output port 的多个 flit 进行仲裁，获胜者获得 crossbar 通路
- `ST`：Switch Traversal，交换穿越阶段；flit 实际穿过 crossbar 到达 output port
- `LT`：Link Traversal，链路穿越阶段；flit 在物理 link 上传输到下游 router

## 路由与切换

- `Topology`：网络连接结构，定义了 router 之间如何互连，决定了 hop 数、bisection bandwidth 和布线复杂度
- `Mesh`：二维网格拓扑，每个 router 与上下左右四个邻居相连；结构规则、与芯片 floorplan 天然兼容，是 AI 加速器最常用的 baseline 拓扑
- `Torus`：在 mesh 基础上增加环绕边（wrap-around link），使边缘节点也能直连对边节点，减少平均 hop 数和边缘效应，但引入长距离物理连线
- `Ring`：环形拓扑，每个 router 只有两个邻居；结构最简单，适合小规模集群或控制网络，带宽随节点数增加而恶化
- `Tree`：树形拓扑，天然适合聚合（reduce）和分发（broadcast）流量，但根节点容易成为瓶颈
- `Fat-Tree`：增强的树形拓扑，越靠近根节点的链路带宽越大，缓解上层瓶颈；常见于数据中心，在片上因布线开销大而较少使用
- `Hierarchical NoC`：层级化互连，将系统分为 cluster 内部的局部网络（如 crossbar 或小 mesh）和 cluster 之间的全局网络，利用 AI workload 的数据局部性减少全局流量
- `Flat mesh`：没有显式层级划分的扁平 mesh；大多数 tile 直接挂在同一层全局网络上
- `Routing`：为 packet 选择路径的方法
- `Deterministic routing`：确定性路由，相同源-目的对始终走相同路径；最简单、最可预测，但不能避开拥塞
- `Dimension-order routing`（XY routing）：先沿 X 方向走完再沿 Y 方向走，是 mesh 上最常用的确定性路由；天然无死锁（不存在路由环路）
- `Source routing`：源端路由，路径由发送端（通常是编译器/runtime）预先计算并编码在 packet header 中，router 只需解码下一跳方向，无需路由表
- `Adaptive routing`：自适应路由，根据网络实时拥塞状况动态选路；可均衡负载，但增加 router 复杂度和死锁风险
- `Turn model`：一种限制路由转弯方向来保证无死锁的方法，如 West-First、North-Last 等；通过禁止特定转弯组合来打破循环依赖
- `Escape VC`：一种死锁恢复/预防技术，保留一个专用 VC 使用无死锁路由（如 XY），其他 VC 可使用自适应路由；当自适应路由陷入死锁时，packet 可转入 escape VC 逃脱
- `Arbitration`：多个请求竞争一个资源时的选择机制
- `Round-robin`：轮询仲裁，各请求者按固定顺序轮流获得优先权，保证公平性
- `Weighted round-robin`：加权轮询，不同请求者按权重获得不同比例的服务机会
- `Age-based`：按年龄仲裁，等待时间最长的请求优先获得服务，防止 starvation
- `Wormhole`：header 牵引 body/tail 逐跳流水前进的 switching 模式；所需 buffer 极小（仅需存放少量 flit），但被阻塞时会占住沿途所有 link
- `Store-and-forward`：存储转发，router 需要接收完整个 packet 后才开始转发；buffer 需求大（packet 级），延迟高，但不会跨 hop 占路
- `Virtual cut-through`：虚拟直通，与 store-and-forward 类似但当下游有足够空间时可在收完整 packet 前开始转发；buffer 需求仍为 packet 级
- `Injection`：将 packet / flit 从某个 endpoint 通过本地接口注入到 NoC
- `Ejection`：将到达目的地的 packet / flit 从 NoC 弹出到目的 endpoint 的本地接口
- `Hop`：flit 从一个 router 到相邻 router 的一次传输，hop count 是衡量路径长度的基本度量
- `Diameter`：网络中任意两个节点间最大 hop 数
- `Bisection bandwidth`：将网络平分为两半时，横跨切面的所有 link 的总带宽；衡量网络承载全局流量的能力
- `Router radix`：router 的端口数量（包括本地端口和到其他 router 的端口），radix 越大硬件复杂度越高
- `Concentration`：每个 router 挂接多少 endpoint / tile；它会影响 router radix、平均 hop、局部拥塞和布线长度
- `Fan-in`：多个流量源朝少数目的地汇聚的结构特征，常导致 sink 侧热点
- `Fan-out`：单个源向多个目的地扩散的结构特征，常导致源附近路径重复占用

## 性能与风险

- `Latency`：从注入到送达的延迟
- `Throughput`：单位时间完成的数据传输量
- `Saturation point`：网络从近线性增长进入明显拥塞的转折点，注入速率超过此点后延迟急剧上升
- `Tail latency`：延迟分布的高百分位值（如 P99、P99.9），反映最坏情况性能；对 AI 推理的 step latency 影响极大，因为最慢的 tile 决定整体速度
- `Deadlock`：资源循环等待导致无前进状态；如四个 packet 各自占住一个 buffer 并等待对方释放，形成环路
- `Livelock`：持续移动但长期无法到达目的地（例如在 adaptive routing 中被反复绕远）
- `Starvation`：某类请求长期得不到服务（如高优先级流量持续占用仲裁，低优先级被饿死）
- `Forward progress`：系统保证所有合法请求最终都能完成的性质；无死锁 + 无饿死 = 有 forward progress
- `Link utilization`：某条 link 在观察时间内实际传输 flit 的周期占总周期的比例
- `Injection rate`：每个 endpoint 每周期注入 NoC 的 flit 数量（或等效带宽）
- `QoS`：Quality of Service，服务质量保证；通过 VC 隔离、仲裁权重、带宽预留等手段，确保关键流量的延迟和带宽不被低优先级流量抢占
- `Critical path`：决定下一步计算或事务能否继续推进的关键依赖路径
- `Bottleneck`：最先限制系统吞吐或时延表现的资源、链路或端点
- `Hotspot`：流量长时间集中压在少数 link、router 或 endpoint 上形成的热点现象
- `Stall breakdown`：把停顿按原因分类统计后的结果，如 `NO_CREDIT`、`EJECTION_BLOCKED`、`WAITING_FOR_OTHER_STREAM`
- `First-order insight`：不追求极致精度，但足以解释主要瓶颈和方向性 tradeoff 的一阶架构结论
- `Validity boundary`：结论成立所依赖的前提边界；当 workload、mapping、traffic class 或模型层次变化时，结论可能失效

## 存储与接口

- `SRAM`：Static Random-Access Memory，片上静态存储器；AI 加速器中用作 tile 本地的权重/激活值缓存，访问延迟通常为 1-2 周期
- `HBM`：High Bandwidth Memory，高带宽存储器；通过 3D 堆叠封装提供极高带宽（通常 1-4 TB/s），是 AI 加速器的主要外部存储，但延迟远高于 SRAM
- `DMA`：Direct Memory Access，直接内存访问引擎；tile 通过 DMA 发起对远端 SRAM 或 HBM 的读写请求，无需 CPU 介入，以 burst 方式高效搬运数据
- `Burst`：DMA 或存储控制器一次连续传输的多个数据单元；burst size 影响 NoC packet 大小和带宽利用率
- `Scratchpad`：一种软件管理的片上 SRAM，与 cache 不同，数据的加载和替换完全由编译器/程序控制，无硬件自动替换策略
- `Bank conflict`：多个并发访问请求命中 SRAM 的同一个 bank 时产生的资源冲突，导致访问串行化和额外延迟
- `Outstanding request`：已发出但尚未收到响应的请求；outstanding request window 的大小决定了能否隐藏访存延迟
- `Double buffering`：双缓冲技术，使用两块 buffer 交替工作——一块正在被消费（计算使用），另一块正在被填充（DMA 搬入新数据），从而隐藏数据搬运延迟
- `Floorplan`：芯片的物理布局规划，决定各模块（tile、SRAM、router、HBM 端口）在硅片上的位置，直接影响 link 长度和布线可行性
- `Reassembly`：把多个 flit 或多个 response fragment 重新拼成完整 packet / 数据块的过程
- `Refill`：把数据从远端 memory 搬回本地 SRAM / cache / scratchpad 的动作
- `Eviction`：本地存储空间不够时，把旧数据写回远端或挪出的动作
- `Overlap`：让通信与计算在时间上并行，以隐藏访存或传输延迟

## AI / 深度学习

- `GEMM`：General Matrix Multiply，通用矩阵乘法；深度学习中全连接层和卷积层的核心计算操作，通常是 AI 加速器中的主要算力消耗
- `Activation`：激活值，神经网络中每一层的中间计算结果；需要在层间传递，是 NoC 上 tile-to-tile 流量的主要来源之一
- `Weight`：权重，神经网络的可学习参数；推理时从 HBM 加载到 tile 本地 SRAM，是 HBM-to-tile 流量的主要来源
- `Partial sum`：部分和，矩阵乘法中由不同 tile 计算的局部结果，需要通过 reduce 操作汇聚得到最终结果
- `KV Cache`：Key-Value Cache，Transformer 推理 decode 阶段缓存的历史注意力键值对；随序列长度线性增长，decode 时每个 token 都需要读取全部 KV cache
- `Prefill`：Transformer 推理的第一阶段，处理整个输入 prompt；计算密集、高并行度、大批量数据移动，瓶颈通常在 compute 和 HBM 带宽
- `Decode`：Transformer 推理的第二阶段，逐 token 自回归生成；batch 小、对延迟极敏感，瓶颈通常在 memory 带宽和 NoC 响应延迟
- `Step latency`：decode 阶段生成一个 token 所需的时间，直接决定用户感受到的生成速度
- `MoE`：Mixture of Experts，混合专家模型；每个 token 只激活部分 expert（子网络），引入动态的 many-to-many dispatch 和 gather 流量模式
- `Expert`：MoE 架构中的独立子网络，每个 expert 通常映射到不同的 tile 或 tile 组
- `Token`：Transformer 模型处理的基本文本单元（如一个词或子词），也指 decode 阶段每步生成的一个输出单元
- `Attention`：注意力机制，Transformer 的核心组件，通过 Query × Key 计算注意力权重，再对 Value 加权求和；计算量随序列长度平方增长
- `Weight-stationary`：一种数据流映射策略，将权重固定在 tile 本地 SRAM 中，让激活值流经各 tile；减少权重搬运但需要 activation 在 tile 间流动
- `Output-stationary`：一种数据流映射策略，将输出结果固定在 tile 本地累加，权重和激活值都流入；减少 partial sum 搬运
- `Mapping`：将工作负载（如矩阵乘法的分块）分配到硬件资源（tile、SRAM、NoC 路径）的策略，直接决定 NoC 上的流量分布
- `Placement`：将逻辑计算单元或数据块映射到物理 tile / SRAM bank 位置的过程，影响 hop 数和热点分布
- `Compute utilization`：计算利用率，tile 实际执行有效计算的周期占总周期的比例；NoC 瓶颈会导致 tile stall，降低 compute utilization
- `Workload`：真实要执行的模型、算子序列和数据依赖集合；NoC 建模的输入主语
- `Event`：一次有语义的通信动作，如 read request、tile-to-tile stream 或 barrier
- `Flow`：一类持续或成组出现的通信，可由多个 packet 组成
- `Trace`：按时间顺序组织好的 event、packet 或 flit 序列，供 simulator 直接消费
- `Response isolation`：把关键响应流量和 bulk 流量分开，以避免 response 被长包或背景流量压住

## 集合通信

- `Broadcast`：一对多通信，一个源将相同数据发送给所有目的节点
- `Multicast`：一对部分多通信，一个源将相同数据发送给一组特定的目的节点（broadcast 的子集）
- `Reduce`：多对一汇聚计算，多个源节点的数据在传输过程中逐步合并（如求和），最终在一个目的节点得到聚合结果
- `Gather`：多对一数据收集，多个源节点将各自的数据发送到一个目的节点，但不做计算合并
- `Scatter`：一对多数据分发，一个源将不同的数据片段分别发送给不同的目的节点
- `All-reduce`：所有节点都参与 reduce，且最终结果广播回所有节点
- `All-to-all`：每个节点都向其他所有节点发送不同的数据，通信量最大的集合操作模式
- `All-gather`：所有节点都把自己的数据分发给其他所有参与者，但不做归约运算
- `Barrier`：栅栏同步，所有参与节点必须都到达 barrier 点后才能继续执行；用于阶段间同步
- `Descriptor`：描述一次 DMA 传输或通信操作的控制数据结构，包含源地址、目的地址、传输长度、消息类型等信息

## 拓扑与组织

- `Concentrated mesh`：多个 tile 共享一个 router 的 mesh 变体，减少全局 router 数量，以增加 router radix 为代价换取更少 hop
- `Crossbar`：交叉开关，全连接的单级交换结构；小规模内单跳零等待，但面积随端口数平方增长
- `Cluster`：一组物理相邻的 tile 及其局部互连（如 local crossbar 或小 mesh），是层次化 NoC 的基本分组单位
- `Overlay network`：叠加在 base NoC 之上的专用通信结构，如 reduction tree、broadcast tree，服务特定通信模式
- `Multi-network`：多物理网络设计，不同 traffic class 走不同的物理独立网络，如 data NoC + control NoC + reduction NoC
- `Chiplet`：可独立制造的小芯片，多个 chiplet 通过封装互连组成完整系统
- `Die-to-Die (D2D)`：跨越两个独立 die 之间的互连，延迟通常是片上 NoC 的 10-50 倍
- `Interposer`：芯片之间的中间层基板，提供 die 间短距离高密度互连
- `Gateway`：多 die 系统中 NoC 与 D2D link 之间的协议转换节点

## Source Routing 与编译器

- `Per-hop encoding`：source routing header 中为每一跳编码方向（N/S/E/W/Local），每跳 2-3 bit
- `Segment encoding`：将连续同方向跳压缩为 (direction, hop_count) pair，减少 header 开销
- `Route table index`：header 携带 route_id，router 查本地表输出 port，适合路径复用场景
- `Dateline`：torus 中用于打破 wrap-around 死锁的虚拟分界线，packet 穿越 dateline 时必须切换 VC
- `In-network compute`：在网络传输过程中对数据做计算（如 partial sum 累加），减少端点汇聚压力
- `Cost model`：编译器用来评估 placement/routing/scheduling 方案优劣的量化模型，从 L0 hop-count 到 L3 cycle-approximate 精度递增

## 地址与存储映射

- `Address map`：地址空间到物理资源的映射表，定义访问某地址应路由到哪个物理节点
- `Address decode`：NI 或 router 中根据地址判断目的节点的硬件逻辑
- `Interleaving`：将连续地址交替分配到不同 bank/port/channel，分散访问压力
- `Striping`：类似 interleaving，按固定粒度轮转分配地址到不同资源

## 功耗与面积

- `Dynamic power`：电路切换活动产生的功耗，与数据流量和翻转率成正比
- `Leakage power`：即使不切换也因漏电流消耗的功耗，与面积和工艺相关
- `Wire energy`：信号在长线上传播消耗的能量，与线长和负载电容成正比
- `Energy per flit`：一个 flit 穿越一跳所消耗的总能量（buffer 读写 + crossbar + link driver）
- `Pareto front`：在多目标优化中，无法在一个目标上改善而不恶化另一个目标的解的集合

## CPU 一致性相关（对照）

- `Cache coherence`：缓存一致性协议，确保多个 cache 副本对同一地址的数据保持一致；典型协议有 MOESI、MESIF 等
- `Snoop`：嗅探，一致性协议中向其他 cache 发出的查询/无效化消息，用于检查是否持有某地址的副本
- `Invalidate`：无效化，一致性协议中通知其他 cache 将某地址的副本标记为无效
- `Request / Response / Snoop`：CPU coherent NoC 中的三大消息类别，通常需要分配到不同的 VN 以避免协议死锁
- `Home agent / LLC`：一致性系统中负责目录或最后一级缓存管理的节点，很多 request 会先到这里再触发后续事务
- `Ordering`：事务到达和生效的先后顺序约束；在 CPU coherent NoC 中通常是协议正确性的一部分
- `Atomicity`：一次事务对外表现为“不可被中间状态打断”的性质；它常要求 NoC 支持特定的顺序与隔离
