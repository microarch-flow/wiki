# 系统网络专题补齐记录

日期：2026-11-17。实施前基线：`914ecb218c6b73a5733304a89f11ab39461d1049`。

## 范围与文章职责

按确认方案，将一篇导读补齐为七章、34 页：总导读、七篇章节导读、26 篇正文，另新增四张仓内 SVG。没有移动、删除或改写相邻专题正文。

基础章区分通信对象、主机 NIC 路径和帧预算；Ethernet/IP 章解释转发、多路径、排队与传输控制；RDMA 章解释资源、权限、操作和完成；RoCE 章解释封装、PFC、ECN/CNP/DCQCN 与配置；InfiniBand 章解释子网管理、SL/VL 和信用；系统集成章解释 GPUDirect RDMA、通信库选路和 UE 1.1；最后一章负责业务流量、预算、测试、诊断与资料。

PCIe/DMA 的事务、ring 与地址机制，NoC 的通用拓扑与前进条件，加速器专题的集体通信、并行流量和库执行语义，以及一致性、SerDes、CPO 的基础解释均通过链接复用。系统网络只保留理解当前路径所需的上下文。

## 技术依据与限制

主要来源为 IEEE、IBTA、IETF RFC、Linux/rdma-core、NVIDIA 官方文档、UCX、ESnet iperf3、perftest，以及 DCQCN 原论文。按操作与服务限定 RDMA 完成保证；区分普通 Write 与 Write with Immediate；不把内核旁路等同于没有 CPU 或操作系统参与；不把内存注册全部简化为预先固定物理页。

RoCE 的 PFC 与 ECN 控制范围分别说明，并保留官方 lossy/lossless 配置差异。GPUDirect RDMA 不等于 GPU 消费者已同步。UE 1.1 官方完整规范已下载并抽取文本，重点核对第 1.1.2、2、3.2、3.3 节的接口、子层、交付模式与 profile 范围；本次没有逐字段证明整个规范实现。1.1 的发布日期、Unified Local 和其他变化另与官方 release notes 对照。

33 个外部来源中，30 个在命令行 HTTP 检查返回 200。IEEE 的两页与 Microsoft Research 的论文入口返回 403；三页均通过联网检索工具打开并复核内容，保留官方引用，不把访问策略限制误报为不存在。可访问性检查不代替逐条事实审核。

所有性能数字都是教学算例；iperf3/perftest 命令未在真实 NIC/GPU 上执行。设备内部资源、PFC 阈值、重传和重排扩展、GPU 平台同步及互操作能力仍需具体版本和硬件验证。

## 路径与兼容

源码维持 `series/interconnect/NETWORK/`，公开前缀维持 `NETWORK/wiki/`。总标题改为“系统网络：节点之间怎样传输数据并确认完成？”，原标题锚点显式保留，原三个小节锚点继续存在，四个旧锚点在网页中各出现一次。

章节与编号目录一一对应，阅读列表同时控制文章顺序和短标题。网站只扩展该专题的短标题适配与导航测试，不改变来源映射，不增加第二份正文或重复 SUMMARY。

## 本地验证

- `python website/prepare.py` 与 `mkdocs build --strict` 通过；最终日志以提交前构建为准。
- 全站 68 项 unittest 通过，含新增专题的 34 页覆盖、章节阅读顺序、源码链接、图形、网页标题、搜索标题、导航当前项、面包屑及旧锚点检查。
- 34 页在 1280 × 900 桌面和 390 × 844 手机尺寸下共 68 组布局检查，无整页横向溢出、无缺失 H1、无图片加载失败。
- 人工查看桌面导读、手机四张图、完成表格及菜单当前项。手机协议比较表可以独立横向滚动，页面本身不横移。手机搜索 DCQCN 返回新文章。
- 独立复算：100 Gb/s、64 B 传统 MAC 帧为约 148.81 Mpps；1518 B 帧为约 8.13 Mpps；四路汇聚到一路的 10 μs 理想积压为 375 kB，排空需 30 μs；100 Gb/s × 1 μs 为 12.5 kB；1 GiB / 12.5 GB/s 约 85.90 ms；8 μs 在途窗口预算为 100 kB。
- 原有 18 个未跟踪文件按 SHA-256 基线验证内容不变。临时下载、脚本和验收日志不加入提交。

公开部署及线上验收结果以交付说明中的提交和 Actions 链接为准。

## 页面清单

- [01 基础概念](../../series/interconnect/NETWORK/01-foundations/README.md)
- [对象与分层](../../series/interconnect/NETWORK/01-foundations/objects-and-layers.md)：应用、端点、包与帧分别表示什么。
- [主机与 NIC 路径](../../series/interconnect/NETWORK/01-foundations/host-nic-data-path.md)：软件、设备、内存和网络怎样衔接。
- [帧、MTU 与包率](../../series/interconnect/NETWORK/01-foundations/frame-mtu-and-rate.md)：把额定速率换算成明确口径的预算。
- [02 Ethernet 与 IP 网络](../../series/interconnect/NETWORK/02-ethernet-and-ip/README.md)
- [转发与传输分工](../../series/interconnect/NETWORK/02-ethernet-and-ip/forwarding-and-transport.md)：Ethernet、IP、TCP 和 UDP 的职责。
- [Clos、ECMP 与多轨](../../series/interconnect/NETWORK/02-ethernet-and-ip/clos-ecmp-and-rails.md)：拓扑、流映射和共享出口的关系。
- [队列与 Incast](../../series/interconnect/NETWORK/02-ethernet-and-ip/queues-incast-and-tail-latency.md)：突发怎样产生排队与尾延迟。
- [重传与拥塞控制](../../series/interconnect/NETWORK/02-ethernet-and-ip/loss-recovery-and-ecn.md)：可靠性、接收流控和网络拥塞分别如何处理。
- [03 RDMA 端点](../../series/interconnect/NETWORK/03-rdma-endpoints/README.md)
- [QP、CQ 与连接](../../series/interconnect/NETWORK/03-rdma-endpoints/queues-and-connection.md)：请求进入设备前后有哪些状态。
- [注册与权限](../../series/interconnect/NETWORK/03-rdma-endpoints/memory-registration-and-permissions.md)：目标地址怎样成为合法访问对象。
- [操作与接收资源](../../series/interconnect/NETWORK/03-rdma-endpoints/send-read-write-and-atomics.md)：双方分别需要准备什么。
- [排序、完成与生命周期](../../series/interconnect/NETWORK/03-rdma-endpoints/completion-ordering-and-lifetime.md)：哪些事件允许消费或回收缓冲。
- [04 RoCE](../../series/interconnect/NETWORK/04-roce/README.md)
- [RoCEv2 封装与路径](../../series/interconnect/NETWORK/04-roce/rocev2-packet-and-path.md)：UDP/IP 与 RDMA 传输怎样配合。
- [PFC 与 Headroom](../../series/interconnect/NETWORK/04-roce/pfc-headroom-and-stalls.md)：接收空间、暂停传播和停顿风险。
- [ECN、CNP 与 DCQCN](../../series/interconnect/NETWORK/04-roce/ecn-cnp-and-dcqcn.md)：网络信号怎样改变源端速率。
- [部署条件与隔离](../../series/interconnect/NETWORK/04-roce/deployment-and-isolation.md)：地址、MTU、QoS、权限如何对齐。
- [05 InfiniBand](../../series/interconnect/NETWORK/05-infiniband/README.md)
- [子网、地址与 SM](../../series/interconnect/NETWORK/05-infiniband/subnets-addresses-and-sm.md)：拓扑发现、路径配置与分区的职责。
- [SL、VL 与信用](../../series/interconnect/NETWORK/05-infiniband/vl-credit-routing-and-congestion.md)：分类、仲裁、缓冲和前进条件。
- [IB、RoCE 与 iWARP](../../series/interconnect/NETWORK/05-infiniband/ib-roce-iwarp-comparison.md)：比较承载和运维条件，避免只比较峰值。
- [06 系统集成与新协议](../../series/interconnect/NETWORK/06-system-integration/README.md)
- [GPUDirect RDMA](../../series/interconnect/NETWORK/06-system-integration/gpudirect-rdma.md)：NIC 访问 GPU 内存后的同步责任。
- [通信库与 NIC 放置](../../series/interconnect/NETWORK/06-system-integration/libraries-and-nic-placement.md)：应用如何选择并占用真实网络。
- [Ultra Ethernet 与 UET](../../series/interconnect/NETWORK/06-system-integration/ultraethernet-uet.md)：版本、子层、profile 与实现边界。
- [07 性能、诊断与查阅](../../series/interconnect/NETWORK/07-performance-and-reference/README.md)
- [业务与流量](../../series/interconnect/NETWORK/07-performance-and-reference/workload-patterns.md)：RPC、存储和集群通信的不同需求。
- [指标与性能预算](../../series/interconnect/NETWORK/07-performance-and-reference/metrics-and-budget.md)：统一方向、单位、窗口和计时边界。
- [TCP 与 RDMA 测试](../../series/interconnect/NETWORK/07-performance-and-reference/benchmarking.md)：从最小路径测试扩展到应用。
- [诊断与恢复](../../series/interconnect/NETWORK/07-performance-and-reference/diagnosis-and-recovery.md)：用增量统计定位并处理失败状态。
- [术语、版本与资料](../../series/interconnect/NETWORK/07-performance-and-reference/glossary-and-sources.md)：核查来源、边界和未验证事项。
