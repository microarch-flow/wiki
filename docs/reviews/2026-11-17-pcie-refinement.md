# PCIe 专题打磨记录（2026-11-17）

本轮按用户确认保留八章与现有路径，修改原有 47 页，新增信用流控与链路重放文章，共 48 页。正文只修改 `series/interconnect/PCIE/`；网站改动限于 PCIe 短导航、维护说明与验证。历史评审保留，不以旧评审结论代替当前事实核查。

## 文章职责

下表中的章节首页负责阅读顺序与短导航名称。专题首页负责整体路径，知识地图负责完整索引。

| 页面 | 内容边界 |
| --- | --- |
| [01 概览与问题定义](../../series/interconnect/PCIE/01-overview/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [按目标学习 PCIe](../../series/interconnect/PCIE/01-overview/goal-oriented-navigation.md) | 按学习、驱动、性能和故障目标选入口，不重复正文机制。 |
| [学习路线图：从设备发现到性能解释](../../series/interconnect/PCIE/01-overview/learning-roadmap.md) | 给出依赖顺序和每阶段可验证的学习结果。 |
| [PCIe 在解决什么问题？](../../series/interconnect/PCIE/01-overview/problem-statement.md) | 说明设备发现、资源访问和异步数据搬运的系统问题。 |
| [PCIe 问题地图：角色、事务、地址与性能](../../series/interconnect/PCIE/01-overview/taxonomy.md) | 用角色、事务、地址、资源和观察点组织问题，不另造协议层。 |
| [02 链路、分层与事务基础](../../series/interconnect/PCIE/02-link-transaction-basics/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [信用流控与链路重放：为什么有数据也不能发送？](../../series/interconnect/PCIE/02-link-transaction-basics/credit-flow-control-and-replay.md) | 新增；解释逐跳信用记账、更新、ACK/NAK、重放及三种资源释放条件。 |
| [PCIe 三层架构：事务、逐跳可靠性与物理链路](../../series/interconnect/PCIE/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md) | 划分三层职责与 Non-Flit/Flit 边界，细节交给事务和流控文章。 |
| [Posted、Non-Posted 与排序：何时可以继续下一步？](../../series/interconnect/PCIE/02-link-transaction-basics/posted-nonposted-completion-ordering.md) | 解释请求类别、排序域及描述符/CQE 发布关系。 |
| [一次 PCIe 读取：TLP、链路确认与 Completion](../../series/interconnect/PCIE/02-link-transaction-basics/tlp-dllp-completion-basics.md) | 沿一次读取解释请求、Tag、分片 CplD 与不同层次的完成。 |
| [Root Complex、Switch、Endpoint：请求经过谁？](../../series/interconnect/PCIE/02-link-transaction-basics/topology-root-complex-switch-endpoint.md) | 区分组件角色与事务角色，解释共享上行链路。 |
| [03 配置、枚举与地址映射](../../series/interconnect/PCIE/03-configuration-enumeration-addressing/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [配置空间、BAR 与 Capability：设备公开哪些资源？](../../series/interconnect/PCIE/03-configuration-enumeration-addressing/config-space-bar-capability.md) | 解释 Function 配置空间、BAR 资源声明及 Capability。 |
| [枚举、总线号与资源分配：从发现到可运行](../../series/interconnect/PCIE/03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md) | 串联发现、总线范围、地址窗口和运行使能。 |
| [IOMMU：设备地址如何翻译并受到隔离？](../../series/interconnect/PCIE/03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md) | 解释设备身份、翻译、权限、缓存失效与故障。 |
| [配置、BAR 与 DMA：一次访问使用哪个地址？](../../series/interconnect/PCIE/03-configuration-enumeration-addressing/mmio-config-dma-address-view.md) | 对照配置访问、BAR 访问和 DMA 的地址空间。 |
| [04 数据路径、DMA 与中断](../../series/interconnect/PCIE/04-data-path-dma-interrupts/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [设备 DMA 的读写路径：谁请求，数据往哪里走？](../../series/interconnect/PCIE/04-data-path-dma-interrupts/device-dma-read-write-flow.md) | 解释设备读写的请求方、数据方向与包数算例。 |
| [主机缓冲区：生命周期、DMA 映射与可见性](../../series/interconnect/PCIE/04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md) | 维护缓冲区生命周期、DMA 映射和所有权交接的主解释。 |
| [PCIe 读取为何需要并发：完整返回时间与 Tag 窗口](../../series/interconnect/PCIE/04-data-path-dma-interrupts/pcie-read-completion-latency.md) | 维护完整 RTT、Little 定律与槽容量推导；区分测量和预测。 |
| [从提交队列到完成通知：Doorbell、CQE 与 MSI-X](../../series/interconnect/PCIE/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md) | 维护 SQ/CQ、Doorbell、CQE、MSI-X 与空间回收的通用流程。 |
| [05 性能与调试](../../series/interconnect/PCIE/05-performance-debug/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [AER 与链路计数器：错误在哪里被观察到？](../../series/interconnect/PCIE/05-performance-debug/aer-counters-link-debug.md) | 区分错误记录、报告路径与计数器观察点。 |
| [PCIe 性能参数：带宽、Credit、MPS 与 MRRS 限制什么？](../../series/interconnect/PCIE/05-performance-debug/bandwidth-latency-credit-mps-mrrs.md) | 解释参数约束和调优条件；提供 4 KiB 拆请求与 RCB 反例。 |
| [UR、CA 与 Timeout：有错误返回，还是没有等到返回？](../../series/interconnect/PCIE/05-performance-debug/common-failures-ur-ca-timeout.md) | 区分错误 Completion、Completion Timeout 和软件等待超时。 |
| [主机与设备数据路径：如何定位吞吐瓶颈？](../../series/interconnect/PCIE/05-performance-debug/host-device-bottleneck-breakdown.md) | 用路径证据和可反驳假设定位性能限制。 |
| [06 工作负载与案例](../../series/interconnect/PCIE/06-workloads-case-studies/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [设备不可用：区分发现、资源分配与 DMA 启动失败](../../series/interconnect/PCIE/06-workloads-case-studies/enumeration-failure-case-card.md) | 用三个构造案例区分发现、资源和 DMA 启动失败。 |
| [FPGA 采集卡：BAR 可访问，为什么 DMA 仍不工作？](../../series/interconnect/PCIE/06-workloads-case-studies/fpga-control-data-plane-case-card.md) | 解释 BAR 控制路径正常为何不能证明 DMA 路径正常。 |
| [GPU 主机链路何时成为瓶颈？](../../series/interconnect/PCIE/06-workloads-case-studies/gpu-accelerator-host-link.md) | 用明确假设的搬运/计算算例区分单任务延迟与流水吞吐。 |
| [链路降速或降宽：先核对能力、配置与实际状态](../../series/interconnect/PCIE/06-workloads-case-studies/link-downgrade-case-card.md) | 对照能力与实际链路状态，计算降速降宽后的带宽上界。 |
| [NIC 数据路径：RX、TX 分别占用哪个 PCIe 方向？](../../series/interconnect/PCIE/06-workloads-case-studies/nic-dma-case-card.md) | 按 RX/TX 分方向统计载荷、描述符和完成项。 |
| [NVMe over PCIe：从 SQ 提交到 CQ 回收](../../series/interconnect/PCIE/06-workloads-case-studies/nvme-queue-data-path-case-card.md) | 将通用队列机制应用于 NVMe；区分存储命令、PCIe 返回和持久性。 |
| [一次跨桥读取：PCIe、AXI 与 NoC 分别负责什么？](../../series/interconnect/PCIE/06-workloads-case-studies/pcie-vs-axi-noc-boundary.md) | 解释跨桥后的拆包、身份映射、顺序、错误和完成语义。 |
| [07 高级主题](../../series/interconnect/PCIE/07-advanced-topics/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [PCIe 与 CXL 的边界：I/O 事务之外增加了什么？](../../series/interconnect/PCIE/07-advanced-topics/cxl-and-pcie-boundary.md) | 给出 I/O 与一致性/内存协议边界，深入内容链接一致性专题。 |
| [PCIe P2P：对端资源、路由与隔离必须同时成立](../../series/interconnect/PCIE/07-advanced-topics/p2p-switch-topology-constraints.md) | 解释对端资源、转发路径、ACS、主桥支持与驱动协同。 |
| [SR-IOV 与地址空间扩展：PF/VF、ATS、PASID、PRI](../../series/interconnect/PCIE/07-advanced-topics/sriov-ats-pasid-pri-overview.md) | 区分 Function 虚拟化与地址空间扩展，列出 SVA 依赖。 |
| [08 查阅、建模与检查清单](../../series/interconnect/PCIE/08-reference/README.md) | 本章问题范围、前置知识、推荐阅读顺序与文章短标题。 |
| [PCIe 术语表](../../series/interconnect/PCIE/08-reference/glossary.md) | 提供短定义及常见混淆项，不重复教程。 |
| [PCIe 高频问题](../../series/interconnect/PCIE/08-reference/high-frequency-questions.md) | 给出短答案并指向唯一主要解释。 |
| [PCIe 调试检查清单](../../series/interconnect/PCIE/08-reference/pcie-debug-checklist.md) | 按排查阶段列出证据和下一步。 |
| [PCIe 故障复盘模板](../../series/interconnect/PCIE/08-reference/pcie-debug-postmortem-template.md) | 记录现象、假设、反证、修复与回归条件。 |
| [PCIe 设计检查清单](../../series/interconnect/PCIE/08-reference/pcie-design-checklist.md) | 按接口契约检查拓扑、映射、并发、通知和错误恢复。 |
| [PCIe 建模参数与公式速查](../../series/interconnect/PCIE/08-reference/pcie-modeling-params.md) | 集中维护代际速率、协议效率、Tag、分包和 Flit 的建模边界。 |
| [PCIe 一页总览：从配置到软件完成](../../series/interconnect/PCIE/08-reference/pcie-one-page.md) | 串联配置到软件完成的主路径，作为复习入口。 |
| [系统 I/O 互连：从发现设备到完成一次 DMA](../../series/interconnect/PCIE/README.md) | 专题入口、系统路径与跨专题阅读边界。 |
| [PCIe 知识地图](../../series/interconnect/PCIE/SUMMARY.md) | 维护全部文章索引，不成为第二套导航配置。 |

## 主要修正与去重

- 将逐跳接收信用、重放资源、Tag/请求槽及软件 CQE 分开解释；ACK 不等于信用返还或端到端事务完成。
- 区分完整返回 RTT、平均在途数、硬件槽容量与软件队列深度；保留必要条件，避免把窗口上界写成性能保证。
- 区分 MPS、MRRS、RCB 和 4 KiB 边界；区分原始速率、编码后容量、TLP 区域与有效载荷吞吐。
- 分开 CPU 地址、BAR/总线地址与 DMA 地址；补齐映射失败、生命周期、缓存同步和发布排序。
- 将缓冲区契约、队列流程、并发推导、参数表分别放在主要文章；案例、FAQ 与清单引用这些解释。
- 案例明确标注教学假设。补齐 NVMe CQ Head Doorbell；区分 CQE 与数据持久性。
- 信用、拓扑、P2P 使用三张结构图；信用图改为纵向布局，保证窄屏可读。

## 核查来源与结论边界

关键事实使用 PCI-SIG、NVM Express、Linux 官方文档与源码、AMD/Altera IP 文档及 Little 原始论文交叉核查。具体来源在正文的对应结论附近维护。

| 核查对象 | 主要依据 | 适用范围 |
| --- | --- | --- |
| 信用单位、完成缓冲、RCB | AMD PG054、PG213 | 传统模式及指定 IP；不把实现容量当协议常数 |
| 事务层与重放、4 KiB 边界 | Altera PCIe IP 文档 | 协议机制与具体实现的区别 |
| DMA、屏障、MSI、AER、SR-IOV、P2P、SVA | docs.kernel.org | Linux 接口；SVA 示例注明架构条件 |
| 配置寄存器 | Linux 主线 pci_regs.h | 配置布局，不代替设备手册 |
| SQ/CQ 事件链 | NVMe over PCIe Transport 1.4 §3.4、附录 A | 普通主机内存队列；命令与持久性另依 Base/NVM Command Set |
| Gen6 Flit、Gen7 原始速率 | PCI-SIG 官方说明 | 不推导未核实的 Gen7 载荷效率 |
| 平均在途数与吞吐 | Little (1961) | 统一统计对象及稳定负载 |

未做实机吞吐测量或协议一致性认证。NIC/GPU/FPGA 等构造案例不能作为特定产品实测数据。缩放信用、新模式 Tag 扩展及完整 Flit 重放状态机不在本轮教程范围；工程实现仍须按所用 Base Specification 与 IP 版本核对。

## 路径、导航与兼容

- 源码继续位于 `series/interconnect/PCIE/`，网站仍由既有映射发布到 `PCIE/wiki/`。不移动旧文件，不改变旧 URL。
- 保留原 47 页的 294 个历史标题锚点；变更标题以显式 `pcie-legacy-anchor` 兼容，保留未改标题的原 ID。
- 旧锚点位于 H1 前的页面增加 `title` 元数据，避免浏览器与搜索标题退回文件名。
- 各章编号阅读列表同时提供顺序和短标题。完整标题保留在正文、当前页的面包屑、辅助技术标签与悬停提示中。
- 原有未跟踪文件和目录不加入本次提交。

## 本地验收与发布门槛

执行网站维护文档中的暂存、MkDocs 构建和完整 unittest；额外测试覆盖全部 48 页的标题、搜索收录、当前导航、面包屑、阅读顺序、文章链接与旧锚点。

浏览器在 1440 × 1000 桌面和 390 × 844 手机视口检查标题、导航、表格、公式和三张 Mermaid 图，并通过搜索进入新增文章。该检查是浏览器响应式验收，不是物理手机实测。

构建中原有 COMPUTE 首页的 7 条相对目录链接提示属于范围外内容，本轮未改写。推送后须以 GitHub Pages workflow 成功和公开页面、搜索、旧路径/锚点检查作为最终发布依据；部署提交与 Actions 链接在交付回复记录。
