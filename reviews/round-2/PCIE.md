# PCI Express逐篇评审

[返回九专题索引](README.md) · [PCIE 专题入口](../../PCIE/wiki/README.md)

## 专题入口

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [PCIE Wiki](../../PCIE/wiki/README.md) · 已修订 | 首页分发专题，其 dashboard 承诺的地址术语应和目标页一致。 | 读者按 PIO 入口查找，却会进入只解释配置、MMIO 和 DMA 的页面。 | 查询配置访问、CPU 的 BAR 访问与设备 DMA 可用该入口；本章没有在该目标页单独定义 PIO。 | 把“MMIO / PIO / DMA 地址视角”改成目标页已有的“配置访问、BAR/MMIO 与 DMA 地址”；其余路线保留。<br>**独立复核** 索引改为配置访问、BAR/MMIO、DMA 地址，链接与目标内容匹配。 |
| [知识地图](../../PCIE/wiki/SUMMARY.md) · 保留 | 知识地图是八章一级目录并提供快速、系统或调试切入点。 | 避免把章节导航与深度协议描述混排。 | 按目的跳转到首页、学习或调试；该页无可量化参数。 | “这页只保留章节级入口”与八个链接一致，保留。 |

## 01 概览与问题定义

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [01 概览与问题定义](../../PCIE/wiki/01-overview/README.md) · 保留 | 本章索引将系统需求、分类、学习顺序和目标导航连为入口。 | 初读者可先选工程问题，再读专题。 | 按全局分类还是按目标选路只改变阅读顺序。 | “推荐阅读顺序”列出四个各司其职的入口，保留。 |
| [按目标学习 PCIE](../../PCIE/wiki/01-overview/goal-oriented-navigation.md) · 保留 | 五条阅读路径分别服务系统判断、驱动、bring-up、性能和虚拟化。 | 面对不同问题时，可直接找到负责该机制的页。 | 读延迟选性能组；配置不可达选 bring-up 组，路线不设定实际设备能力。 | “目标 3”和“目标 4”分别链接错误状态与并发分析，保留。 |
| [学习路线图](../../PCIE/wiki/01-overview/learning-roadmap.md) · 保留 | 五阶段把系统角色、事务配置、运行路径、观察和案例串起。 | 避免在理解参与者前推断字段和性能。 | 初学从拓扑开始，已有具体目标可转上方目标导航。 | “阶段 2”明写识别设备与收发事务的目标；“阶段 3”连到主机数据链，保留。 |
| [PCIE 在解决什么问题](../../PCIE/wiki/01-overview/problem-statement.md) · 保留 | PCIe 提供主机与端点间的事务、设备发现与配置契约；IOMMU 提供平台隔离。 | 解释多种外设如何共享主机的软件资源模型。 | 涉及外设发现、映射或 DMA 时走 PCIe 路径；片内路由或跨机通信另有相应协议。 | “它和相邻主题怎么分工”及 NIC、NVMe 场景已限定讨论边界，保留。 |
| [PCIE 分类框架](../../PCIE/wiki/01-overview/taxonomy.md) · 已修订 | AER 是扩展错误报告；链路重放是链路协议对丢失或损坏数据的恢复。 | 五层参数表会决定误码、重放和统计间的因果关系。 | 链路错误触发重放时增加占用并可能留下错误记录；报告使能或日志条数本身不能生成重放。 | 换掉“系统能力层／AER 引发的 replay 开销”；拆成链路重放计数和 AER 可观察性，注明方向、工作负载。<br>**独立复核** AER 状态与方向性重放增量分别采样，报告使能与链路重放没有错误因果。 |

## 02 链路、分层与事务基础

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [02 链路、分层与事务基础](../../PCIE/wiki/02-link-transaction-basics/README.md) · 已修订 | TLP 承载事务，Completion 自身是 TLP；传统 DLLP 为相邻链路传输控制信息。 | 章头会影响读者把三者理解成串行阶段还是不同种类。 | posted Memory Write 无事务级 Completion；逐跳 ACK 也不能替代完成返回。 | 改写“一个请求为什么会表现成 TLP、DLLP 和 completion”，直接指向两种不同返回。<br>**独立复核** 章节入口将事务请求/返回 TLP 与逐跳 Non-Flit ACK/NAK 区分，posted 无 Cpl。 |
| [分层架构：Transaction / Data Link / Physical](../../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md) · 已修订 | Transaction 层表达请求与匹配；传统 Data Link 层按链路确认或重放，流控在两端约束 TLP 发送；Physical 层决定通道状态与串行化。 | 读者需要知道三层分别处理哪种异常和等待。 | 未训练无法正常传送；相关 credit 不足会等待；链路级确认不释放端到端读 Tag；Flit 模式的控制承载形式不同。 | “Data Link Layer 关心什么”区分 TLP 发送条件与 UpdateFC 等链路交换；添请求经过一跳的例子并指明 Non-Flit。<br>**独立复核** 两跳 Non-Flit ACK 分属相邻端口，读 Tag 跟随事务完整返回；流控类别对应接收容量。 |
| [Posted / Non-Posted / Completion 与 Ordering](../../PCIE/wiki/02-link-transaction-basics/posted-nonposted-completion-ordering.md) · 已修订 | Memory Write 是 posted；Memory Read 和配置读写是 non-posted，响应含或不含数据；ordering 限制不同观察点可见的先后。 | 提交描述符和通知设备时，发包、到达和软件完成易被混同。 | 描述符在适用 DMA 发布/排序操作之后才敲 doorbell；非一致映射还要按平台同步，不能只依赖 PCIe 排序。 | “Ordering 为什么重要”已有故障样例，补正确发布顺序及观察者；“三个词”补成功配置写返回无数据 Cpl。<br>**独立复核** coherent CQ 的 phase→dma_rmb→内容，以及 streaming CQ 的独立交还→sync-for-CPU→首次读取，已用 Linux DMA 指南复核。 |
| [TLP、DLLP 与 Completion 语义](../../PCIE/wiki/02-link-transaction-basics/tlp-dllp-completion-basics.md) · 已修订 | Non-Flit DLLP 在一跳确认、更新流控；CplD 是事务级的读数据 TLP，按请求身份匹配。 | 缺少确认层级与 Tag 生命周期会导致模拟器提早释放并发槽。 | 一个读可多次返回 CplD，最后所需数据收齐才能正常回收该请求；一跳 ACK 不终结事务。 | “DLLP 是什么”限定模式；在“Completion 是什么”加两跳读例，区分链路确认、事务返回和软件 CQE。<br>**独立复核** 两跳可累计确认的 ACK 不释放读 Tag，完整或错误 Completion 与软件 CQE 明确分层。 |
| [Root Complex、Switch、Endpoint 在系统里各做什么](../../PCIE/wiki/02-link-transaction-basics/topology-root-complex-switch-endpoint.md) · 已修订 | RC 接主机域，交换机在端口间转发，EP 承载功能并可作 requester 或 completer。 | 路径角色决定请求发起方、共享带宽和仲裁位置。 | 两个 EP 同时向 host 发送且复用上行口时同向竞争；交换机本地允许的 P2P 可不占该上行口。 | “Root Complex 决定主机如何发…DMA”补设备 DMA 由 EP 发起；“带宽共享”加一张逐跳路径或短例。<br>**独立复核** EP 发起 DMA；共享交换机上行路径与可本地转发的 P2P 路径有可验证不同。 |

## 03 配置、枚举与地址映射

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [03 配置、枚举与地址映射](../../PCIE/wiki/03-configuration-enumeration-addressing/README.md) · 保留 | 配置章索引把标准配置、桥资源、CPU 访问窗口和设备 DMA 翻译分开。 | 读者能定位“看得到设备”和“设备能 DMA”所需的不同设置。 | 枚举定位与 I/O 地址翻译分属不同入口。 | “推荐阅读顺序”覆盖四个对象，不承担协议推演，保留。 |
| [配置空间、BAR 与 Capability](../../PCIE/wiki/03-configuration-enumeration-addressing/config-space-bar-capability.md) · 已修订 | 配置空间按 Function 提供管理入口；BAR 寄存器给出资源属性和被分配的总线地址，Capability 声明可选机制。 | 声明支持、分配资源与运行时允许访问是三个可分别观察的状态。 | 枚举可读配置但 BAR 未分配、桥窗口不转发或 Memory Space 未使能时，该 MMIO 访问不能按预期到达。 | “BAR 在做什么”加入分配、使能、译码的最短例；“Capability”区分声明 MSI-X 与实际配置/使能。<br>**独立复核** BAR 地址分配、沿桥窗口、MSE 译码和配置空间可发现相互独立；MSI-X 表项/使能与 capability 分开。 |
| [枚举、总线号与资源分配](../../PCIE/wiki/03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md) · 已修订 | 枚举软件沿桥发现已有设备/功能，建立桥总线号和地址窗口，并分配 BAR；驱动可随后使能相应功能。 | 混同地址标识与运行使能会让模型把资源不足诊断为未枚举。 | 下级总线不在桥的可转发范围会影响配置发现；未打开 bus master 仍可发现 Function；MSI-X 只在所选模式下需要。 | 改“分配 bus number / device / function”和“打开…MSI-X”；增加已枚举、BAR 可用、允许运行三个可区分的结果。<br>**独立复核** 发现已有 device/function 与桥 bus number 编程分开，诊断按枚举、MMIO 与 DMA 三层。 |
| [IOMMU、地址翻译与设备隔离](../../PCIE/wiki/03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md) · 已修订 | IOMMU 按请求身份选择域，翻译 DMA 地址并检查权限；IOTLB 缓存翻译。 | 要解释访问被拒与合法访问变慢的不同原因。 | 翻译使能且 IOTLB miss 时可进行页表遍历；映射缺失或权限不符走 fault 策略；旁路情形不同。 | “映射建立是否正确／TLB…开销”补一例同 IOVA 不同域及 hit、miss、fault 的输出，延迟留待平台标定。<br>**独立复核** 同一 IOVA 在两个域到不同页；IOTLB 命中、miss 后 walk 与 fault 后停止/恢复有不同输出。 |
| [MMIO、配置访问、DMA 地址空间视角](../../PCIE/wiki/03-configuration-enumeration-addressing/mmio-config-dma-address-view.md) · 保留 | 该页按发起者区分配置访问、CPU 对 BAR 的 MMIO 和设备对主机缓冲区的 DMA。 | 使驱动能辨认每次交互使用的地址对象。 | 典型队列交互先分配 BAR、再 MMIO 配置、设备另用 DMA 地址取描述符；DMA 地址未必等于 CPU 虚拟地址。 | “三种常见地址视角”和四步“典型交互”已直接回答，保留。 |

## 04 数据路径、DMA 与中断

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [04 数据路径、DMA 与中断](../../PCIE/wiki/04-data-path-dma-interrupts/README.md) · 保留 | 本章索引连起 descriptor 提交、读写、通知和内存可见性。 | 便于从真实运行路径进入不同专题。 | 想查读延迟走第 3 项；映射或缓存问题走第 4 项。 | “推荐阅读顺序”覆盖提交至完成和缓冲区专题，保留。 |
| [设备 DMA 的读写路径](../../PCIE/wiki/04-data-path-dma-interrupts/device-dma-read-write-flow.md) · 保留 | 设备经 MMIO 获知工作，经 DMA 读描述符并读输入或写结果，按设备协议回写完成。 | 相同应用动作可能消耗不同方向链路和资源。 | DMA 读依赖返回与可用 Tag；写设备结果受下游接收和主机内存约束。 | “一条常见提交路径”“为什么两者不能混看”已逐步对照，保留。 |
| [主机内存、Pinned Buffer 与设备可见性](../../PCIE/wiki/04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md) · 已修订 | Pin 保持页面可用与稳定，DMA 映射给出设备使用的地址，同步建立所有权和可见性。 | 仅有稳定页无法保证缓存已同步或映射还在。 | 传统显式映射须覆盖 DMA 生命周期；流式非一致映射按 DMA API 在交接处同步，确认设备结束后才撤映射、释放页。 | “三个必须同时成立的条件”补一次 CPU 写→同步给设备→设备结束→归还缓冲区；如提 SVA/PRI, 单独限定可分页场景。<br>**独立复核** 传统非一致 streaming buffer 的 map/sync、设备所有权、CPU 取回与解除映射的次序正确，分页 SVA 单列。 |
| [PCIe Read Completion 延迟为什么敏感](../../PCIE/wiki/04-data-path-dma-interrupts/pcie-read-completion-latency.md) · 已修订 | 读请求的有效在途时间覆盖发出至最终成功完成；Tag/槽和完成缓冲维持请求流水。 | 分片情况下首包延迟与并发槽实际占用时间不同。 | 分片慢时最终释放时间变长；同一稳态窗口 N、S 与 RTT 决定并发上界且受响应带宽限制。 | 保留“25 个”算例，在“量化小节”明确 RTT 起止与 N 是平均在途或硬容量上限；避免将 S 直接等于 MRRS。<br>**独立复核** 用完整返回 RTT、每请求平均有效负载、同窗口实际在途解释 Little 定律；25 个 tag 仅为必要条件。 |
| [队列、Doorbell、Completion 与 MSI-X](../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md) · 已修订 | SQ/ring 发布工作，doorbell 通知设备，CQE 记录命令状态，MSI-X 用可配置消息中断请求 CPU 服务。 | CPU 中断到达与具体命令完成的判定依赖不同对象。 | 中断屏蔽、合并或轮询时 CQE 仍可累积；设备按接口要求发布 CQE，主机验证有效状态后回收。 | 在“四个对象分别做什么”补队尾/有效位与生产消费方；将“该处理完成了”明确成服务通知，可一中断多 CQE。<br>**独立复核** SQ/CQ 的两端、有效位与 phase、门铃和 MSI-X 的职责分开，一个中断可覆盖多个 CQE。 |

## 05 性能与调试

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [05 性能与调试](../../PCIE/wiki/05-performance-debug/README.md) · 保留 | 本章入口区别链路能力、全路径瓶颈、错误统计和事务故障。 | 分析者可按观测到的问题选择下一页。 | 连续吞吐低与返回错误码分别转向第 1/2 项和第 3/4 项。 | 四个“推荐阅读顺序”入口已按性能和故障划分，保留。 |
| [AER、计数器与链路调试路径](../../PCIE/wiki/05-performance-debug/aer-counters-link-debug.md) · 已修订 | AER 记录和报告 PCIe 错误，分 correctable 与 uncorrectable，后者再分 non-fatal/fatal。 | “可恢复”容易误读为协议错误类别或固定恢复动作。 | 有些错误由链路纠正，另一些需软件恢复；观察到的日志还受报告使能、掩码和平台处理影响，不能直接转为重放次数。 | “AER 在做什么”换成规范分类；补同一窗口看错误状态与独立 replay 计数的例子。<br>**独立复核** Correctable / Uncorrectable 的层级正确，同一窗口分别观测 AER、重放、方向有效吞吐。 |
| [带宽、延迟、Credit、MPS 与 MRRS](../../PCIE/wiki/05-performance-debug/bandwidth-latency-credit-mps-mrrs.md) · 保留 | 名义带宽、有限 credit、MPS、MRRS 与 RCB 分别约束输送速率、接收容量、负载大小、读取长度和拆分位置。 | 避免从一个最大包长直接推导吞吐或完成包数。 | 256 B 对齐、MPS=256、RCB=64 可返回一包或四包；有限信用不足阻塞对应流。 | “量化小节”给 Non-Flit 假设、例外、无限通告与真实接收缓冲，足够保留。<br>**保留页抽查** Gen5 x16 单向编码后约 63.015 GB/s、128/(128+24)≈84.21% 均可复算；24 B 为 Non-Flit 假设，MPS/MRRS/RCB、无限通告与物理完成缓冲已分开。 |
| [Unsupported Request、Completer Abort、Timeout 怎么看](../../PCIE/wiki/05-performance-debug/common-failures-ur-ca-timeout.md) · 已修订 | UR 和 CA 可作为对应 non-posted 请求的 Completion Status；Completion Timeout 是 requester 在规定窗口内未获所需返回。 | 现有描述把协议超时和等待软件 CQ 的超时混在一起。 | 收到 UR/CA 有返回证据；在途读取未如期完成可能由 requester 报超时；CQ 软件超时可在所有 PCIe 事务正常时发生。 | 拆开“也可能是软件观察点等待错对象”；举配置/内存读，并说明 posted 请求没有普通错误 Cpl 路径。<br>**独立复核** non-posted 的 UR/CA 或协议 timeout，与软件等待 CQE 超时以及 posted MWr 无常规 Cpl 均有区分。 |
| [Host 到 Device 路径的瓶颈拆解](../../PCIE/wiki/05-performance-debug/host-device-bottleneck-breakdown.md) · 已修订 | 驱动提交、DMA 取数、交换/根端口、翻译/内存与回收是不同可测服务段。 | 光列出潜在原因无法判断低利用率来自上游供给还是往返时间。 | 待发队列常空优先查提交；读队列有工作且 Tag 长期满时测最终 Cpl RTT 与返回拥塞；同步采同一时窗吞吐与分段计数。 | “一个实用拆解顺序”补两组判别性观测及反例，区分端点输入饥饿与在途资源满。<br>**独立复核** 空发送队列、Tag 满及服务就绪反例能区分软件供给与 RTT/容量，不凭单一计数定因。 |

## 06 工作负载与案例

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [06 工作负载与案例](../../PCIE/wiki/06-workloads-case-studies/README.md) · 保留 | 案例入口列出 NIC、NVMe、加速器、采集卡、枚举、降速及片内边界。 | 读者可选择相符的工作负载或失效阶段。 | 只有在具体案例符合平台拓扑和软件队列假设时才复用其路径。 | 七个“推荐阅读顺序”已按设备与故障提供入口，保留。 |
| [枚举失败案例卡](../../PCIE/wiki/06-workloads-case-studies/enumeration-failure-case-card.md) · 已修订 | 发现、BAR 分配、MMIO 解码和 bus mastering 是逐级且可独立失败的状态。 | “系统看不见”与“BDF 可见但数据通路不可用”需要不同证据。 | 配置读可达但 BAR 无资源时 Function 仍可枚举；仅 bus master 禁用主要影响设备发起的内存事务。 | “典型现象”逐项标出配置读、桥窗口/BAR 和 Command 位对应的诊断分支。<br>**独立复核** 配置读、BAR/桥窗口/MSE、BME/映射三条故障分支有各自可观测结果。 |
| [FPGA / 采集卡控制面与数据面案例卡](../../PCIE/wiki/06-workloads-case-studies/fpga-control-data-plane-case-card.md) · 保留 | FPGA 案例按 BAR 寄存器控制和设备 DMA 搬运拆分 bring-up。 | 证明配置可达后，可以独立验证缓冲区、队列和数据传输。 | BAR 可访问但 DMA 映射错时控制面通过、数据面仍失败；完成记录可见性须独立核对。 | “最关键的两条路径”“最常见问题”与缓冲生命周期例已给出条件和后果，保留。 |
| [GPU / 加速器 Host Link 视角](../../PCIE/wiki/06-workloads-case-studies/gpu-accelerator-host-link.md) · 已修订 | GPU host link 承担提交和数据传入传出，copy engine、NoC 和 HBM 服务设备内访问。 | 要把工作量落到主机链路或设备内存资源，需知道数据是否已驻留、搬运和计算是否重叠。 | 输入驻留后多次重用会摊薄主机字节成本；每批主机往返且不能重叠时传输进入关键路径。 | “为什么它常常不是全局性能上限”补同一计算两种驻留/重叠情形，注明有效字节方向。<br>**独立复核** 主机搬一次后驻留与逐批往返无重叠两种条件在方向字节和关键路径上可区分。 |
| [链路降速案例卡](../../PCIE/wiki/06-workloads-case-studies/link-downgrade-case-card.md) · 保留 | 可用代际和 lane 数来自链路协商，限定单位时间可传量。 | 链路能力下滑与应用自身供给不足具有不同证据。 | 实测协商宽度/速率下降说明输送上界下降；小事务或内存慢时应用吞吐单独不能判定降档。 | “最短排查链”及“最常见误判”均给出反例与应查状态，保留。 |
| [NIC DMA 案例卡](../../PCIE/wiki/06-workloads-case-studies/nic-dma-case-card.md) · 已修订 | RX 环提供空缓冲区，NIC 将接收载荷写主机；TX 环发布待发送缓冲区，NIC 读主机后发送。 | 现在列出 RX/TX，却只解释了 DMA write，易把两个方向压成一类流量。 | 小包时每包描述符/CQE处理占比增加；中断合并减少中断频率但可能增加首次通知等待。 | “最关键的三条主线”各写一条 RX/TX 方向，并用 ring 空或合并门限说明可观察结果。<br>**独立复核** RX 向主机写，TX 从主机读，描述符耗尽及合并门限有可观察的丢包/中断结果。 |
| [NVMe 队列与数据路径案例卡](../../PCIE/wiki/06-workloads-case-studies/nvme-queue-data-path-case-card.md) · 已修订 | NVMe SQ 提交命令，控制器取 SQE；CQE 表示命令状态；存储读和写在 PCIe 数据方向相反。 | “DMA 读命令、写结果”不足以给出存储写的数据搬运路径。 | NVMe Read 常将介质数据以 DMA write 送主机；NVMe Write 常 DMA read 主机数据；两者均可写 CQE 并可选 MSI-X。 | 在“最关键的机制”加双向命令到 CQ 的例子，将存储命令、PCIe Completion 和 CQE 拆开。<br>**独立复核** NVMe Read 回主机采用 posted write，NVMe Write 取主机数据采用 MRd/CplD，CQE 单独写回。 |
| [PCIE vs AXI / NoC：边界与分工](../../PCIE/wiki/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md) · 已修订 | AXI 按通道/ID 搬移片内事务，NoC 提供共享路由，PCIe 在主设备边界定义请求与返回。 | 芯片内外串联时，跨桥重组决定上游完成怎么看。 | 支持此桥接的设备中，一个 PCIe BAR 读可变成下游 AXI 读，等待下游数据再组 CplD；竞争可在 NoC 或返回链路发生。 | 在“对体系结构最关键的判断”加入一例跨桥读，标出两个观察点与可选实现。<br>**独立复核** 跨桥读区分 host MRd→完整 Cpl 与片内 AR→R；桥接 AXI/NoC 仅为示例实现。 |

## 07 高级主题

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [07 高级主题](../../PCIE/wiki/07-advanced-topics/README.md) · 保留 | 高级索引分别指向设备虚拟化与翻译、P2P 约束和 CXL。 | 把可选平台特性放在基础数据路径之后。 | 平台启用的特性决定深读入口，目录不承诺使用其中任何能力。 | “推荐阅读顺序”只给三篇扩展入口，保留。 |
| [CXL 和 PCIE 的边界](../../PCIE/wiki/07-advanced-topics/cxl-and-pcie-boundary.md) · 已修订 | CXL.io 承担发现、配置和 I/O，CXL.cache 支持设备一致地访问/缓存主机内存，CXL.mem 支持主机访问设备内存。 | “更靠近内存语义”还不足以判定何时改变请求类型。 | 仅具有普通 PCIe 连接不能据此产生一致性流量；需主机、设备类型和协商模式支持相应协议，再依访问对象建模。 | 在“两者边界怎么抓”补三种协议方向与 Type 3 内存设备示例，避免把所有 CXL 设备都设为缓存主机内存。<br>**独立复核** CXL.io/cache/mem 的作用和主要发起方向明确，Type 3 的 io+mem 例不要求设备缓存主机内存。 |
| [Peer-to-Peer、Switch 与拓扑约束](../../PCIE/wiki/07-advanced-topics/p2p-switch-topology-constraints.md) · 已修订 | P2P DMA 将有效载荷送入对端暴露的可访问资源；路径可能本地交换或经受支持的上游路由。 | CPU 未主动复制也是主机内存普通 DMA 的特征，无法单独定义 P2P。 | 给出同交换机、允许直转的例子；ACS 重定向、桥支持或映射策略变化可能改路/阻止；主机缓冲中转需软件明确选择。 | 改“而不是每次都经 CPU 主动搬运”；明确对端 BAR、请求者、路由与不支持的结果。<br>**独立复核** 以请求者、对端 BAR、ACS 与平台路由定义 P2P；没有可达路径不意味着硬件自动用主机中转。 |
| [SR-IOV、ATS、PASID、PRI](../../PCIE/wiki/07-advanced-topics/sriov-ats-pasid-pri-overview.md) · 已修订 | PF 管理 VF；ATS 允许设备请求/缓存翻译，PASID 标识地址空间，PRI 让设备请求缺页服务。 | 这些机制解决共享 Function、翻译复用与可分页内存的不同问题，不是同时必选。 | VF 可独立存在；启用 ATS 时命中设备缓存可减少查询且须遵守失效；允许 PRI 时缺页可等待软件响应，拒绝不能假定成功。 | “各自大致在解决什么”逐项说明输入与结果，并加一次 PASID/缺页请求分支，具体组合取决于平台。<br>**独立复核** SR-IOV、ATS、PASID、PRI 各自输入输出清楚；缺页处理可失败，映射失效约束明确。 |

## 08 术语与检查清单

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [08 术语与检查清单](../../PCIE/wiki/08-reference/README.md) · 保留 | 参考索引区分术语、设计/调试检查、量化建模与复盘模板。 | 读者可直接取正确类型的工具。 | 需要量化上界时第 6 项给条件；故障证据归档用第 7 项。 | “推荐阅读顺序”已专门标出建模参数用途，保留。 |
| [术语表](../../PCIE/wiki/08-reference/glossary.md) · 已修订 | 词表给出包、地址、方向、协议界限和计量单位；AER、MSI-X 和 Completion 的职责仍需准确。 | 读者会用词条解释中断、完成匹配和错误报告，缩写不足以判断含义。 | non-posted 配置写可返回无数据 Cpl；MSI-X 向配置的目的地址发送消息，可关联完成服务；AER 可分级报告错误。 | “常见术语”把 Completion 写成 non-posted 返回且可含数据，扩充只有英文名的 AER；原有 GT/s、RCB、Tag 和 credit 条件保留。<br>**独立复核** Completion 对应 non-posted 请求，成功配置写 Cpl 无数据；AER、模式、Tag 和 RCB 限定齐全。 |
| [PCIE 高频问题](../../PCIE/wiki/08-reference/high-frequency-questions.md) · 已修订 | FAQ 用实际包长、MRRS/MPS/RCB、Tag 和 RTT 分开估算读写。 | 问题在“只要 credit 足够就能连续发”的充分条件判断。 | posted 写无需等待单次事务返回，但发包供给、路径仲裁、接收端服务与链路状态仍会限制连续发送。 | 在“为什么 write 常比 read 更容易跑满”限定为 posted Memory Write 并补上游供给与下游服务；保留例题。<br>**独立复核** BAR 是目标资源窗口，DMA 地址由请求设备用于访问映射资源；主机内存与受支持的对端 BAR 两种目的同时成立。 |
| [PCIE 调试检查清单](../../PCIE/wiki/08-reference/pcie-debug-checklist.md) · 保留 | 调试清单依次检查链路、可枚举性、映射、完成可见性与错误。 | 可将单一应用症状分到不同观察点。 | 配置可读后检查 BAR 和使能；中断失效时单独看 CQ 记录及轮询状态。 | “通知与完成”同时列 delivery、可见性和通知匹配，可用于取证，保留。 |
| [PCIE 故障复盘模板](../../PCIE/wiki/08-reference/pcie-debug-postmortem-template.md) · 保留 | 复盘模板记录现象/复现条件、影响、定位、证据、根因和处理。 | 保存真实故障上下文，便于重复验证。 | 特定平台、插槽、时间或 workload 会限定结论范围；需保存配置快照和统计。 | “关键证据”明确列出 link、AER、映射和队列统计，表单本身不提供硬件参数，保留。 |
| [PCIE 设计检查清单](../../PCIE/wiki/08-reference/pcie-design-checklist.md) · 保留 | 设计评审清单要求明确角色、资源、完成点、隔离和可观测性。 | 在实现前识别缺少的设备和平台契约。 | 多租户才需要相应隔离契约，轮询与中断策略按低延迟/CPU 开销目标选择。 | “中断与完成”“地址翻译与隔离”提出可验证的独立设计问题，保留。 |
| [PCIe 建模参数与公式速查](../../PCIE/wiki/08-reference/pcie-modeling-params.md) · 保留 | 量化页分别定义链路上界、真实 payload、Tag 并发、RCB 合法拆分、credit/缓冲与 Flit 开销。 | 把规范上限、平台容量和实验假设分开，能避免重复折扣。 | Non-Flit 的 24 B 仅为示例；Flit 打包、实际传输方向、目标能力和计数窗口改变结果；未知策略应做扫描。 | 有“25 个请求”、256 B 一包/四包、通告无限与实际接收缓冲、Gen6 TLP 区域上限及来源和校准步骤，保留。 |
| [PCIE 一页版总览](../../PCIE/wiki/08-reference/pcie-one-page.md) · 已修订 | 速览串起发现、MMIO、DMA、协议返回、CQ 与中断；链路吞吐和端到端吞吐取不同边界。 | 三组高频混淆在本页仅并排列词，读者难以自检。 | posted 写可用于写 CQE 而无相应事务级 Completion；轮询即可观察 CQE，即使没有 MSI-X。 | 在“最容易混淆的三组词”各加一句判据；对 BAR/DMA 写明发起方、对带宽写明计数字节和窗口。<br>**独立复核** CQ 容纳 CQE，命令状态存于条目；对端 BAR 可成为设备 DMA 的目标，映射及拓扑决定实际可达路径。 |
