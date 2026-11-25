# 芯片与系统互连 · 逐页内容去向

从系列第一课的主机读请求开始，可以一路追到片上 SRAM，也可以在片内网络、封装边界或收发电路处停下来深读。这份索引列出九个专题的公开入口、现行正文和保留的旧网址，供核对合并前后某个知识点的落处。

## 九个专题从哪里读起

| 专题 | 首读 | 读完可以检查什么 |
| --- | --- | --- |
| [片上事务与总线](https://microarch-flow.github.io/wiki/BUS/wiki/) | [地址已经收下，数据为什么还没回来？](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/transaction-address-data-response/) | 沿八个时钟沿区分接地址、出数、交付 42。 |
| [片上网络](https://microarch-flow.github.io/wiki/NOC/wiki/) | [一次读取怎样变成 NoC 里的请求包和返回包？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/ni-network-interface-design/) | 从桥的同一笔读找到 NI、请求包、返回包和标识。 |
| [封装内芯粒互连](https://microarch-flow.github.io/wiki/D2D/wiki/) | [一次跨芯粒的寄存器读，什么时候才算完成？](https://microarch-flow.github.io/wiki/D2D/wiki/ucie-pcie-read/) | 把一次 32 位读的物理通道与协议完成放到同一张图。 |
| [系统 I/O 互连](https://microarch-flow.github.io/wiki/PCIE/wiki/) | [一次跨桥读取：设备已经收到请求，主机为什么还在等？](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary/) | 全系列第一课。先从已配置好的卡读取 42，另一条入口从上电枚举和 BAR 分配开始。 |
| [一致性与内存互连](https://microarch-flow.github.io/wiki/COHERENCE/wiki/) | [内存里还是 0，为什么 B 能读到 A 写的 1？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-invariants/) | 只跟一条缓存行，区分数据最新值和写权限。 |
| [加速器互连](https://microarch-flow.github.io/wiki/SCALEUP/wiki/) | [GPU A 能访问 GPU B 的地址，什么时候才能读？](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/address-mapping-and-permissions/) | 沿一块对端缓冲判断映射、可读、用完和释放。 |
| [系统网络](https://microarch-flow.github.io/wiki/NETWORK/wiki/) | [同样发 4 KiB，TCP 和 RDMA 什么时候能复用缓冲区？](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/host-nic-data-path/) | 跟踪 4096 字节在主机 A 和 B 的两端完成。 |
| [高速电链路](https://microarch-flow.github.io/wiki/SERDES/wiki/) | [一个 32 位字怎样穿过 SerDes，又怎样拼回来？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/) | 尝试把接收端的字边界挪一位，再还原 32 位字。 |
| [共封装光学](https://microarch-flow.github.io/wiki/CPO/wiki/) | [一个比特怎样从电路进入光纤，再回到电路？](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/) | 沿一个 1 走过调制、光纤、探测与判决，再读每波长预算。 |

## 三个补充算例

| 教学现场 | 要改变的条件 | 观察位置 |
| --- | --- | --- |
| [PCIe 链路能力与实际协商结果](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/aer-counters-link-debug/) | 对照同一条链路两端的构造输出。 | 从拓扑找桥和设备；在 LnkCap 与 LnkSta 中分别读出 Gen4 ×8 能力和 Gen3 ×4 状态。 |
| [两台服务器、四张 GPU 做环形全归约](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/four-gpu-allreduce-egress/) | 相同的 4 MiB 张量、四卡和四分块，只换环顺序。 | 在同一发送端统计所有 GPU 共用的网卡出口，按方向算出 6 MiB 与 12 MiB。 |
| [四条电通道、四种波长和一根单向光纤](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/) | 只给一路波长增加 1 dB 损耗。 | 对照发端 TP2 与收端 TP3 的单通道 OMA，检查这一路的预算；独立的反向光纤不计入正向预算。 |

## 合并时保留了哪些算例条件

| 旧文中的例子 | 新正文里的做法与依据 |
| --- | --- |
| SerDes 解串旧篇把同一个八位组 B2 连发两次。从第二位开始读八位，借到下一个 B2 的首位，得到 0x65。 | [32 位字的边界检验](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/#align)保留原数值，另给相邻的两个完整字 0xB2000000、0xA5A5A5A5。分别改判单个位、挪动整组边界，输出为 0x92000000、0x64000001。两个例子都按给定的位序从连续数据逐位取数。 |
| CPO 光链路旧篇给出 100 µW → 80 µA → 80 mV 的近似，还单列每通道光学预算。 | [探测器和 TIA](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/#receiver)把 100 µW 放在探测器有源面，保留响应度、跨阻和低频假设。[每波长预算](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/#budget)按 CWDM4 Rev. 1.1 图 1-1、表 2-3 至 2-5，将线路指标放在 TP2、TP3，避免重复计入光引擎内部损耗。 |
| NoC 的环形归约给出每个参与者的字节量，加速器互连的集体映射说明路径与分块。 | [出口计数表](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/four-gpu-allreduce-egress/#link-bytes)保留每卡发送 6 MiB 的结果，新增每个物理方向的账。计算同一物理截面的流量时，只计一次经过该处的载荷。 |

## 跨系列的知识边界

| 互连正文 | 遇到哪个问题时转到另一系列 |
| --- | --- |
| [MSI 中的行、副本和权限](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-invariants/) | 想看缓存阵列如何命中、填充和写回，从主文的两处链接进入「存储系统」。本篇跟踪同一行跨端点时的权限消息和最新值。 |
| [TCP 和 RDMA 的发送、接收与完成](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/host-nic-data-path/) | NIC 的描述符和任务提交机制接「计算微架构」的 DMA 网卡案例。互连跟踪跨端点操作、在途流量和两端完成。 |
| [采样边沿](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/)、[光电接收](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/) | 锁存与采样窗口、结区载流子和跨阻电路的电压响应用「半导体与电路基础」的先修路径。互连聚焦通道、恢复、解串和每波长预算。 |

## 合并前的书签现在去哪里

下表中的旧址保留可点击的分节目录。原小节涉及多篇深读时，按原位置送到相应一篇。

| 旧入口 | 主要去向 | 兼容书签 |
| --- | --- | --- |
| [一次跨芯粒通信（原章节入口）](https://microarch-flow.github.io/wiki/D2D/wiki/01-foundations/cross-die-communication/) | [一次跨芯粒的寄存器读，什么时候才算完成？](https://microarch-flow.github.io/wiki/D2D/wiki/ucie-pcie-read/) | 6 |
| [MSI 读写事务（原章节入口）](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/msi-transactions/) | [内存里还是 0，为什么 B 能读到 A 写的 1？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-invariants/) | 6 |
| [CUDA 与 HIP 对端访问（原章节入口）](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/peer-access-setup/) | [GPU A 能访问 GPU B 的地址，什么时候才能读？](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/address-mapping-and-permissions/) | 4 |
| [RDMA 排序、完成与缓冲区复用（原章节入口）](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/completion-ordering-and-lifetime/) | [同样发 4 KiB，TCP 和 RDMA 什么时候能复用缓冲区？](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/host-nic-data-path/) | 4 |
| [并行字与串行流（原章节入口）](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/parallel-to-serial/) | [一个 32 位字怎样穿过 SerDes，又怎样拼回来？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/)、[PLL、分频与多相时钟怎样工作？](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/clock-pll-and-multiphase/) | 4 |
| [解串、字边界与时钟域（原章节入口）](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/deserializer-and-alignment/) | [一个 32 位字怎样穿过 SerDes，又怎样拼回来？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/)、[走一遍 RX 协同案例](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/rx-cooperation-example/) | 4 |
| [学习路线图的原章节入口](https://microarch-flow.github.io/wiki/CPO/wiki/01-overview/learning-roadmap/) | [CPO 学习顺序导航页](https://microarch-flow.github.io/wiki/CPO/wiki/16-learning-navigation/study-navigation/) | 13 |
| [激光器、调制器与探测器的原章节入口](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/laser-modulator-detector/) | [一个比特怎样从电路进入光纤，再回到电路？](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/) | 6 |

同址重写的章节前身也可从变更记录查回，包括[跨桥读与 BUS 首课](https://github.com/microarch-flow/wiki/pull/14)、[AXI 写](https://github.com/microarch-flow/wiki/pull/19)、[仲裁](https://github.com/microarch-flow/wiki/pull/23)、[网络接口](https://github.com/microarch-flow/wiki/pull/26)、[共享总线、交叉开关与多跳网络](https://github.com/microarch-flow/wiki/pull/30)、[PCIe 枚举和链路诊断](https://github.com/microarch-flow/wiki/pull/34)、[跨芯粒读](https://github.com/microarch-flow/wiki/pull/38)、[MSI](https://github.com/microarch-flow/wiki/pull/41)、[GPU 对端缓冲区](https://github.com/microarch-flow/wiki/pull/44)和[TCP 与 RDMA](https://github.com/microarch-flow/wiki/pull/49)。

## 逐页核对

九个专题共 496 个公开页面，其中有 397 篇现行正文、案例、练习或参考资料，91 个专题或章节入口、8 个旧网址兼容页。另有一个[系列总入口](https://microarch-flow.github.io/wiki/interconnect/)。下面每条指向读者实际打开的网址。章节标题本身带链接时就是该章入口。

| 专题 | 正文与参考 | 入口 | 兼容页 |
| --- | ---: | ---: | ---: |
| 片上事务与总线 | 57 | 10 | 0 |
| 片上网络 | 81 | 11 | 0 |
| 封装内芯粒互连 | 23 | 2 | 1 |
| 系统 I/O 互连 | 38 | 10 | 0 |
| 一致性与内存互连 | 21 | 6 | 1 |
| 加速器互连 | 23 | 7 | 1 |
| 系统网络 | 25 | 8 | 1 |
| 高速电链路 | 56 | 11 | 2 |
| 共封装光学 | 73 | 26 | 2 |

## 片上事务与总线

从[专题首页](https://microarch-flow.github.io/wiki/BUS/wiki/)进入。

- [知识地图](https://microarch-flow.github.io/wiki/BUS/wiki/SUMMARY/)　按章节和问题查找各篇文章。

### [01 概览与问题定义](https://microarch-flow.github.io/wiki/BUS/wiki/01-overview/)

- [按目标学习 BUS](https://microarch-flow.github.io/wiki/BUS/wiki/01-overview/goal-oriented-navigation/)　按设计、调试、建模目标分流。
- [学习路线图](https://microarch-flow.github.io/wiki/BUS/wiki/01-overview/learning-roadmap/)　按依赖关系安排第一次学习的顺序。
- [BUS 在解决什么问题](https://microarch-flow.github.io/wiki/BUS/wiki/01-overview/problem-statement/)　从共享资源推出接口必须解决的问题。
- [BUS 分类框架](https://microarch-flow.github.io/wiki/BUS/wiki/01-overview/taxonomy/)　从访问语义、连接方式和仲裁位置区分同名总线。

### [02 基础对象与事务语义](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/)

- [两个模块同时访问同一目标，谁先走？](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/arbitration-ordering-backpressure/)　桥和 DMA 争一个 SRAM 入口，逐沿区分获选、握手与等待。
- [一条点到点专线，什么时候需要仲裁和事务标识？](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/bus-vs-noc-vs-point-to-point/)　只有一对端点时，用多个在途请求检查响应匹配和回压。
- [地址已经收下，数据为什么还没回来？](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/transaction-address-data-response/)　跟随数值 42 区分地址被接受、目标出数与桥收下返回。
- [位宽、时钟、Burst 与延迟](https://microarch-flow.github.io/wiki/BUS/wiki/02-fundamentals/width-clock-burst-latency/)　从线宽与时钟推算带宽上限，再加入突发和停顿。

### [03 片上总线协议族](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/)

- [AHB-Lite 与 APB 深化](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/ahb-lite-and-apb-deep-dive/)　对照 AHB-Lite 的流水与 APB 的两阶段外设访问。
- [AXI / AHB / APB 对照](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-ahb-apb-comparison/)　按流水、并发和状态成本比较三种 AMBA 接口。
- [AXI Burst、对齐与边界](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-burst-alignment-boundary/)　用地址递增、传输粒度和边界规则检查一次突发。
- [AXI Channel、ID 与 Outstanding](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding/)　辨认读写通道、标识和在途槽的不同限制。
- [一次 AXI 写入，地址、数据和响应分别在哪一拍交付？](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-five-channels-handshake/)　逐沿追踪四拍写，定位数据停住、末拍与写响应。
- [AXI Narrow Transfer 与 WSTRB](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-narrow-transfer-wstrb/)　用选通字节和起始地址解释窄写会改哪些字节。
- [AXI Response 与错误路径](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/axi-response-error-path/)　沿正常与错误响应检查一笔事务怎样结束。
- [Coherent Bus vs Non-Coherent Bus](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus/)　区分设备能访问共享地址与缓存副本参与协调。
- [分层总线与协议分工](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/hierarchical-bus-and-protocol-roles/)　从高速主干进入外设子系统，定位协议转换边界。
- [TileLink 概览](https://microarch-flow.github.io/wiki/BUS/wiki/03-on-chip-protocol-families/tilelink-overview/)　按 TileLink 的通道和权限组织读协议。

### [04 微架构与系统集成](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/)

- [AXI 属性、Cacheability 与 Barrier](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/axi-attributes-cacheability-barrier/)　配置访问属性，核对顺序、缓存和屏障的作用范围。
- [AXI 与 DMA 的系统接口](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/axi-dma-system-interface/)　沿 DMA 的访问责任区分命令、数据及完成。
- [AXI 到 DDR Controller 的路径](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/axi-to-ddr-controller-path/)　追踪 AXI 请求进入 DDR 控制器后经历的排队和服务。
- [Boot Path 与地址映射初始化](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/boot-path-address-map-initialization/)　沿复位后的第一段取指检查地址映射。
- [Bridge、CDC 与 Width Adapter](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/bridge-cdc-width-adaptation/)　在跨协议、跨时钟域和跨位宽时检查两端握手。
- [Debug Path 与 System Access](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/debug-path-system-access/)　检查调试主设备在正常 CPU 通路失效时还能访问哪里。
- [CPU、DMA、外设与内存之间的总线路径](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/dma-cpu-peripheral-memory-path/)　分开 CPU 设备控制流、DMA 数据流和返回。
- [DMA Descriptor Fetch、Data Move 与 Writeback](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback/)　分别追踪描述符抓取、数据搬运和写回。
- [Doorbell、Completion 与 Interrupt Flow](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/doorbell-completion-interrupt-flow/)　区分门铃、完成记录和中断的先后与所有者。
- [互连组件与数据路径分解](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/interconnect-components/)　把协议访问拆成各段组件和可观察事件。
- [IOMMU、SMMU 与 DMA 寻址](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/iommu-smmu-dma-addressing/)　定位设备地址翻译、权限检查与故障位置。
- [MMIO、Cache 与 Interrupt 视角](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/mmio-cache-interrupt-view/)　比较寄存器副作用、普通缓存和中断通知的软件假设。
- [Read/Write Combine 与 Bus Turnaround](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/read-write-combine-turnaround/)　分析读写合并如何交换排队等待与切换开销。
- [Row Locality、Return Path 与 AXI 体验](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/row-locality-return-path-axi-experience/)　查同一 AXI 接口遇到行命中、冲突时的返回节奏。
- [Shared Bus、Bus Matrix 与 Crossbar](https://microarch-flow.github.io/wiki/BUS/wiki/04-microarchitecture-integration/shared-bus-bus-matrix-crossbar/)　从具体矩阵端口和仲裁代价回看结构选型；首读对照在 NoC。

### [05 性能与调试](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/)

- [AXI Waveform Debug 方法](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/axi-waveform-debug-method/)　按通道读波形，识别已传输、被挡住和等待响应的拍。
- [带宽、延迟、利用率与拥塞](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/bandwidth-latency-utilization/)　把流量、忙时、等待时间和饱和条件放回同一测量窗口。
- [争用、QoS 与可观测性](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/contention-qos-observability/)　对共享点检查服务策略、观测位置和流量假设。
- [Counters、Trace 与观测点设计](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/counters-trace-observation-points/)　为计数器、追踪记录与观测点定义计数对象。
- [Timeout、Fault 与 Hang 定位框架](https://microarch-flow.github.io/wiki/BUS/wiki/05-performance-debug/timeout-fault-hang-debug-framework/)　用超时、显式故障和无进展的差别定位断点。

### [06 典型系统与案例](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/)

- [APB、MMIO 与普通内存的软件模型对照](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/apb-mmio-memory-software-model/)　从软件视角比较访问普通内存和设备寄存器的约束。
- [APB Peripheral Subsystem 案例卡](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/apb-peripheral-subsystem-case-card/)　沿慢外设子系统复核桥接与等待。
- [AXI Crossbar 案例卡](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/axi-crossbar-case-card/)　在交叉开关案例中检查端口、竞争及返回路径。
- [AXI vs TileLink 对照](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/axi-vs-tilelink-comparison/)　按一次典型事务对照 AXI 和 TileLink。
- [AI 芯片里的 BUS vs NoC](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip/)　用 AI 芯片案例区分接口约定与承载网络。
- [CPU 读 MMIO 卡死案例卡](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/cpu-mmio-read-hang-case-card/)　沿 CPU 到寄存器的读取，逐段寻找停止返回的位置。
- [DMA Completion 丢失案例卡](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/dma-completion-missing-case-card/)　把 DMA 已搬完和完成通知被软件看到分别验证。
- [IOMMU Fault 案例卡](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/iommu-fault-case-card/)　沿失败设备地址检查 IOMMU 映射与隔离状态。
- [MCU / SoC / AI 芯片中的 BUS 对照](https://microarch-flow.github.io/wiki/BUS/wiki/06-scenarios-case-studies/mcu-soc-ai-bus-comparison/)　在 MCU、SoC、AI 系统三个场景比较控制与数据流。

### [07 术语与检查清单](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/)

- [BUS 故障复盘模板](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/bus-debug-postmortem-template/)　记录故障现象、证据、根因和修复验证。
- [BUS 设计检查清单](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/bus-design-checklist/)　评审功能、并发和错误处理时逐条查漏。
- [BUS 一页版总览](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/bus-one-page/)　从一个入口复习总线需要回答的设计问题。
- [DDR/IOMMU/Debug 集成清单](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/ddr-iommu-debug-checklists/)　集成 DDR、地址翻译与调试子系统时核对依赖。
- [术语表](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/glossary/)　统一主从角色、事务、顺序和返回的词义。
- [BUS 高频问题](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/high-frequency-questions/)　按常见误判反查 BUS 与 NoC、协议与实现边界。
- [互连方案评估模板](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/interconnect-evaluation-template/)　在相同需求下记录互连候选的假设与取舍。
- [Master/Slave/Bridge 设计清单](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/master-slave-bridge-checklists/)　分主设备、从设备和桥检查接口责任。
- [BUS 协议阅读模板](https://microarch-flow.github.io/wiki/BUS/wiki/07-reference/protocol-reading-template/)　读陌生协议时记录请求、响应、顺序和错误语义。

### [08 建模与架构探索](https://microarch-flow.github.io/wiki/BUS/wiki/08-modeling/)

- [BUS 建模参考](https://microarch-flow.github.io/wiki/BUS/wiki/08-modeling/bus-modeling-reference/)　建模时查协议依赖图、事件词汇和状态边界。

## 片上网络

从[专题首页](https://microarch-flow.github.io/wiki/NOC/wiki/)进入。多播慢分支、虚通道、死锁与逐拍仿真各留下独立问题。

- [片上网络阅读目录](https://microarch-flow.github.io/wiki/NOC/wiki/SUMMARY/)　按章节和问题查找各篇文章。

### [01 认识 NoC](https://microarch-flow.github.io/wiki/NOC/wiki/01-overview/)

- [两笔读能同时通过吗？从共享总线、交叉开关到多跳 NoC](https://microarch-flow.github.io/wiki/NOC/wiki/01-overview/bus-vs-noc-vs-crossbar/)　在相同入口、不同或相同目的端的两笔读取之间比较共享口争用。
- [NoC 学习与建模路线](https://microarch-flow.github.io/wiki/NOC/wiki/01-overview/learning-roadmap/)　按认识机制、分析系统和实现模型三种需求选读。
- [NoC 在解决什么问题？](https://microarch-flow.github.io/wiki/NOC/wiki/01-overview/problem-statement/)　由多个端点的一次请求引出片上竞争与路由器。
- [NoC 的设计维度与工作负载](https://microarch-flow.github.io/wiki/NOC/wiki/01-overview/taxonomy/)　先定义工作负载和目标，再列拓扑、路由和流控维度。

### [02 路由器与逐跳流控](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/)

- [VC 分配和交换分配分别决定什么？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/allocator-design-vc-switch/)　区分分配输出虚通道与获得交换机时隙。
- [Credit 如何控制逐跳发送与反压？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/credit-based-flow-control/)　用信用守恒解释逐跳发送上限和反压。
- [输入缓冲如何组织和分配空间？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/input-buffer-organization/)　从单 FIFO 的队头阻塞比较不同输入缓冲组织。
- [Packet、Flit 与 Phit：网络传输分成哪些单位？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/packet-flit-phit-hierarchy/)　从端点事务拆到 packet、flit 与物理传输单位。
- [NoC 路由器怎样逐步转发一个 Flit？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/router-pipeline-stages/)　逐阶段检查一个 flit 在路由、分配和穿越时占用的资源。
- [路由器的面积、功耗和性能如何权衡？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/router-power-area-tradeoff/)　从缓冲容量、端口和仲裁讨论面积功耗与性能。
- [虚通道如何分离队列与共享链路？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/virtual-channel-fundamentals/)　说明多个 VC 如何分队列又共享同一物理链路。
- [存储转发、虚直通与虫洞交换有什么区别？](https://microarch-flow.github.io/wiki/NOC/wiki/02-router-microarchitecture/wormhole-vs-vct-vs-store-forward/)　让同一条三跳路径承载三种转发方式并比较缓冲需求。

### [03 拓扑与物理组织](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/)

- [Crossbar 与 Concentrated Mesh：怎样连接多个端点？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/crossbar-and-concentrated-mesh/)　区分全交叉连接与多个端点共享一座 mesh 路由器。
- [Flattened Butterfly 与 Dragonfly：高端口数网络怎样连接？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/flattened-butterfly-dragonfly/)　比较维度内直连和组间连接给高端口数路由器的需求。
- [层次化与混合互连：局部网络怎样接入全局网络？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/hierarchical-and-hybrid-topology/)　沿跨区传输区分局部网络、网关和全局网络。
- [Mesh 与 Torus：怎样比较网格和环回连接？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/mesh-and-torus/)　从环回连接与流量分布比较 mesh、torus 的负载。
- [Ring 与分层 Ring：共享路径的容量在哪里？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/ring-and-hierarchical-ring/)　分别计算环的双向与单向切面容量。
- [怎样定义和比较 NoC 拓扑指标？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/topology-design-metrics/)　在相同端点和流量假设下比较 4×4 mesh 与 torus 的指标。
- [拓扑与物理实现：连接图怎样落到芯片上？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/topology-physical-realization/)　把逻辑边放回芯片，考虑长线流水、缓冲及信用往返。
- [拓扑选型：怎样比较满足同一需求的候选？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/topology-selection-framework/)　固定流量目标和比较口径后再选择候选拓扑。
- [Tree 与 Fat-tree：怎样组织汇聚和分发？](https://microarch-flow.github.io/wiki/NOC/wiki/03-topology/tree-and-fat-tree/)　从上层汇聚链路解释树形与 fat-tree 的容量区别。

### [04 路由、仲裁与服务保证](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/)

- [自适应路由：怎样利用可选路径？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/adaptive-routing-tradeoffs/)　对有多条合法出路的包分析状态信息、候选路径和拥塞。
- [NoC 仲裁策略：共享资源先服务谁？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/arbitration-policies/)　区分一次轮询保证服务的次数界与可证明的等待时间。
- [Turn Model 与逃逸资源：怎样限制路由依赖？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/deadlock-avoidance-turn-model/)　沿转向的资源依赖审查路由限制与逃逸资源。
- [死锁、活锁与饥饿：为什么包不能完成？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/deadlock-livelock-starvation/)　沿等待图识别循环等待、无效前进和长期不获服务。
- [维序路由：固定维度顺序改变了什么？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/dimension-order-routing/)　沿 XY、YX 两种维序路径检查热点与依赖顺序。
- [NoC 的 QoS：怎样为不同流量分配服务？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/qos-and-priority-classes/)　将业务目标具体落实到分类、仲裁和路径服务。
- [NoC 路由算法怎样分类？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/routing-algorithm-classes/)　按目的、路径自由度与拥塞反馈分类路由算法。
- [端到端服务保证：带宽与延迟怎样证明？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/service-guarantees-and-latency-bounds/)　把输入到达约束和每段服务承诺合成端到端界。
- [Source Routing：源端怎样指定网络路径？](https://microarch-flow.github.io/wiki/NOC/wiki/04-routing-and-flow-control/source-routing-for-deterministic-systems/)　算源路由字段需要的位数并检查中间跳的解释。

### [05 端点与系统集成](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/)

- [地址怎样映射到端点和路径？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/address-map-and-routing-table/)　从地址交错、端点映射和路由组合推算流量分布。
- [跨时钟域、复位与流控：空槽何时可以再次使用？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/clock-domains-and-reset/)　用两槽异步 FIFO 跟踪跨时钟域的可用槽。
- [DMA 与 NoC：请求窗口怎样影响流量？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/dma-engine-noc-interaction/)　将 DMA 请求窗口折算为对网络的注入和在途上限。
- [多网络与共享资源：怎样隔离不同流量？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/multiple-physical-networks/)　固定总资源量比较物理隔离与逻辑共享。
- [一次读取怎样变成 NoC 里的请求包和返回包？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/ni-network-interface-design/)　从桥的读请求跟到 NI 封包、内部标签和匹配返回。
- [NoC 与存储系统：数据为什么会在端点等待？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/noc-meets-memory-system/)　从存储端口、bank 和回程区分端点等待与网络排队。
- [系统事务如何跨越 BUS 与 NoC？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/noc-vs-bus-revisited/)　在 BUS、NI 和 NoC 边界核对事务责任。
- [流量模式与表征：网络实际收到什么？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/traffic-patterns-and-characterization/)　构造相同平均速率、不同突发的输入并比较等待。
- [事务拆分、顺序与完成：网络怎样保持接口语义？](https://microarch-flow.github.io/wiki/NOC/wiki/05-system-integration/transaction-ordering-and-completion/)　检查一笔读拆分后怎样匹配返回及维持接口顺序。

### [06 AI NOC Specifics](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/)

- [All-to-All 与通信矩阵：流量在哪里形成瓶颈？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/all-to-all-and-traffic-matrix/)　把 All-to-All 通信矩阵折算为物理切面负载。
- [广播、多播与复制：同一份数据怎样交付多个目的端？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/broadcast-multicast-tree/)　从共享路径和复制位置分析慢多播分支。
- [NoC 网关与跨 Die 互连：请求怎样跨越边界？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect/)　从片内网关追到封装边界，再定位请求与完成。
- [集体通信基础：参与者交换什么，何时完成？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/collective-communication-basics/)　用四端点例子区分广播、聚集、归约和完成参与者。
- [编译器与 NoC 协同：怎样产生可执行的通信计划？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/compiler-noc-co-design/)　把工作负载意图转成由硬件能力承接的通信计划。
- [确定性与静态调度：提前规划能保证什么？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/deterministic-noc-and-static-scheduling/)　列出确定性与静态调度依赖的服务、路由和端点假设。
- [Memory-centric NoC：存储端口怎样塑造网络？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/memory-centric-noc/)　保持流量不变，只改存储端口位置，比较容量限制。
- [归约与 AllReduce：多份数据怎样合并与分发？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/reduction-and-collective-networks/)　区分算术归约与数据分发，推导环形算法的字节量。
- [Tile 怎样与 NoC 交换数据？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/tile-architecture-and-noc/)　追踪一个 tile 的收发与 bank 反压。
- [工作负载怎样形成 NoC 流量？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/why-ai-noc-is-different/)　从任务依赖和物理放置说明逻辑工作怎样产生网络流量。
- [Attention Decode 与 KV Cache：数据怎样支持下一步生成？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/workload-attention-decode-kv-cache/)　沿 decode 的依赖和 KV 放置核对每步需要的有效数据。
- [Attention Prefill 案例：分块和掩码怎样改变通信？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/workload-attention-prefill/)　给相同 prefill 分块配置不同掩码，追踪通信和可用时刻。
- [GEMM 通信案例：分块和放置怎样改变流量？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/workload-gemm-on-noc/)　在 2×2 tile 的 GEMM 映射上选择部分和累加位置。
- [MoE 通信案例：专家选择怎样形成片上流量？](https://microarch-flow.github.io/wiki/NOC/wiki/06-ai-noc-specifics/workload-moe-routing/)　在相同逻辑数据量下计算两种专家分布的流量。

### [07 Evaluation Methodology](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/)

- [架构探索与实验设计：怎样比较候选？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/architecture-exploration-loop/)　用受控实验对比合法候选并寻找参数交互。
- [实验与案例记录：怎样保存可复查的结论？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/case-card-template/)　按已填案例记录假设、下界与可检验结论。
- [从工作负载到流量 Trace：事件和依赖怎样生成？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/from-workload-to-traffic-trace/)　从任务依赖产生有来源、目的、大小和完成条件的 trace。
- [延迟、吞吐与饱和：数字从哪里开始，到哪里结束？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/metrics-latency-throughput-saturation/)　为延迟与吞吐分别选取事件边界和时间窗口。
- [如何选择模型粒度：需要保留哪些状态？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/modeling-layers-analytical-event-cycle/)　由问题决定模型显式保留哪些状态与推进规则。
- [性能界与瓶颈分析：流量和容量能说明什么？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/performance-bounds-and-bottlenecks/)　把每个资源的字节需求换成可检验的完成时间下界。
- [功耗、能量与面积建模：性能收益需要付出什么？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/power-area-modeling/)　用操作次数、单位能量和面积统计界定成本模型。
- [Stall 分类与归因：等待发生在哪里？](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/stall-taxonomy-and-attribution/)　根据阻塞对象、占用者和时间归因 stall。
- [Trace 生成与核算实作：一个 4×4 GEMM 示例](https://microarch-flow.github.io/wiki/NOC/wiki/07-evaluation-methodology/trace-generation-worked-example/)　运行 4×4 GEMM trace 并与手算通信量对照。

### 工作负载案例

- [缓存一致性通信案例：一次读取会产生哪些消息？](https://microarch-flow.github.io/wiki/NOC/wiki/07-workload-cases/coherent-access-and-noc/)　用同一行数据解释一致性协议生成了哪些请求和返回消息。
- [公开 NoC 案例：AMD Versal 如何承载一次读请求？](https://microarch-flow.github.io/wiki/NOC/wiki/07-workload-cases/published-noc-case/)　将一次实际架构上的读映射到 AMD Versal 公开组件。

### [08 Simulator Construction](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/)

- [核心数据结构：状态由谁持有，何时改变？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/core-data-structures/)　核对路由器、端点和工作负载分别持有哪些模型状态。
- [事件推进与逐拍精度：怎样安全地跳过空拍？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/event-driven-vs-cycle-accurate/)　在语义相同的模型中比较逐拍和事件驱动推进。
- [实现路线与阶段验收：先做哪一部分？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/implementation-roadmap/)　按最小传输、扩展能力和验收用例分阶段实现。
- [最小逐拍仿真实作：三跳单播如何前进？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/minimal-cycle-simulator/)　运行三跳最小单播例子，检验每个 flit 的前进时间。
- [参数与配置参考：数值、单位和边界怎样对应？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/parameter-reference/)　按单位和资源边界核对配置、派生量和合法性。
- [路由器逐拍推进：怎样检查并提交动作？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/router-pipeline-pseudocode/)　按同一拍快照选择动作，再提交路由器状态。
- [模拟器设计规格：第一版要表示什么？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/simulator-design-spec/)　固定第一版模型所承诺的输入、状态、行为与输出。
- [流量注入、分包与完成：Trace 怎样进入网络？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/traffic-injection-and-tracing/)　从就绪事件生成包并追到完成，检查分包开销。
- [验证、校准与适用边界：怎样检查模型？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/verification-and-calibration/)　用无阻塞路径、争用等小场景校准时序。
- [工作负载与端点执行：依赖何时释放？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/workload-endpoint-execution/)　按资源并发和本地消费定义依赖何时释放。
- [从 Flow 到完成：一条依赖怎样跨过网络？](https://microarch-flow.github.io/wiki/NOC/wiki/08-simulator-construction/workload-to-completion-worked-example/)　让一个有前驱的流从注入越过网络直到任务可继续。

### [09 Reference](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/)

- [NoC 检查清单：怎样避免遗漏条件？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/checklists/)　按资源、流量与目标做设计或建模检查。
- [NoC 练习与参考解答：怎样检查结论？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/exercises-and-worked-solutions/)　通过可手算练习与解答核对推导。
- [NoC 术语表：常见概念怎样区分？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/glossary/)　检索核心概念和最容易混淆的词对。
- [NoC 高频问题：怎样避免常见误判？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/high-frequency-questions/)　从常见误判回到前置假设。
- [NoC 设计决策路径：怎样生成并检验候选？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/noc-design-decision-tree/)　按一次可区分候选的观察安排下一项设计实验。
- [NoC 参考资料与工具：按什么问题继续查？](https://microarch-flow.github.io/wiki/NOC/wiki/09-reference/references-and-tools/)　按流控、路由、事务和集体通信检索资料与工具。

## 封装内芯粒互连

从[专题首页](https://microarch-flow.github.io/wiki/D2D/wiki/)进入。

- [封装内芯粒互连：知识地图](https://microarch-flow.github.io/wiki/D2D/wiki/SUMMARY/)　按章节和问题查找各篇文章。
- [BoW.Flexi：AHB 读取怎样封装成跨芯粒数据包？](https://microarch-flow.github.io/wiki/D2D/wiki/bow-flexi/)　用一次 AHB 读取看事务如何封装进 BoW.Flexi。
- [BoW PHY 2.0：数据怎样通过并行线路跨越芯粒？](https://microarch-flow.github.io/wiki/D2D/wiki/bow-phy/)　按 slice 的线路数量和方向核对同时收发能力。
- [一次跨芯粒的寄存器读，什么时候才算完成？](https://microarch-flow.github.io/wiki/D2D/wiki/ucie-pcie-read/)　将一次读在封装通道和 UCIe/PCIe 两层的事件一一对应。

### 基础

- [一次跨芯粒通信（原章节入口）](https://microarch-flow.github.io/wiki/D2D/wiki/01-foundations/cross-die-communication/)　原入口。见上表中的分节去向。
- [芯粒怎样在封装内连接？](https://microarch-flow.github.io/wiki/D2D/wiki/01-foundations/in-package-connections/)　比较中介层、桥与堆叠的物理剖面。
- [芯粒是什么，为什么要把系统拆开？](https://microarch-flow.github.io/wiki/D2D/wiki/01-foundations/what-is-a-chiplet/)　区分 die、芯粒和封装，再讨论功能如何拆分。

### 接口与协议

- [AIB 2.0：数据怎样通过芯粒间的物理接口？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/aib-2/)　从 AIB 的线数和时序算一个通道的运输量。
- [BoW 存储接口：计算芯粒怎样连接存储芯粒？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/bow-memory/)　检查计算芯粒、存储控制器和读写 slice 的边界。
- [BoW PHY 2.0：一条数据线坏了怎样绕过？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/bow-phy-redundancy/)　把逻辑位映射到可用物理线，跟随 D4 故障。
- [AMBA CHI C2C：一致性消息怎样跨越芯粒？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/chi-c2c/)　沿一次跨芯粒 snoop 对上 CHI 与承载接口。
- [OIF 112G XSR+：高速串行信号怎样跨越芯粒？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/oif-cei-112g-xsr-plus/)　按 XSR+ 的串行通道和 lane 数核算路径。
- [UCIe 1.1 链路怎样启动？从边带到主带训练](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/ucie-1-1-link-bring-up/)　跟踪 UCIe 从复位、边带发现到主带训练。
- [UCIe-3D：上下堆叠的芯粒怎样交换数据？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/ucie-3d/)　比较面对面堆叠与平面封装的连接方式。
- [UCIe.mem：计算芯粒怎样访问封装内存？](https://microarch-flow.github.io/wiki/D2D/wiki/02-interfaces/ucie-memory/)　在 UCIe.mem 的读路径上区分协议接口和 DRAM 操作。

### 系统设计

- [跨芯粒读取：为什么带宽高而吞吐不足？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/effective-bandwidth-and-latency/)　把线速、承载开销和在途请求窗口折算为吞吐上限。
- [跨芯粒流控：请求、snoop 和响应怎样继续前进？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/flow-control-and-forward-progress/)　定位请求、snoop、响应分别等待的资源。
- [芯粒互操作与启动：连接接通后怎样让系统可用？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/interoperability-and-bring-up/)　区分电气互通、链路建立和系统可访问的启动条件。
- [跨芯粒链路出错后怎样检测和重放？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/link-reliability/)　沿一次检测、重放与恢复检查状态所有者。
- [芯粒链路怎样测试：通过回环后能证明什么？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/link-testing-and-diagnosis/)　比较不同回环覆盖的边界和遗漏的故障。
- [多颗芯粒怎样连接？从数据放置看跨芯粒流量](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/multi-chiplet-topology/)　改变数据的放置位置，观察跨芯粒流量。
- [UCIe 2.0 DFx：封装后怎样访问与管理芯粒测试逻辑？](https://microarch-flow.github.io/wiki/D2D/wiki/03-system-design/ucie-dfx-test-access/)　跟踪管理通道怎样抵达封装后测试逻辑。

### 产品案例

- [AMD EPYC 9004：计算芯粒怎样连接 I/O die？](https://microarch-flow.github.io/wiki/D2D/wiki/04-product-cases/amd-epyc-9004-gmi/)　从 EPYC 计算芯粒经 I/O die 跟到 DDR5。
- [AMD MI300A：CPU、GPU 和 HBM 怎样在同一封装协作？](https://microarch-flow.github.io/wiki/D2D/wiki/04-product-cases/amd-mi300a/)　用 MI300A 对照 CPU、GPU、HBM 的封装内角色。
- [Stratix 10 TX：FPGA 与收发器芯粒怎样协同？](https://microarch-flow.github.io/wiki/D2D/wiki/04-product-cases/stratix-10-tx/)　分清 FPGA 逻辑、收发器芯粒以及外部串行链路。

## 系统 I/O 互连

从[专题首页](https://microarch-flow.github.io/wiki/PCIE/wiki/)进入。

- [PCIe 知识地图](https://microarch-flow.github.io/wiki/PCIE/wiki/SUMMARY/)　按章节和问题查找各篇文章。

### [01 概览与问题定义](https://microarch-flow.github.io/wiki/PCIE/wiki/01-overview/)

- [按目标学习 PCIe](https://microarch-flow.github.io/wiki/PCIE/wiki/01-overview/goal-oriented-navigation/)　按设备枚举、驱动、性能与验证目的寻找入口。
- [学习路线图：从设备发现到性能解释](https://microarch-flow.github.io/wiki/PCIE/wiki/01-overview/learning-roadmap/)　按请求路径、发送条件和性能现象安排学习次序。
- [PCIe 在解决什么问题？](https://microarch-flow.github.io/wiki/PCIE/wiki/01-overview/problem-statement/)　用一张设备卡提问发现、寻址、事务与出错处理。
- [PCIe 问题地图：角色、事务、地址与性能](https://microarch-flow.github.io/wiki/PCIE/wiki/01-overview/taxonomy/)　沿角色、事务、地址和性能把现象拆成可查问题。

### [02 链路、分层与事务基础](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/)

- [信用流控与链路重放：为什么有数据也不能发送？](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/credit-flow-control-and-replay/)　分别检查逐跳信用和重放需要保留的状态。
- [PCIe 三层架构：事务、逐跳可靠性与物理链路](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical/)　把事务处理、逐跳可靠性与物理传输放在不同边界。
- [Posted、Non-Posted 与排序：何时可以继续下一步？](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/posted-nonposted-completion-ordering/)　区分 Posted、Non-Posted 和可观察完成条件。
- [一次 PCIe 读取：TLP、链路确认与 Completion](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/tlp-dllp-completion-basics/)　沿两跳追踪 Tag、链路 ACK 和目标返回的 Completion。
- [Root Complex、Switch、Endpoint：请求经过谁？](https://microarch-flow.github.io/wiki/PCIE/wiki/02-link-transaction-basics/topology-root-complex-switch-endpoint/)　画出 RC、Switch、Endpoint 的一条实际事务路径。

### [03 配置、枚举与地址映射](https://microarch-flow.github.io/wiki/PCIE/wiki/03-configuration-enumeration-addressing/)

- [主机第一次读卡上的寄存器，地址是怎么来的？](https://microarch-flow.github.io/wiki/PCIE/wiki/03-configuration-enumeration-addressing/config-space-bar-capability/)　给 64 KiB BAR 分配地址，再从寄存器偏移读版本号。
- [桥怎样用总线号找到设备，又怎样用地址窗口转发访问？](https://microarch-flow.github.io/wiki/PCIE/wiki/03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation/)　跨三个桥比较配置请求按总线号路由与 MMIO 按窗口转发。
- [IOMMU：设备地址如何翻译并受到隔离？](https://microarch-flow.github.io/wiki/PCIE/wiki/03-configuration-enumeration-addressing/iommu-address-translation-device-isolation/)　沿设备身份查 IOTLB、页表及权限故障。
- [配置、BAR 与 DMA：一次访问使用哪个地址？](https://microarch-flow.github.io/wiki/PCIE/wiki/03-configuration-enumeration-addressing/mmio-config-dma-address-view/)　用方向和请求者区分配置地址、BAR 地址与设备 DMA 地址。

### [04 数据路径、DMA 与中断](https://microarch-flow.github.io/wiki/PCIE/wiki/04-data-path-dma-interrupts/)

- [设备 DMA 的读写路径：谁请求，数据往哪里走？](https://microarch-flow.github.io/wiki/PCIE/wiki/04-data-path-dma-interrupts/device-dma-read-write-flow/)　从设备视角区分内存读请求、读返回和带数据的写。
- [主机缓冲区：生命周期、DMA 映射与可见性](https://microarch-flow.github.io/wiki/PCIE/wiki/04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility/)　同时检查主机缓冲生命周期、DMA 映射和缓存可见性。
- [PCIe 读取为何需要并发：完整返回时间与 Tag 窗口](https://microarch-flow.github.io/wiki/PCIE/wiki/04-data-path-dma-interrupts/pcie-read-completion-latency/)　从完整返回时间与 Tag 个数估计在途读取上限。
- [从提交队列到完成通知：Doorbell、CQE 与 MSI-X](https://microarch-flow.github.io/wiki/PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix/)　从提交门铃跟到真正可回收的完成项和中断。

### [05 性能与调试](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/)

- [AER 与链路计数器：错误在哪里被观察到？](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/aer-counters-link-debug/)　从 AER 与链路寄存器的观测点解读错误来源。
- [PCIe 性能参数：带宽、Credit、MPS 与 MRRS 限制什么？](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/bandwidth-latency-credit-mps-mrrs/)　分别计算线带宽、信用、最大载荷和读请求限制。
- [UR、CA 与 Timeout：有错误返回，还是没有等到返回？](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/common-failures-ur-ca-timeout/)　把 UR、CA 的显式失败与没有返回的超时分别查证。
- [主机与设备数据路径：如何定位吞吐瓶颈？](https://microarch-flow.github.io/wiki/PCIE/wiki/05-performance-debug/host-device-bottleneck-breakdown/)　沿 CPU、设备、PCIe 与软件分段采集吞吐证据。

### [06 工作负载与案例](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/)

- [设备不可用：区分发现、资源分配与 DMA 启动失败](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/enumeration-failure-case-card/)　把设备未出现、资源未分配和 DMA 未启动拆开。
- [FPGA 采集卡：BAR 可访问，为什么 DMA 仍不工作？](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/fpga-control-data-plane-case-card/)　用构造的 FPGA 采集卡观察比较 BAR 控制和 DMA 数据面。
- [GPU 主机链路何时成为瓶颈？](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/gpu-accelerator-host-link/)　在主机与 GPU 之间拆出搬运量、链路时间与可重叠部分。
- [链路降速或降宽：先核对能力、配置与实际状态](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/link-downgrade-case-card/)　从两端 lspci 输出对照链路能力与协商结果。
- [NIC 数据路径：RX、TX 分别占用哪个 PCIe 方向？](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/nic-dma-case-card/)　分别计算网卡收、发占用的 PCIe 方向。
- [NVMe over PCIe：从 SQ 提交到 CQ 回收](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/nvme-queue-data-path-case-card/)　跟踪普通 NVMe Read 从 SQ 提交到 CQ 回收。
- [一次跨桥读取：设备已经收到请求，主机为什么还在等？](https://microarch-flow.github.io/wiki/PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary/)　从设备接下读请求跟到主机最终收齐片内 SRAM 的 42。

### [07 高级主题](https://microarch-flow.github.io/wiki/PCIE/wiki/07-advanced-topics/)

- [PCIe 与 CXL 的边界：I/O 事务之外增加了什么？](https://microarch-flow.github.io/wiki/PCIE/wiki/07-advanced-topics/cxl-and-pcie-boundary/)　在 Type 3 内存扩展例子中划分 PCIe 与 CXL 职责。
- [PCIe P2P：对端资源、路由与隔离必须同时成立](https://microarch-flow.github.io/wiki/PCIE/wiki/07-advanced-topics/p2p-switch-topology-constraints/)　按资源、转发路径和隔离配置验证 P2P 是否成立。
- [SR-IOV 与地址空间扩展：PF/VF、ATS、PASID、PRI](https://microarch-flow.github.io/wiki/PCIE/wiki/07-advanced-topics/sriov-ats-pasid-pri-overview/)　将 PF/VF 设备呈现与地址翻译、进程标识、缺页处理分开。

### [08 查阅、建模与检查清单](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/)

- [PCIe 术语表](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/glossary/)　查 PCIe 术语与常见混淆。
- [PCIe 高频问题](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/high-frequency-questions/)　按读写性能、BAR/DMA 等高频问题回看对应机制。
- [PCIe 调试检查清单](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/pcie-debug-checklist/)　现场调试时按拓扑、枚举和数据路径核对。
- [PCIe 故障复盘模板](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/pcie-debug-postmortem-template/)　归档故障现象、影响范围与验证过程。
- [PCIe 设计检查清单](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/pcie-design-checklist/)　设计评审时检查角色、资源、通知和恢复。
- [PCIe 建模参数与公式速查](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/pcie-modeling-params/)　查明确模式、字节和方向口径下的性能公式。
- [PCIe 一页总览：从配置到软件完成](https://microarch-flow.github.io/wiki/PCIE/wiki/08-reference/pcie-one-page/)　从配置、提交到软件完成快速重建模型。

## 一致性与内存互连

从[专题首页](https://microarch-flow.github.io/wiki/COHERENCE/wiki/)进入。

- [CXL：从设备发现到内存访问](https://microarch-flow.github.io/wiki/COHERENCE/wiki/cxl-host-memory/)　沿 Type 3 内存扩展路径认识三类 CXL 协议。

### [基础概念：先确定一致性保证的对象](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/)

- [缓存一致性、内存顺序与原子性：分别保证什么？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-consistency-atomicity/)　用两个地址区分缓存一致性、顺序与原子性。
- [一致性域与 I/O：谁参与副本协调？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-domains-and-io/)　沿设备写入检查哪些缓存副本受协调。
- [内存里还是 0，为什么 B 能读到 A 写的 1？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/01-foundations/coherence-invariants/)　在同一条缓存行上跟踪值、权限、失效确认与脏数据返回。

### [协议与控制器：把权限规则变成执行过程](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/)

- [目录、Home 与 Snoop Filter：谁知道缓存行在哪里？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/directory-snoop-filter/)　比较目录与探测过滤器记录的信息及容量成本。
- [一致性事务如何保证前进？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/forward-progress/)　用有限缓冲和资源依赖解释一致性事务可能无法推进。
- [MESI 与 MOESI：增加状态解决了什么问题？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/mesi-moesi-extensions/)　从 E、O 状态分别定位省掉的请求和写回。
- [MSI 读写事务（原章节入口）](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/msi-transactions/)　原入口。见上表中的分节去向。
- [瞬态状态与并发竞争：收到数据以后，还在等什么？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/02-protocols/transient-states-and-races/)　用并发写和数据、确认异步到达检查瞬态状态。

### [CHI：从节点职责到事务完成](https://microarch-flow.github.io/wiki/COHERENCE/wiki/03-chi/)

- [CHI 的流控、重试与完成：三种“可以继续”](https://microarch-flow.github.io/wiki/COHERENCE/wiki/03-chi/chi-flow-control-retry-completion/)　区分链路信用、协议重试和事务完成。
- [CHI 节点与通道：把协议角色放到访问路径中](https://microarch-flow.github.io/wiki/COHERENCE/wiki/03-chi/chi-nodes-and-channels/)　将请求、归属、从属节点与 CHI 通道放在读取路径内。
- [CHI 的读取与写权限：数据到达和事务完成怎样区分？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/03-chi/chi-read-and-ownership/)　跟踪 ReadShared 与取得写权限时数据和完成的边界。

### 04-cxl

- [CXL.cache 与设备内存：两个方向的一致性](https://microarch-flow.github.io/wiki/COHERENCE/wiki/04-cxl/cxl-cache-and-device-memory/)　区分设备缓存主机数据和主机访问设备内存两个方向。
- [Linux CXL：从发现设备到应用可用内存](https://microarch-flow.github.io/wiki/COHERENCE/wiki/04-cxl/cxl-linux-regions-and-memory/)　从 Linux 枚举一直查到可用于应用的内存。
- [内存扩展、池化与共享：容量怎样分配，数据怎样协调？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/04-cxl/cxl-pooling-sharing-fabric/)　按分配关系和版本能力讨论扩展、池化与共享。
- [Type 3 内存访问：从主机地址到设备地址](https://microarch-flow.github.io/wiki/COHERENCE/wiki/04-cxl/cxl-type3-address-path/)　用两路交织算例把主机地址换算成设备地址。

### [性能与可靠性：从访问过程到系统代价](https://microarch-flow.github.io/wiki/COHERENCE/wiki/05-performance-reliability/)

- [共享、伪共享与一致性流量：程序改了几个字节，网络搬了多少？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/05-performance-reliability/coherence-traffic-and-false-sharing/)　按缓存行计流量，检查小范围写入引起的真共享或伪共享。
- [CXL 延迟、带宽与数据放置：为什么线速率不能预测应用性能？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/05-performance-reliability/cxl-latency-bandwidth-and-placement/)　结合并发深度、延迟与放置判断应用可用带宽。
- [内存错误、复位与容量移除：数据何时仍然可用？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/05-performance-reliability/memory-errors-and-lifecycle/)　区分介质错误、复位、移除与持久化承诺。

### [查阅与验证：把理解变成可检查的结论](https://microarch-flow.github.io/wiki/COHERENCE/wiki/06-reference/)

- [设计与调试检查表：把现象转换为可验证的问题](https://microarch-flow.github.io/wiki/COHERENCE/wiki/06-reference/design-debug-checklist/)　用三种反例复核故障假设与观测证据。
- [术语、版本与一手资料：怎样追溯本专题的结论？](https://microarch-flow.github.io/wiki/COHERENCE/wiki/06-reference/glossary-and-sources/)　查版本口径与各项结论的一手规范。
- [一致性模型怎样验证：从可检查状态到竞争反例](https://microarch-flow.github.io/wiki/COHERENCE/wiki/06-reference/modeling-and-validation/)　从状态义务和竞争反例设计模型断言。

## 加速器互连

从[专题首页](https://microarch-flow.github.io/wiki/SCALEUP/wiki/)进入。

### [01 访问语义](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/)

- [GPU A 能访问 GPU B 的地址，什么时候才能读？](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/address-mapping-and-permissions/)　从 peer 地址授权跟到生产、消费和归还 GPU 缓冲区。
- [加速器互连的对象与边界：先确定谁与谁通信](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/objects-and-domains/)　将软件对象映射到 GPU、端口与通信域。
- [读写、原子操作与完成：哪些事件允许继续执行](https://microarch-flow.github.io/wiki/SCALEUP/wiki/01-access-semantics/operations-ordering-and-completion/)　从“数据加通知”检验读、写、原子的完成条件。

### [02 交换结构](https://microarch-flow.github.io/wiki/SCALEUP/wiki/02-fabric-architecture/)

- [背压与拥塞：缓冲不溢出以后，请求能否继续前进](https://microarch-flow.github.io/wiki/SCALEUP/wiki/02-fabric-architecture/backpressure-and-progress/)　沿拥塞的出口定位反压与响应前进资源。
- [一次远端读取：请求、返回和在途状态怎样配合](https://microarch-flow.github.io/wiki/SCALEUP/wiki/02-fabric-architecture/remote-read-path/)　用一次读的请求、返回和在途窗口估算吞吐。
- [链路重试与事务失败：恢复了传输，是否恢复了操作](https://microarch-flow.github.io/wiki/SCALEUP/wiki/02-fabric-architecture/retry-and-failure/)　用超时后的原子加法区分链路恢复和操作重试。
- [直连与交换：怎样计算可供任务使用的带宽](https://microarch-flow.github.io/wiki/SCALEUP/wiki/02-fabric-architecture/topology-and-bandwidth/)　用超售例子对比直连和交换的可用容量。

### [03 协议与系统案例](https://microarch-flow.github.io/wiki/SCALEUP/wiki/03-protocols-and-systems/)

- [AMD xGMI：八 GPU 直连系统怎样分配链路](https://microarch-flow.github.io/wiki/SCALEUP/wiki/03-protocols-and-systems/amd-xgmi/)　查八 GPU 系统的实际 xGMI 邻接和子集分配。
- [NVLink 与 NVSwitch：从 GPU 链路到机架通信域](https://microarch-flow.github.io/wiki/SCALEUP/wiki/03-protocols-and-systems/nvlink-nvswitch/)　按链路、交换结构和机架通信域解读公开带宽。
- [UALink 200G 1.0：一次内存事务怎样穿过协议栈](https://microarch-flow.github.io/wiki/SCALEUP/wiki/03-protocols-and-systems/ualink-200g-transactions/)　从一次 UALink 200G 1.0 读追踪分层职责。
- [UALink 规范组件：Common、DL/PL 与系统管理怎样分工](https://microarch-flow.github.io/wiki/SCALEUP/wiki/03-protocols-and-systems/ualink-specification-family/)　查 Common、DL/PL 和管理组件的组合与版本。

### [04 软件与集体通信](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/)

- [集体通信怎样映射到链路、分块和交换归约](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/collective-mapping-and-offload/)　将逻辑通信块映射到链路、分块和交换归约。
- [四张 GPU 做一次 AllReduce，哪个出口最忙？](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/four-gpu-allreduce-egress/)　在两机四卡上保持每卡发送量相同，分别核算两种环顺序占用的每个物理方向。
- [GPU 发起通信：数据传输、通知和等待怎样配合](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/gpu-initiated-communication/)　从 PE 和对称对象追踪带通知的 GPU 传输。
- [NCCL 与 RCCL：通信组、执行依赖和底层路径怎样连接](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/nccl-rccl-contracts/)　核对通信组、GPU 流依赖和调用返回时刻。
- [CUDA 与 HIP 对端访问（原章节入口）](https://microarch-flow.github.io/wiki/SCALEUP/wiki/04-software-and-collectives/peer-access-setup/)　原入口。见上表中的分节去向。

### [05 负载与性能](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/)

- [多卡通信怎样测试：正确性、路径和计时边界一起记录](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/benchmarking/)　用 NCCL Tests 记录正确性、实际路径和计时口径。
- [带宽与时延指标：先统一字节、方向和观察边界](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/metrics-and-units/)　对照算法带宽、总线带宽和链路方向。
- [MoE 分发与回收：平均流量为何掩盖热点](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/moe-dispatch-and-combine/)　用 MoE 目的分布解释总量相同却出现热点。
- [通信与计算重叠：怎样计算没有被隐藏的时间](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/overlap-and-critical-path/)　在通信与计算共享资源时区分覆盖时间和暴露时间。
- [TP、PP、DP：从计算切分得到通信事件](https://microarch-flow.github.io/wiki/SCALEUP/wiki/05-workloads-and-performance/parallelism-traffic/)　从 TP、PP、DP 的张量切分推导消息形状。

### [06 建模、诊断与查阅](https://microarch-flow.github.io/wiki/SCALEUP/wiki/06-modeling-and-reference/)

- [多卡通信异常定位：先找失败边界，再改变配置](https://microarch-flow.github.io/wiki/SCALEUP/wiki/06-modeling-and-reference/diagnosis-and-recovery/)　把异常缩小到访问、路由、完成或消费的一处。
- [加速器互连术语、版本与一手资料](https://microarch-flow.github.io/wiki/SCALEUP/wiki/06-modeling-and-reference/glossary-and-sources/)　查加速器术语、协议版本与厂商一手材料。
- [从通信矩阵到性能下界：一个四端点预算例子](https://microarch-flow.github.io/wiki/SCALEUP/wiki/06-modeling-and-reference/traffic-budget-example/)　用一个四端点矩阵将通信量换算成资源时间下界。

## 系统网络

从[专题首页](https://microarch-flow.github.io/wiki/NETWORK/wiki/)进入。

### [01 基础概念](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/)

- [帧长、MTU 与包率：额定带宽怎样变成有效数据？](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/frame-mtu-and-rate/)　由 Ethernet 的帧长度、线开销和包率算有效吞吐。
- [同样发 4 KiB，TCP 和 RDMA 什么时候能复用缓冲区？](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/host-nic-data-path/)　比较普通 TCP 与 RDMA 交付 4 KiB 时发送、接收和槽归还的时刻。
- [系统网络的对象与分层：一次通信到底传输了什么？](https://microarch-flow.github.io/wiki/NETWORK/wiki/01-foundations/objects-and-layers/)　把应用消息、端点操作、传输包和线路帧分层。

### [02 Ethernet 与 IP 网络](https://microarch-flow.github.io/wiki/NETWORK/wiki/02-ethernet-and-ip/)

- [Clos、ECMP 与多轨：多条链路为什么仍会形成瓶颈？](https://microarch-flow.github.io/wiki/NETWORK/wiki/02-ethernet-and-ip/clos-ecmp-and-rails/)　从 Clos 和 ECMP 选路定位多路径中的共享出口。
- [Ethernet、IP、TCP 与 UDP：谁负责找到并交付数据？](https://microarch-flow.github.io/wiki/NETWORK/wiki/02-ethernet-and-ip/forwarding-and-transport/)　沿一次跨子网传输区分链路、网络与传输层。
- [丢包、重传与拥塞控制：可靠交付怎样与有限带宽配合？](https://microarch-flow.github.io/wiki/NETWORK/wiki/02-ethernet-and-ip/loss-recovery-and-ecn/)　用 TCP 窗口、重传和 ECN 解释丢包后的可靠交付。
- [队列、Incast 与尾延迟：带宽够用时为什么还会等待？](https://microarch-flow.github.io/wiki/NETWORK/wiki/02-ethernet-and-ip/queues-incast-and-tail-latency/)　从突发的到达速率和服务能力算 Incast 排队。

### [03 RDMA 端点](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/)

- [RDMA 排序、完成与缓冲区复用（原章节入口）](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/completion-ordering-and-lifetime/)　原入口。见上表中的分节去向。
- [内存注册与访问权限：远端怎样获得合法目标？](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/memory-registration-and-permissions/)　追踪注册、授权、远端访问和回收的依赖。
- [QP、工作队列与 CQ：RDMA 请求怎样进入设备？](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/queues-and-connection/)　以 RC 检查 QP、发送接收队列及完成队列的关系。
- [Send、Write、Read 与原子操作：双方分别需要准备什么？](https://microarch-flow.github.io/wiki/NETWORK/wiki/03-rdma-endpoints/send-read-write-and-atomics/)　对比四类 verbs 在两端各需准备的资源。

### [04 RoCE](https://microarch-flow.github.io/wiki/NETWORK/wiki/04-roce/)

- [RoCE 部署条件：地址、MTU、QoS 与权限怎样对齐？](https://microarch-flow.github.io/wiki/NETWORK/wiki/04-roce/deployment-and-isolation/)　沿地址、MTU、QoS、权限逐项排除部署故障。
- [ECN、CNP 与 DCQCN：发送端怎样知道该减速？](https://microarch-flow.github.io/wiki/NETWORK/wiki/04-roce/ecn-cnp-and-dcqcn/)　沿标记包到接收端，再跟 CNP 回到源端减速。
- [PFC、Headroom 与暂停传播：怎样避免缓冲溢出？](https://microarch-flow.github.io/wiki/NETWORK/wiki/04-roce/pfc-headroom-and-stalls/)　在同一个热点出口算 ECN、PFC 的两个门槛及暂停在途余量。
- [一次 RoCEv2 传输：RDMA 怎样穿过 IP 网络？](https://microarch-flow.github.io/wiki/NETWORK/wiki/04-roce/rocev2-packet-and-path/)　沿一次 RoCEv2 操作查看 IP、UDP 和以太网封装。

### [05 InfiniBand](https://microarch-flow.github.io/wiki/NETWORK/wiki/05-infiniband/)

- [InfiniBand、RoCE 与 iWARP：相似 RDMA 接口为何需要不同网络？](https://microarch-flow.github.io/wiki/NETWORK/wiki/05-infiniband/ib-roce-iwarp-comparison/)　按传输、管理与承载条件比较三类 RDMA 网络。
- [InfiniBand 子网：SM、LID、GID 与路径怎样建立？](https://microarch-flow.github.io/wiki/NETWORK/wiki/05-infiniband/subnets-addresses-and-sm/)　区分子网管理、寻址、路由及分区。
- [SL、VL 与信用：InfiniBand 怎样分配链路资源？](https://microarch-flow.github.io/wiki/NETWORK/wiki/05-infiniband/vl-credit-routing-and-congestion/)　从服务类到虚拟通道，定位信用约束的链路。

### [06 系统集成与新协议](https://microarch-flow.github.io/wiki/NETWORK/wiki/06-system-integration/)

- [GPUDirect RDMA：NIC 怎样访问 GPU 内存并交付结果？](https://microarch-flow.github.io/wiki/NETWORK/wiki/06-system-integration/gpudirect-rdma/)　沿 GPU 显存和网卡之间的数据放置追踪交付。
- [通信库与 NIC 放置：应用怎样选到真实网络路径？](https://microarch-flow.github.io/wiki/NETWORK/wiki/06-system-integration/libraries-and-nic-placement/)　将通信库、进程、GPU 和 NIC 对应到实际路径。
- [Ultra Ethernet 与 UET：新的传输怎样与以太网配合？](https://microarch-flow.github.io/wiki/NETWORK/wiki/06-system-integration/ultraethernet-uet/)　以 UE 1.1 为基线查 UET 与以太网增强各自职责。

### [07 性能、诊断与查阅](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/)

- [怎样测试 TCP 与 RDMA：先验证路径，再比较性能](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/benchmarking/)　沿可达性、功能、计时和统计逐层验证 TCP/RDMA 测试。
- [停顿、丢包与性能下降：怎样沿证据定位故障？](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/diagnosis-and-recovery/)　将计数器的观测时间与具体停顿、丢包及完成挂起对齐。
- [术语、版本与一手资料：怎样复核系统网络结论？](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/glossary-and-sources/)　追溯系统网络术语、规范版本及适用范围。
- [网络性能预算：怎样统一单位、方向与完成边界？](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/metrics-and-budget/)　把网络、PCIe 和软件边界的下界放到同一口径。
- [RPC、存储与集群通信：怎样把业务变成网络需求？](https://microarch-flow.github.io/wiki/NETWORK/wiki/07-performance-and-reference/workload-patterns/)　将 RPC、存储与集群业务的到达和完成要求换算成网络需求。

## 高速电链路

从[专题首页](https://microarch-flow.github.io/wiki/SERDES/wiki/)进入。主线集中在同一个字的传送。均衡、恢复时钟、训练、误码和实测方法继续独立查阅。

### [01 全局链路：一组数据怎样到达另一端？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/)

- [一个 32 位字怎样穿过 SerDes，又怎样拼回来？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/link-end-to-end/)　沿一个 32 位字走过发送、通道、采样和收端字边界。
- [PHY、SerDes 与协议是什么关系？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/phy-serdes-protocol/)　把 PHY、收发器和协议层的功能放到同一条传输路径。
- [位宽、线速率、符号率与时钟怎样换算？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/rates-clocks-and-ui/)　由并行时钟和位宽推导线速、符号率和 UI。
- [为什么需要 SerDes？](https://microarch-flow.github.io/wiki/SERDES/wiki/01-overview/why-serdes/)　比较并行引脚和串行 lane 需要承担的时序及线路成本。

### [02 电信号与通道：信号为什么会变化？](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/)

- [差分信号、共模与回流](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/differential-and-return/)　用差分和共模扰动检查失衡、回流怎样影响接收。
- [特性阻抗、终端与反射](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/impedance-and-reflection/)　在阻抗失配的终端追踪第一次反射。
- [ISI、串扰与噪声怎样影响判决？](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/isi-noise-and-eye/)　从离散抽样值分别识别 ISI、串扰与噪声。
- [怎样读损耗、dB 和 S 参数？](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/loss-db-and-s-parameters/)　从 dB 和 S 参数读取给定参考面上的通道损耗。
- [时序偏差、抖动和采样窗口](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/timing-skew-and-jitter/)　用 UI 统一时钟偏差、抖动和采样窗口的口径。
- [电压、电流和有限的翻转时间](https://microarch-flow.github.io/wiki/SERDES/wiki/02-signal-channel/voltage-current-and-switching/)　用有限驱动和负载解释电压翻转需要时间。

### [03 发送端：怎样把并行位送进通道？](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/)

- [PLL、分频与多相时钟怎样工作？](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/clock-pll-and-multiphase/)　把分频、整数倍频与多相时钟放入同一计时关系。
- [发送驱动、摆幅与终端](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/driver-swing-and-termination/)　按负载与终端查看发送摆幅的实际观察点。
- [并行字与串行流（原章节入口）](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/parallel-to-serial/)　原入口。见上表中的分节去向。
- [发送均衡与 FFE：为什么要改变发送波形？](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/tx-equalization-ffe/)　用两个 FFE 抽头调整发送符号，再与通道串接。
- [走一遍 TX 教学案例](https://microarch-flow.github.io/wiki/SERDES/wiki/03-transmitter/tx-path-worked-example/)　在同一个 TX 波形例子里打开、关闭发送均衡。

### [04 接收端：怎样从受损波形恢复数据？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/)

- [接收前端与 CTLE 做什么？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/analog-frontend-and-ctle/)　比较 CTLE 对频响、增益和噪声的影响。
- [CDR 怎样恢复采样时序？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/cdr-and-timing-recovery/)　跟随相位误差和采样时刻构成 CDR 反馈。
- [解串、字边界与时钟域（原章节入口）](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/deserializer-and-alignment/)　原入口。见上表中的分节去向。
- [DFE 怎样使用历史判决？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/dfe-and-error-propagation/)　用旧判决消除后游标，观察一次误判怎样传播。
- [接收端有哪些数据与反馈路径？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/receiver-signal-chain/)　辨认接收端的前端、采样、判决与反馈各支路。
- [走一遍 RX 协同案例](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/rx-cooperation-example/)　把通道衰减、均衡和实际判决放到一个例子里。
- [采样器怎样把波形变成判决？](https://microarch-flow.github.io/wiki/SERDES/wiki/04-receiver/sampler-and-decision/)　改变门限或采样时间，比较同一 NRZ 波形的判决。

### [05 信号与指标：怎样读懂链路数据？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/)

- [怎样计算带宽和每比特能耗？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/bandwidth-power-efficiency/)　把线路位数与有效载荷分别作为带宽、每比特能耗分母。
- [BER、置信度与 FEC 怎样关联？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/ber-confidence-and-fec/)　把测到的错误数、置信度和 FEC 前后观察点分开。
- [线路编码与加扰解决什么问题？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/coding-and-scrambling/)　比较编码与加扰对开销和跳变特征的影响。
- [怎样理解眼图和抖动？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/eye-and-jitter/)　在指定参考面上读眼高、眼宽和时序裕量。
- [NRZ 与 PAM4：比特怎样映射到符号？](https://microarch-flow.github.io/wiki/SERDES/wiki/05-signaling-and-metrics/nrz-and-pam4/)　把同一组比特按 NRZ、PAM4 映射到不同符号。

### [06 初始化与链路训练：链路怎样建立和维持？](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/)

- [初始化与校准：先让模块具备工作条件](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/initialization-calibration/)　沿复位、参考时钟和校准结果检查初始化状态。
- [多 lane 为什么需要对齐？](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/lane-alignment/)　用两条 lane 到达有先后解释 deskew 的职责。
- [PCIe 链路训练案例：从现象到证据](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/pcie-training-case/)　对照构造的训练日志及状态变化排查 PCIe 链路。
- [重训练与运行观察：怎样定位变化？](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/retraining-and-observation/)　按时间线查运行中重训练的原因、证据和影响。
- [训练与自适应：谁观察，谁调整？](https://microarch-flow.github.io/wiki/SERDES/wiki/06-link-operation/training-and-adaptation/)　从观察量、训练请求和参数更新组成自适应过程。

### [07 设计与验证：怎样建立可信证据？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/)

- [接收架构和均衡怎样选择？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/architecture-tradeoffs/)　以同一接收目标比较两类架构及均衡代价。
- [电路、版图与 PVT 怎样影响结果？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/circuit-layout-and-pvt/)　区分工艺电压温度角、统计变化与版图连接效果。
- [怎样判断自研范围和可用性证据？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/in-house-evidence/)　将自研范围对应到具体模块、交付物和实证。
- [实验室、合规与互通测试怎样分工？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/lab-compliance-interop/)　区分实验室特性、合规测试和跨设备互通的证据。
- [怎样把链路需求写成可验证的契约？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/requirements-and-contract/)　把线路需求写成带条件与观察边界的可验证约定。
- [通道模型和仿真能回答什么？](https://microarch-flow.github.io/wiki/SERDES/wiki/07-design-and-validation/system-and-channel-models/)　区分模型层次及通道、器件和系统仿真的适用范围。

### [08 系统应用：把链路放回实际连接场景](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/)

- [Chiplet 与 D2D：怎样选择封装内互连？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/chiplet-and-d2d/)　在封装内比较宽并行、窄高速及其协议承担的职责。
- [CPO：电链路怎样接入光链路？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/cpo-electrical-optical/)　衔接电链路和光引擎，明确不同功率预算的观察点。
- [HBM 与 3D 堆叠：数据经过哪些连接？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/hbm-and-3d/)　沿堆叠结构追踪 HBM 数据路径并手算总带宽。
- [增加 lane 还是提高单 lane 速率？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/lane-count-vs-rate/)　在总线速相同的前提比较加 lane 和提单 lane 速率。
- [PCIe 与以太网：共用什么，又在哪里不同？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/pcie-and-ethernet/)　区分 PCIe 与以太网复用的电气概念和各自协议边界。
- [怎样阅读公开的 SerDes 产品声明？](https://microarch-flow.github.io/wiki/SERDES/wiki/08-system-applications/product-claims-and-evidence/)　给公开产品指标标出版本、测试条件与证明范围。

### [09 建模：怎样把链路放进系统模型？](https://microarch-flow.github.io/wiki/SERDES/wiki/09-modeling/)

- [链路状态、失败与恢复怎样建模？](https://microarch-flow.github.io/wiki/SERDES/wiki/09-modeling/link-state-and-failure/)　将失败、暂停和恢复作为有状态的链路服务建模。
- [怎样选择链路模型的层次？](https://microarch-flow.github.io/wiki/SERDES/wiki/09-modeling/modeling-scope/)　依据问题挑选线路、电气或服务级模型。
- [怎样定义速率、延迟与功耗？](https://microarch-flow.github.io/wiki/SERDES/wiki/09-modeling/rate-latency-power/)　把服务速率、串行化、延迟以及能耗参数分开。
- [走一遍有恢复停顿的链路模型](https://microarch-flow.github.io/wiki/SERDES/wiki/09-modeling/worked-model-and-limits/)　用一个恢复停顿例子逐步计算任务完成时间。

### [SerDes 术语、资料与自测](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/)

- [链路与电气术语](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/glossary/)　检索链路与电气对象的术语。
- [信号、指标与训练术语](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase2-glossary/)　查信号、误码、均衡和训练词义。
- [信号、指标与训练自测](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase2-self-check/)　用信号、指标和训练题检查口径及因果。
- [信号、指标与训练资料](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase2-sources/)　按信号、指标和训练问题回查资料。
- [设计、系统与建模术语](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase3-glossary/)　查设计、系统应用与模型中的术语。
- [设计、系统与建模自测](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase3-self-check/)　用设计、系统和建模练习检验假设。
- [设计、系统与建模资料](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/phase3-sources/)　按设计、系统和建模问题查出处。
- [链路收发自测](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/questions-and-self-check/)　按收发路径练习时钟、采样、通道与位序。
- [链路与电气资料](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/sources/)　按电信号和收发器对象查资料。
- [符号、单位和参考面](https://microarch-flow.github.io/wiki/SERDES/wiki/10-reference/symbols-and-units/)　复核 UI、bit、baud、dB、误码和功耗的单位及参考面。

## 共封装光学

从[专题首页](https://microarch-flow.github.io/wiki/CPO/wiki/)进入。技术、产业、论文与维护资料各有独立入口。公司角色卡供定位，具体公告以深卡中的日期和原始资料为准。

- [知识地图](https://microarch-flow.github.io/wiki/CPO/wiki/SUMMARY/)　按章节和问题查找各篇文章。

### [01 概览与问题定义](https://microarch-flow.github.io/wiki/CPO/wiki/01-overview/)

- [学习路线图的原章节入口](https://microarch-flow.github.io/wiki/CPO/wiki/01-overview/learning-roadmap/)　原入口。见上表中的分节去向。
- [CPO 在解决什么问题](https://microarch-flow.github.io/wiki/CPO/wiki/01-overview/problem-statement/)　从交换 ASIC 到连接器的电通道入手，辨认共封装改变的位置。
- [CPO 分类框架](https://microarch-flow.github.io/wiki/CPO/wiki/01-overview/taxonomy/)　按系统位置、光源位置和集成方式分类。

### [02 产业链与角色](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/)

- [公司与平台图谱](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-landscape/)　按公司角色寻找交换平台、光引擎与供应链参与者。
- [生态关系图与协作逻辑](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/ecosystem-relationships/)　按系统、光器件、封装和测试之间的交付关系读图。
- [路线对比表](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/route-comparison/)　比较不同产业角色推动 CPO 采用的路线。
- [产业链与角色](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/value-chain/)　从上游材料和器件向下追到光引擎与系统整合方。

### [公司卡片](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/)

- [Broadcom：交换芯片主导型 CPO 观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/broadcom-switch-cpo/)　聚焦交换 ASIC 与整机 I/O 边界；公开产品进展另见公司深卡。
- [Cisco：系统与硅光协同型 CPO 观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/cisco-system-silicon-photonics/)　聚焦网络系统和硅光协同；按深卡回查具体公告。
- [Intel：硅光平台型 CPO 观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/intel-silicon-photonics/)　聚焦硅光平台与制造能力；按深卡核对演示条件。
- [Marvell：互连与平台协同型 CPO 观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/marvell-interconnect-platform/)　聚焦互连器件与平台协同；与详细公司资料分开查阅。
- [NVIDIA：AI 网络牵引型 CPO 观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/02-industry/company-cards/nvidia-ai-network-cpo/)　聚焦 AI 网络系统需求；厂商公告与日期另见深卡。

### [03 系统架构与集成平台](https://microarch-flow.github.io/wiki/CPO/wiki/03-architecture-platform/)

- [封装与集成路线](https://microarch-flow.github.io/wiki/CPO/wiki/03-architecture-platform/packaging-routes/)　对照封装路线与电子、光学器件的集成边界。
- [系统栈与接口位置](https://microarch-flow.github.io/wiki/CPO/wiki/03-architecture-platform/system-stack/)　从交换芯片向外对照可插拔与共封装的位置。

### [04 光引擎与核心器件](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/)

- [激光器、调制器与探测器的原章节入口](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/laser-modulator-detector/)　原入口。见上表中的分节去向。
- [一个比特怎样从电路进入光纤，再回到电路？](https://microarch-flow.github.io/wiki/CPO/wiki/04-optical-engine/optical-link-basics/)　沿一束光关联器件职能、波长映射和通道功率预算。

### [05 电性能、热与可靠性](https://microarch-flow.github.io/wiki/CPO/wiki/05-electrical-thermal-reliability/)

- [带宽、功耗与热](https://microarch-flow.github.io/wiki/CPO/wiki/05-electrical-thermal-reliability/bandwidth-power-thermal/)　比较不同负载下每比特能耗、功耗密度与温度。
- [测试、可靠性与失效定位](https://microarch-flow.github.io/wiki/CPO/wiki/05-electrical-thermal-reliability/reliability-test/)　把测试阶段、可更换边界及失效定位放在一起考虑。

### [06 制造、测试与良率](https://microarch-flow.github.io/wiki/CPO/wiki/06-manufacturing/)

- [KGD、装配良率与系统良率](https://microarch-flow.github.io/wiki/CPO/wiki/06-manufacturing/known-good-die-and-yield/)　区分裸片已知良好、装配良率和系统良率。
- [制造流程](https://microarch-flow.github.io/wiki/CPO/wiki/06-manufacturing/process-flow/)　沿制造顺序定位光纤耦合、测试和封装的交接。

### [07 应用场景与经济性](https://microarch-flow.github.io/wiki/CPO/wiki/07-applications-economics/)

- [落地障碍与商业化判断](https://microarch-flow.github.io/wiki/CPO/wiki/07-applications-economics/adoption-barriers/)　按客户验证、维护和成本条件判断商业采用的障碍。
- [AI 集群场景与使用逻辑](https://microarch-flow.github.io/wiki/CPO/wiki/07-applications-economics/ai-cluster-use-cases/)　以 AI 集群端口密度、功耗和维护条件讨论应用。

### [08 研究模板与术语](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/)

- [4 天学习计划与阅读提问清单](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/4-day-study-plan/)　按四天阅读次序为论文带入不同的复核问题。
- [公司分析模板](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/company-analysis-template/)　用产品出处、控制环节和可推翻条件做公司研究笔记。
- [术语表](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/glossary/)　按 CPO 器件、接口与发布资料查易混术语。
- [论文阅读模板](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-review-template/)　统一记录论文的假设、数据、比较条件与局限。
- [CPO 入门必读 10 篇](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/reading-pack-cpo-top-10/)　从预选文献建立阅读顺序并找到原始材料。

### [案例库](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/case-studies/)

- [案例：外置激光 CPO 论文怎么读](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/case-studies/external-laser-cpo-paper/)　练习从外置光源论文提取分光、耦合与供光边界。
- [案例：系统动机型论文怎么读](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/case-studies/system-motivation-paper/)　练习判断系统动机型论文选择的约束和比较基线。
- [案例：热与可靠性论文怎么读](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/case-studies/thermal-reliability-paper/)　练习核对热可靠性论文的温度、工况与验证证据。

### [完整论文卡](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/detailed-cards/)

- [完整卡：CPO status, challenges, and solutions](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/detailed-cards/cpo-status-challenges-solutions/)　记录综述对系统障碍和方案的归纳，回到原文查范围。
- [完整卡：In-Package Optical I/O](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/detailed-cards/in-package-optical-io/)　用封装内光 I/O 材料复核集成位置和系统目标。
- [完整卡：TeraPHY optical I/O chiplet](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/detailed-cards/teraphy-chiplet/)　跟随 TeraPHY 案例核对光 I/O 芯粒的边界与作用。

### [论文卡片库](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/)

- [外置激光与光源架构类论文卡片](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/external-laser-papers/)　筛选讨论外置光源位置、余量和维护的研究资料。
- [封装集成类论文卡片](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/packaging-integration-papers/)　按封装方式、耦合方式及验证条件整理文献。
- [硅光与光引擎类论文卡片](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/silicon-photonics-engine-papers/)　按器件指标与系统指标筛选硅光引擎论文。
- [系统架构类论文卡片](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/system-architecture-papers/)　按系统动机与约束提取架构类论文的可比数据。
- [热与可靠性类论文卡片](https://microarch-flow.github.io/wiki/CPO/wiki/08-research/paper-cards/thermal-reliability-papers/)　收集温度、热源、寿命和验证条件的文献入口。

### [09 供应链与区域格局](https://microarch-flow.github.io/wiki/CPO/wiki/09-supply-chain-geography/)

- [成本、量产与 adoption 约束](https://microarch-flow.github.io/wiki/CPO/wiki/09-supply-chain-geography/cost-yield-adoption/)　按成本拆分、量产条件和验证进度追问采用门槛。
- [区域格局：美国、台湾地区、日本、欧洲、中国大陆](https://microarch-flow.github.io/wiki/CPO/wiki/09-supply-chain-geography/regional-landscape/)　从区域分工寻找不同环节的公开证据。
- [供应链分层地图](https://microarch-flow.github.io/wiki/CPO/wiki/09-supply-chain-geography/supply-chain-stack/)　按供应链层次追踪每个环节的交付物。

### [10 重点公司与合作关系图谱](https://microarch-flow.github.io/wiki/CPO/wiki/10-company-ecosystem/)

- [公司分组地图](https://microarch-flow.github.io/wiki/CPO/wiki/10-company-ecosystem/company-groups/)　把平台主导者、器件、封装与配套供应商分组。
- [如何研究一家公司在 CPO 生态中的位置](https://microarch-flow.github.io/wiki/CPO/wiki/10-company-ecosystem/how-to-study-a-company/)　用产品、控制点、合作类型和证据研究一家企业。
- [重点组合案例](https://microarch-flow.github.io/wiki/CPO/wiki/10-company-ecosystem/key-combinations/)　把明确披露过的组合关系放到具体平台与系统中。
- [合作关系图](https://microarch-flow.github.io/wiki/CPO/wiki/10-company-ecosystem/partnership-map/)　按证据类型和日期区分投资、合作、演示及供货。

### [11 重点公司深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/)

- [AMD 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/amd/)　查 AMD 所控制的环节及其收购、合作的原始证据。
- [Ayar Labs 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/ayar-labs/)　查 Ayar Labs 光 I/O 芯粒路线及公开合作关系。
- [Broadcom 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/broadcom/)　区分 Broadcom 不同代产品的公告、出货和客户部署证据。
- [Cisco 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/cisco/)　从 Cisco 系统与硅光路线向下追溯原始公告。
- [Intel 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/intel/)　查 Intel 硅光路线、演示边界和可验证指标。
- [Marvell 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/marvell/)　查 Marvell 互连与光平台的产品、客户入口和条件。
- [NVIDIA 深卡](https://microarch-flow.github.io/wiki/CPO/wiki/11-deep-company-cards/nvidia/)　查 NVIDIA 网络平台、光互连合作与原始材料。

### [12 研究结论与竞争观察框架](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/)

- [如何持续跟踪 CPO 竞争格局](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/how-to-track/)　按季度复核证据，记录哪些信号足以改变判断。
- [阶段性研究结论](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/interim-conclusions/)　保留有日期的阶段判断，供与后续公开事实对照。
- [长期主线与次主线判断](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/long-term-route-view/)　比较并行路线在不同边界与时间尺度下的成立条件。
- [如何比较 CPO 商用进展](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/who-scales-first/)　按量产、出货、演示等证据层级比较商业进度。
- [平台角色、关键部件与风险](https://microarch-flow.github.io/wiki/CPO/wiki/12-conclusions-competition/winners-components-risks/)　从平台角色、关键部件与风险三处比较主张。

### [13 一页版总览](https://microarch-flow.github.io/wiki/CPO/wiki/13-one-page-summary/)

- [CPO 一页版总览](https://microarch-flow.github.io/wiki/CPO/wiki/13-one-page-summary/cpo-one-page/)　快速回顾定义、集成位置和工程取舍。

### [14 术语、公司与路线索引](https://microarch-flow.github.io/wiki/CPO/wiki/14-indexes/)

- [公司索引表](https://microarch-flow.github.io/wiki/CPO/wiki/14-indexes/company-index/)　从公司名称跳到角色卡、深卡或来源。
- [路线索引表](https://microarch-flow.github.io/wiki/CPO/wiki/14-indexes/route-index/)　从技术与产业路线找到相应专题。
- [术语索引表](https://microarch-flow.github.io/wiki/CPO/wiki/14-indexes/term-index/)　按中英文词条查定义和首次解释。

### [15 中国大陆机会点专题](https://microarch-flow.github.io/wiki/CPO/wiki/15-china-opportunities/)

- [中国大陆在 CPO 生态中的位置](https://microarch-flow.github.io/wiki/CPO/wiki/15-china-opportunities/china-position/)　列出中国大陆相关研究范围，区分假设与公开证据。
- [主要约束与短板](https://microarch-flow.github.io/wiki/CPO/wiki/15-china-opportunities/constraints/)　把平台准入、器件能力和工程积累落到具体核实问题。
- [研究与跟踪框架](https://microarch-flow.github.io/wiki/CPO/wiki/15-china-opportunities/how-to-track-china/)　按验证里程碑追踪中国大陆相关企业和项目。
- [中国大陆可研究的机会环节](https://microarch-flow.github.io/wiki/CPO/wiki/15-china-opportunities/opportunity-areas/)　按连接、装配与测试等交付物分解潜在机会。

### [16 学习顺序导航](https://microarch-flow.github.io/wiki/CPO/wiki/16-learning-navigation/)

- [CPO 学习顺序导航页](https://microarch-flow.github.io/wiki/CPO/wiki/16-learning-navigation/study-navigation/)　按读者问题组织器件、制造和产业资料的阅读次序。

### [17 研究汇报模板](https://microarch-flow.github.io/wiki/CPO/wiki/17-report-template/)

- [CPO 研究汇报模板](https://microarch-flow.github.io/wiki/CPO/wiki/17-report-template/cpo-report-template/)　按汇报时长组织系统边界、证据和结论。

### [18 来源与更新时间](https://microarch-flow.github.io/wiki/CPO/wiki/18-sources-and-updates/)

- [公司生态与时效性来源表](https://microarch-flow.github.io/wiki/CPO/wiki/18-sources-and-updates/company-ecosystem-sources/)　维护公司生态判断对应的原始资料与核阅时间。

### [19 版本说明与使用说明](https://microarch-flow.github.io/wiki/CPO/wiki/19-versioning-and-usage/)

- [当前完成度评估](https://microarch-flow.github.io/wiki/CPO/wiki/19-versioning-and-usage/current-coverage/)　保留当时的覆盖范围和带日期的主观评估。
- [如何维护和继续扩展](https://microarch-flow.github.io/wiki/CPO/wiki/19-versioning-and-usage/how-to-maintain/)　供后续维护者核对新增证据、更新次序与链接。
- [这套 wiki 适合谁、适合做什么](https://microarch-flow.github.io/wiki/CPO/wiki/19-versioning-and-usage/who-is-this-for/)　界定适读对象和资料的使用方式。

### [20 编辑规范与页面模板](https://microarch-flow.github.io/wiki/CPO/wiki/20-editorial-style/)

- [公司页模板](https://microarch-flow.github.io/wiki/CPO/wiki/20-editorial-style/company-page-template/)　供维护者把短角色卡与有证据的公司深卡分别成文。
- [论文页模板](https://microarch-flow.github.io/wiki/CPO/wiki/20-editorial-style/paper-page-template/)　供维护者把文献短卡和长卡写成一致结构。
- [术语与写法约定](https://microarch-flow.github.io/wiki/CPO/wiki/20-editorial-style/terminology-style/)　统一术语、核阅日期以及公司关系的写法。
- [主题页模板](https://microarch-flow.github.io/wiki/CPO/wiki/20-editorial-style/topic-page-template/)　定义主题文章的问题、证据与适用边界。
