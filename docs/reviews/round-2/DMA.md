# 直接存储器访问逐篇评审

[返回九专题索引](README.md) · [DMA 专题入口](../../../series/microarchitecture/DMA/wiki/README.md)

## 专题入口

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [DMA Wiki](../../../series/microarchitecture/DMA/wiki/README.md) · 保留 | DMA全域dashboard与按学习/engine/软件系统目标分流导航 | 快速定位对象、同步、集成、建模与案例入口 | 适用边界：系统数据移动层主线，非单MCU或单Linux API教程 | 首页维护原则区分传输语义/实现/软件/系统瓶颈，导航链接覆盖新增参数/schema与案例。 |
| [知识地图](../../../series/microarchitecture/DMA/wiki/SUMMARY.md) · 保留 | 按01–09章组织DMA全部正文索引 | 使概念、微架构、编程、建模、案例和参考可回查 | 适用边界：目录导航，不定义额外协议/时间关系 | 各章逐页列表含性能模型四个新规格页，未出现独立事实或数值承诺。 |

## 01 概览与问题定义

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [01 概览与问题定义](../../../series/microarchitecture/DMA/wiki/01-overview/README.md) · 保留 | DMA概览以逻辑任务、执行节奏、系统耦合和软件可见完成分层 | 避免把所有问题压成DMA慢 | 适用边界：入门不定义具体IP，后续模型必须分提交/执行/可见性 | “建模提示”四层明确，入口给问题、分类和学习路径。 |
| [按目标学习 DMA](../../../series/microarchitecture/DMA/wiki/01-overview/goal-oriented-navigation.md) · 保留 | 按判断、bringup、AI、性能、研究、建模六目标裁剪路线 | 减少无关阅读但保留软件时序与可见性 | 性能问题涉及doorbell/completion→不能跳过软件语义 | “目标6”区分诊断与从零建模，“建模启示”按analysis_goal选状态，路径职责清晰。 |
| [学习路线图](../../../series/microarchitecture/DMA/wiki/01-overview/learning-roadmap.md) · 保留 | 按角色→对象→执行→系统/AI供数与建模逐层学习 | 字段/API需有系统语义支撑 | 目标从峰值估算变成hang/尾延迟→从transfer模型升级queue和system coupling | L1/L2/L3草图及三路线注明输入知识与新增状态，导航有边界。 |
| [DMA 在解决什么问题](../../../series/microarchitecture/DMA/wiki/01-overview/problem-statement.md) · 已修订 | DMA把CPU声明的数据移动任务转成独立事务执行流 | 降低逐数据搬运控制成本并支持与compute重叠 | CPU memcpy循环→消耗load/store、执行和cache资源，但不天然每cacheline进driver/中断 | “CPU为什么不能亲自搬”把CPU搬运描述为每次陷driver/写寄存器/等中断，混成single-shot DMA控制流程；分别写CPU复制成本、异步设备提交成本与DMA依赖，避免用错误因果支持动机。<br>**独立复核** CPU memcpy 以 load/store 占用算力/带宽；异步 DMA 另有 map、提交、通知和回收开销，依赖允许才重叠。 |
| [DMA 分类框架](../../../series/microarchitecture/DMA/wiki/01-overview/taxonomy.md) · 保留 | 按路径、控制模式、系统语义和并发组织分类DMA | 同名IP不代表相同completion、地址域与瓶颈 | 8channel共享2data path→接口并行不等实际带宽独立 | “工程分类问法”与DMAClass含completion/address-domain扩展，分清register/list/ring/queue和coherence。 |

## 02 基础对象与传输语义

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [02 基础对象与传输语义](../../../series/microarchitecture/DMA/wiki/02-fundamentals/README.md) · 保留 | 基础章定义logical transfer、descriptor、transaction、completion与可见性 | 数据搬完不等于软件可消费 | 适用边界：统一对象和系统语义，协议规则在后续专题展开 | “本章输出物”明确三层术语、cache/IOMMU与completion边界。 |
| [地址、描述符与 Burst](../../../series/microarchitecture/DMA/wiki/02-fundamentals/address-descriptor-burst.md) · 已修订 | descriptor描述任务，logical transfer经边界/粒度拆成互连子事务 | 批量化控制并组织合法高效burst | AXI4地址0x0FF0、32B、8B/beat→先16B到4KB边界再16B，增加AW/B或AR/R事务 | “边界规则”只有未完成的0x1003例；补完整源/目的拆分算法min(remaining,maxburst,src/dst boundary)、byte mask/尾部与事务数，区分AXI4 4KB、PCIe MPS/MRRS及IOMMU page并非同一约束。<br>**独立复核** 0x0FF0、32 B、8 B/beat 的源端两笔各 2 beat，目的可一笔 4 beat；对齐、字节掩码、协议边界与映射分开。 |
| [缓存一致性、IOMMU 与地址空间](../../../series/microarchitecture/DMA/wiki/02-fundamentals/consistency-cache-coherency.md) · 保留 | DMA地址翻译/权限与cache可见性/owner交接分别建模 | 旧数据与fault可能来自不同系统边界 | TO_DEVICE交出前发布CPU修改；FROM_DEVICE完成后CPU接管前同步旧副本 | “Noncoherent难点”不硬编码某平台recipe，明确IOVA/CPU地址不同、coherent仍要顺序及mapping生命周期。 |
| [Non-Coherent vs Coherent DMA](../../../series/microarchitecture/DMA/wiki/02-fundamentals/noncoherent-vs-coherent-dma.md) · 保留 | 硬件coherence与Linux coherent/streaming mapping是独立维度 | 在软件维护成本与硬件一致性成本间选择 | streaming FROM_DEVICE完成后sync_for_cpu再读；sync本身不等待DMA完成 | “Linux示例”含分配/映射失败检查、owner、方向、保留映射复用、unmap与cacheline共享边界，已有具体可执行契约。<br>**保留页抽查** 硬件 coherence 与 DMA API mapping 类型分开；descriptor 发布仍需顺序，streaming 收包先等设备完成再 sync_for_cpu，复用/解除映射和 cacheline 共享边界符合 Linux DMA API。 |
| [传输对象与基本语义](../../../series/microarchitecture/DMA/wiki/02-fundamentals/transfer-basics.md) · 已修订 | 任务分submit、accept、transfer done、consumer visible四阶段 | 统计延迟与buffer复用必须绑定具体完成事件 | completion回收限制可再发任务数→visible延迟会直接降低稳态吞吐 | 末段“只关心吞吐可折叠accept_ts/visible_ts”缺条件；限定提交/回收不是瓶颈且资源不依这些事件释放，给completion backlog压住queue反例，模型折叠须保等价服务约束。<br>**独立复核** 四个槽均等待 completion 的反例表明提交回收限制稳态；折叠时间戳须证明服务与容量等价。 |

## 03 DMA 引擎微架构

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [03 DMA 引擎微架构](../../../series/microarchitecture/DMA/wiki/03-dma-microarchitecture/README.md) · 保留 | 微架构章组织command、issue、response、completion及channel/stride能力 | 从任务语义推进到内部资源与调度 | 适用边界：结构入口，具体吞吐受OS/回包和系统约束 | “本章输出物”明示descriptor/issue/response/completion职责和不同能力主问题。 |
| [多通道、虚拟化与隔离](../../../series/microarchitecture/DMA/wiki/03-dma-microarchitecture/channels-virtualization.md) · 保留 | channel为调度单位、queue为提交容器、stream为逻辑流、context为权限地址上下文 | 性能配额与地址隔离必须分开 | 多queue共context→fault与mapping归属共享；多channel共data path→争吞吐 | 正文用8channel/2data-path反例及DMAChannel配额/priority字段，已说明接口分离不等资源隔离。 |
| [DMA 引擎的组成](../../../series/microarchitecture/DMA/wiki/03-dma-microarchitecture/engine-components.md) · 保留 | engine由命令解释、地址生成、读写事务、buffer与完成跟踪组成 | 并发/乱序/错误需显式关联和回收状态 | read response乱序→用inflight映射关联descriptor/subrequest，不能只左右搬数据 | “最小engine”和四个IP阅读问题给模块输入职责，DMAEngineState与命令/数据/完成三段一致。 |
| [多维 DMA 与 Stride 地址生成](../../../series/microarchitecture/DMA/wiki/03-dma-microarchitecture/multidimensional-stride-dma.md) · 已修订 | 多维DMA用active bytes/count/pitch生成规则行/面地址，再统一拆burst | 减少线性descriptor膨胀并改变事务组织 | src_pitch≠dst_pitch→第r行源s0+r·ps、目的d0+r·pd，各搬L byte | 正文只列一套base/stride，缺源目的独立pitch与完整地址示例；补2D伪代码/3行含padding例、零行/零长/负stride支持、算术溢出/区间重叠与边界拆分规则，不能称自动改善数据事务数。<br>**独立复核** 三行起点复算源 1000/1008/1010、目的 2000/2006/200C；独立 pitch、零长/负 stride、重叠与越界均定义。 |
| [调度、Outstanding 与回包组织](../../../series/microarchitecture/DMA/wiki/03-dma-microarchitecture/scheduling-outstanding.md) · 保留 | 调度控制发谁/发多快/何时节流，回包按协议和资源种类组织 | 隐藏latency同时避免return/consumer和completion积压 | AXI读逐R beat落位、末R释放读OS；PCIe posted写无事务Cpl→不能走通用响应链 | “request和response一起看”已给AXI4/PCIe偏序及独立资源释放反例，明确B不保证DRAM/CPU可见，符合协议边界。 |

## 04 软件栈与编程模型

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [04 软件栈与编程模型](../../../series/microarchitecture/DMA/wiki/04-programming-model/README.md) · 保留 | 软件章组织任务描述、提交、同步、消费与buffer复用契约 | 偶发错误常在字段发布/ownership/completion边界 | 适用边界：软件事件与可见性模型入口，非具体驱动API规范 | “本章输出物”明确descriptor可见、doorbell、completion和owner，阅读顺序覆盖同步与overlap。 |
| [队列、Doorbell 与 Completion](../../../series/microarchitecture/DMA/wiki/04-programming-model/queues-doorbells-completions.md) · 已修订 | queue批量提交、doorbell提示新任务、completion定义软件推进点 | 摊薄控制开销但增加槽位与可见性管理 | 环形prod==cons可能空或满→需phase/wrap或保留空槽；CQ写回与IRQ可同时使用 | 正文DMAQueue仅四索引无容量/回卷规则；补一轮小ring提交/consume/reclaim例，slot/数据buffer回收点分开。interrupt/polling是发现方式，completion record是状态表示，两者非互斥三选一。<br>**独立复核** 设备明确允许时可按消费确认提前回收 SQE，data buffer 等完成和所有权交还。轮询/中断均可批量消费 CQ，四槽保留一空的回卷成立。 |
| [软件栈与编程模型](../../../series/microarchitecture/DMA/wiki/04-programming-model/software-stack.md) · 保留 | 应用/runtime产生需求，driver准备队列，OS映射权限，engine执行 | 数据内容、设备地址与生命周期需同时正确 | completion回收率不足→即使data path快也会积压并限制新提交 | 软件前端字段submit_batch/doorbell_interval/mapping_ready/completion预算与模块职责对应，支持拆分软件/硬件瓶颈。 |
| [同步、一致性与常见错误](../../../series/microarchitecture/DMA/wiki/04-programming-model/synchronization-errors.md) · 保留 | 按descriptor发布、buffer owner、completion语义和槽位复用定位偶发错 | 单一done不足以证明数据可读或资源可复用 | descriptor半发布就doorbell→设备可能读半成品；done仅consumed→提前覆盖造成错误 | 四类错误与排查顺序明确，并链接Linux coherent/streaming具体流程；区分可见性与同步。 |
| [Tiling、Double Buffer 与 Overlap](../../../series/microarchitecture/DMA/wiki/04-programming-model/tiling-double-buffering.md) · 保留 | tiling定粒度，双buffer在资源独立时重叠DMA与compute | 用空间降低串行等待，不能消除主导瓶颈 | D=2,C=5,N=3独立两资源→总17cycle；单端口SRAM共享→max(D,C)假设失效 | 已有有限批次D+C+(N−1)max(D,C)、N=0、三块时间表与共享资源反例，首块延迟/稳态间隔/总时间分开。 |

## 05 系统集成

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [05 系统集成](../../../series/microarchitecture/DMA/wiki/05-system-integration/README.md) · 保留 | 系统章把DMA映射到NoC、memory、外设与AXI/PCIe边界 | 端点、互连与软件节奏共同约束行为 | 适用边界：跨域机制入口，协议合法性与具体profile另查 | “本章输出物”明确Resource/Topology/Interaction/Capability及横向协议链接。 |
| [AXI / PCIe 视角下的 DMA](../../../series/microarchitecture/DMA/wiki/05-system-integration/axi-pcie-view.md) · 已修订 | AXI DMA以AR/R及AW/W/B闭合，PCIe DMA以MRd/CplD与posted MWr运输 | 协议响应与软件completion必须分层 | PCIe MWr无对应事务Cpl；MRd被拆多个CplD→全部所需数据返回才释放read tag | 正文仅称posted/nonposted代价不同，需显式写无MWr Completion及DLL ACK非可见性；补AXI4 4KB/maxbeat与PCIe MPS/MRRS/tag/4KB的profile规则，避免“AXI写B=目的可消费”。<br>**独立复核** 普通 MWr 无事务 Cpl，Non-Flit 链路 ACK 不证明 CPU 可见；AXI4 INCR、PCIe MRRS/MPS/4KB/Tag 条件各自独立。 |
| [DMA 与 Local Memory / DDR / HBM](../../../series/microarchitecture/DMA/wiki/05-system-integration/dma-and-memory-system.md) · 保留 | DMA源供数、互连、目的消费和memory mapping共同定上限 | tile/burst/stride需与row locality和SRAM端口协同 | stride映射同bank不同row→PRE/ACT开销增加；refill与compute争单port→断供 | 正文区分local bank/port与外存return，要求研究shape时展开地址，未把连续地址直接等同row-hit。 |
| [DMA 与 NoC](../../../series/microarchitecture/DMA/wiki/05-system-integration/dma-and-noc.md) · 保留 | DMA把逻辑需求整形为burst/OS/priority驱动的request/response流 | 局部热点与ejection不能从拓扑名或平均带宽判断 | 多stream同相refill/writeback→端口峰值和credit回压增大 | “最该盯冲突”和DMANoCFlow保留路径共享点、return queue及stream priority，可定位网络/端点耦合。 |
| [SoC 外设与 I/O DMA](../../../series/microarchitecture/DMA/wiki/05-system-integration/soc-peripheral-io.md) · 已修订 | 外设DMA按FIFO/采样/帧节拍搬运并回报half/full-transfer状态 | 降低CPU逐数据介入并维持实时供收 | 不可回压外设以R生产且DMA最长停L→FIFO至少容纳R·L及现有积压，否则overrun | 正文提backpressure却未说明camera/audio等不可停源的丢数行为；补FIFO水位/服务时隙小例、overrun/underrun及循环half-transfer buffer ownership，明确平均生产率≤服务率还不够保证无丢失。<br>**独立复核** 4 B 初积压加 2 B/cycle×5 cycle 为 14 B；12 B 必超限，半区回卷前须交还，IRQ 不替代所有权。 |

## 06 性能建模与调优

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [06 性能建模与调优](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/README.md) · 保留 | 性能章连接指标、模型层次、参数/schema、校准和敏感度 | 从定性机制形成可解释实验与工具输入 | 适用边界：性能诊断与开发模型分两路线，数值需校准 | “本章输出物”明确submit/service/completion/consumer-ready采样，规格向路径指向统一事件定义。 |
| [校准与验证](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/calibration-validation.md) · 已修订 | 校准用观测拟合参数，留出数据验证趋势和外推范围 | 已知点拟合不能替代独立验证与可识别性检查 | OS高水位低可由注入不足导致→仅是已用容量下界，不能当max capacity | 反推表多错：计数差不是时间、busy不等冲突、subreq比−1可>1而非效率损失、端到端响应分布不能直接分解interconnect/DRAM。改用关联事件/控制实验/参数区间，分容量与水位。百分比标可选项目验收目标，非层次固有精度；尾部拟合须保留分布相关性。<br>**独立复核** 计数差、时间戳、容量/已用水位与事务增量均不互相代替；分段测量、可辨识性、分布相关和留出验证明确。 |
| [观测、计数器与调试路径](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/debug-observability.md) · 已修订 | 分阶段counter、histogram及快照关联提交、OS、返回、完成与错误 | 没有事件边界就无法区分发不满/回不来/软件未见 | 同ID复用或跨时钟trace→需task/subtxn序号及统一时间域才能相关 | “最值得计数器”只列名字，补submitted/accepted/completed事件、bytes按逻辑或线上计量、OS采样高水位/占用分布、buffer-full vs demand-stall、时间戳/溢出/快照一致性，避免把不可观测CPU可见时刻当硬件直接counter。<br>**独立复核** 发起/接收/完成的域与分母明确，水位是容量下界；跨时钟事件关联、回绕和 CPU 同步需对应软件证据。 |
| [指标、瓶颈与实验设计](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/metrics-bottlenecks.md) · 已修订 | 以不同事件边界统计提交、传输、完成可见、consumer-ready及吞吐 | 数据运输量与系统可继续时间不可互换 | timeout请求未完成→不能从P99样本删除；FIFO满但没请求→不等同有效stall | 已有完成域/偏序限定可保留；补effective bytes/测量时间、每指标起止事件与单位、offered/accepted/completed、warmup/drain及未完成数，counter分母固定。consumer-ready总延迟与completion后的准备增量采用不同名字。<br>**独立复核** 单槽可达低吞吐稳态，增槽效果须对照吞吐、窗口占用、完整 RTT 与 backlog；P99 同列未完成项，总时间与 completion 后增量清楚。 |
| [模型数据结构与事件规范](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/model-schema.md) · 保留 | DMAModel统一Knobs/Resources/State/Metrics/Observability与协议相关事件偏序 | 各页小结构是投影，不能拼成通用线性请求链 | AXI早R beat先落位、末R释放OS；posted MWr无事务Cpl；各resource独立release | “规范事件与偏序”明确观察域、未知时间、AXI AW/W解耦、B非CPU可见；时间分解有设备契约前提及目标化折叠条件，已有充分反例。 |
| [从抽象模型到系统诊断](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/modeling-method.md) · 保留 | 按理想容量、事务队列、系统耦合三层增加可解释状态 | 用能回答问题的最小模型避免黑盒或过细 | 读写共享半双工链路→复制1B消耗2B服务；单流对但多流错→加资源共享状态 | “第一层”已限定上界/共享需求/填排，升级触发对应queue/NoC/memory/consumer边界。 |
| [优化与调参手册](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/optimization-playbook.md) · 保留 | 先分问题和DMA画像，再按粒度、并发、冲突与调度/完成路径调参 | 减少盲扫并保持正确性与完成定义前提 | 偶发错→先同步/owner；return backlog→再发更多请求可能恶化尾延迟 | 正文给四类问题与五步顺序，并承认多流QoS有时为必要保护；旋钮结构可用于条件化实验。 |
| [参数与公式速查](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/parameter-reference.md) · 已修订 | 容量服务需求、BDP、事务效率、简化row miss与overlap公式用于一阶估算 | 把模型变量落到单位与适用边界 | B_target·RTT/S=6.25→平均窗口需求6.25、整数容量至少7但不保证满速 | Little段“足够点/超过只会排队”过强，补稳态同边界、RTT随负载变化、并行/请求大小约束。efficiency用地址/握手等效bytes仅限同瓶颈串行资源，AXI独立通道不能机械相加。burst≤256限定AXI4 INCR，ID数非OS上限；stride范围需字段能力，校准链接指向实际calibration页。<br>**独立复核** closed bank 需 ACT，open-row conflict 需 PRE 后 ACT；miss 增量按类加权。状态表示、通知、批次及合并独立；Little 算例容量至少 7。 |
| [旋钮敏感度与耦合](../../../series/microarchitecture/DMA/wiki/06-performance-modeling/sensitivity-coupling.md) · 已修订 | 用参数-指标影响假设及耦合簇组织设计空间探索 | 低维扫描可筛方向，但剪枝须有证明或实证 | 增加channel但共享OS/端口不变→吞吐不增且可因争用降；单流completion回收也可能限吞吐 | “data_width/num_channels单调”无普适性；矩阵箭头不能当定律或据—直接跳过sweep。删单流可跳供数/完成簇、完成路径与数据吞吐无关等断言；补频率/面积固定条件与反例，采用小范围验证/交互检查后才剪枝，BDP不推出唯一拐点。<br>**独立复核** 四槽、1 task/cycle 引擎和 1 task/10 cycle 软件回收，稳态受回收限制；不由单调矩阵或 BDP 直接剪枝。 |

## 07 工作负载与案例

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [07 工作负载与案例](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/README.md) · 保留 | 案例章比较不同平台路径、瓶颈和完成语义 | 同名DMA应映射具体资源/事务profile | 适用边界：系统画像入口，非某商业IP的实测规格 | “本章输出物”明确案例化边界，9类路径覆盖AXI/NIC/NVMe/GPU/local供数。 |
| [AI 加速器里的 DMA](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/ai-accelerator-dma.md) · 保留 | AI DMA协调HBM→cluster→tile及writeback的持续供数 | compute利用率依赖稳定refill与消费节奏 | refill/writeback共端口→每资源服务量须累加，不能只看单点峰值 | “建模启示”已按资源服务需求计重复占用、以各stage事件分析断供，职责和条件具体。 |
| [AI Local DMA 案例卡](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/ai-local-dma-case-card.md) · 已修订 | local DMA按片上计划执行staging/refill/writeback并同步compute | 靠近compute，ready/consume/release错误会立刻断供或覆盖 | A filling未达consumer-ready→compute不可读；A draining未release→DMA不可覆盖 | “核心机制/建模”仅给参数名，需补两buffer小案例、依赖token和单bank/单port冲突时序；明确DMA数据到SRAM、buffer ready、计算释放三事件，未必有软件CQ。<br>**独立复核** 同一单端口 bank、两 tile、两 beat 例中 3–4 拍 DMA 被算端阻挡；完整写、ready、release 顺序可查。 |
| [AXI DMA 案例卡](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/axi-dma-case-card.md) · 已修订 | AXI DMA把命令展开成读写burst并处理R/B与软件完成 | 在共享fabric上以合法粒度隐藏延迟 | 源0x0FF0复制32B、8B/beat且4KB限界→至少拆两AR，目的侧独立拆AW/W | 案例缺具体参数/事务流程；补小型搬运的AR/R→buffer→AW/W/B/错误回收，区分泛指AXI DMA与特定AXI-stream产品，寄存器模式也合法；completion可折叠须先证明不限制回收。<br>**独立复核** AR 分两笔跨 4KB、目的 AW 一笔 4W+B 计算成立；早 R 错仍收整 burst，已接受写须完整收尾。 |
| [CPU / GPU / NPU 系统中的 DMA 分工](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/cpu-gpu-npu-comparison.md) · 保留 | 按CPU/SoC软件I/O、GPU异步copy、NPU本地供数比较主关注点 | 完成边界与主资源不同，不能共享默认调优假设 | 同样OS/queue参数在host-I/O与local pipeline下→对应不同服务/可见性瓶颈 | 正文用“通常/更偏”限定画像，末段profile含dominant_path/completion_boundary，且承认CPU I/O也需steady-state。 |
| [嵌入式多媒体与存储/网络路径](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/embedded-storage-network.md) · 保留 | 多媒体偏deadline，存储/网络偏队列循环与completion稳态 | 平均字节吞吐不足以判断丢帧/欠采样或回收积压 | scanout错过窗口→花屏而非仅变慢；深队列但CQ回收不足→吞吐未必提升 | “建模启示”分deadline miss与completion backlog终态，三类系统差异和共性清楚。 |
| [GPU Copy Engine 案例卡](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/gpu-copy-engine-case-card.md) · 已修订 | copy engine是异步执行图中的传输资源，event约束kernel和buffer复用 | 分离搬运资源可与compute重叠但需依赖/能力允许 | 同stream H2D→kernel有依赖则串行；两tile流水用独立buffer/engine与事件才可能overlap | 正文只有“依赖允许”概述，无可检查例；补两stream/tile事件图与engine数量/方向、pageable staging或pinned路径条件，区分API异步返回、传输完成与实际overlap，设备内async copy不一律由copy engine执行。<br>**独立复核** H2D(B) 与 kernel(A) 只在 [3,6) 重叠，整批 13 时间单位；独立引擎、两 buffer、pinned/map 和真实依赖均有前提。 |
| [HBM 到 Tile 的数据供给链](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/hbm-to-tile-data-supply-chain.md) · 已修订 | 将runtime计划、HBM fetch、NoC、SRAM、tile-ready、compute与writeback连成流水 | 跨阶段节奏错配会放大反压和bubble | HBM读与writeback写共享同MC→稳态周期至少总读写服务需求，不等于各stage最大值 | 末段“峰值可折叠成最慢stage”需独立资源/不重复占用前提；补一个同资源服务量例及per-tile阶段偏序/buffer释放，避免stage枚举被误实现为全系统只能单stage状态。<br>**独立复核** 每 tile 经同一 MC 读写各 100 B，100 B/cycle 合计至少两拍；buffer ready/release 区分，全局各 tile 可重叠。 |
| [NVMe / 存储路径中的 DMA](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/nvme-storage-dma-case-card.md) · 已修订 | NVMe controller取SQ命令、按PRP/SGL搬数据并写CQE供host回收 | I/O并发需与介质、PCIe、软件完成共同匹配 | NVMe Read→设备以PCIe MWr写host；NVMe Write→设备以MRd/CplD读host；CQE也常为MWr | “核心机制”缺主机命令方向与PCIe事务方向的交叉例；补SQ fetch→payload→CQE→可选MSI-X与CQ head回收，区分介质完成/持久性条件。删NVMe天然大数据/比NIC少中断、必须深队列的泛化，4KiB低QD同样是有效场景。<br>**独立复核** NVMe SQE 和 descriptor 控制路径、Read 发 MWr/Write 发 MRd+CplD、CQE/CQ head、缓存持久化和 FUA/Flush 分开。 |
| [PCIe NIC DMA 案例卡](../../../series/microarchitecture/DMA/wiki/07-workloads-case-studies/pcie-nic-dma-case-card.md) · 已修订 | NIC RX把包写host，TX从host取包，ring/CQE与moderation组织稳态 | 包率、描述符和软件回收可能早于PCIe payload容量饱和 | TX DMA完成可允许host buffer复用，但不自动证明远端收到或网络可靠送达 | “延迟四段”需分别给RX/TX一条方向链，显式RX MWr/CQE/MSI-X与TX MRd/CplD/发送/CQE区别；moderation从首事件计时/阈值触发需定义，通知与CQE状态表示分开。<br>**独立复核** NIC RX 的 MWr、TX 的 MRd/CplD、MAC 和 CQE 是不同事件；TX buffer 可回收不代表远端收悉，首事件计时器/门限明确。 |

## 08 DMA IP 与产业视角

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [08 DMA IP 与产业视角](../../../series/microarchitecture/DMA/wiki/08-industry-ip/README.md) · 保留 | 产业章建立按系统匹配度评估IP的方法入口 | 峰值/feature需对照完成、接入和观测能力 | 适用边界：评审框架，未声称当前厂商产品规格或推荐排名 | 阅读顺序与输出物涵盖功能、微架构、系统接入及对照口径。 |
| [DMA 对照矩阵](../../../series/microarchitecture/DMA/wiki/08-industry-ip/dma-comparison-matrix.md) · 已修订 | 对照矩阵按系统位置、路径、约束和能力保留DMA类型差异 | 跨平台名称和feature不能简单排名 | NVMe数据路径是host buffer↔设备介质侧buffer/控制器，不是host↔storage queue | 表中NVMe“主要路径”把队列控制路径当payload路径；修正并加完成边界列区分CQE/协议Cpl/local-ready，匹配本页声明的“位置+路径+控制+完成语义”四元画像。<br>**独立复核** 六类实现均列位置、payload 路径、控制和完成边界，简表字段与正文一致；读在最后 R 握手、写在 B 握手完成，NVMe 另以 CQE 报命令状态。 |
| [DMA IP 评估清单](../../../series/microarchitecture/DMA/wiki/08-industry-ip/dma-ip-checklist.md) · 保留 | 按路径适配、功能、微架构、接入、软件及可诊断性评估IP | 支持列表不能证明深队列/错误/隔离下兑现能力 | 多租户场景→检查context fault containment及配额，不只channel数 | “系统接入层”和“软件/可观测性层”有具体问题，深入评审要求证据来源，框架可保留。 |
| [DMA IP 与厂商图谱](../../../series/microarchitecture/DMA/wiki/08-industry-ip/vendor-landscape.md) · 保留 | 按系统位置/主路径建立IP家族画像，再查厂商参数 | 避免脱离完成语义的峰值数字主导选型 | 同称多channel但资源未分离→不能直接比较吞吐/隔离 | 正文明确本页先分类而非产品清单，DMAIPClass保留control/visibility model，边界自洽。 |

## 09 参考资料与研究模板

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [09 参考资料与研究模板](../../../series/microarchitecture/DMA/wiki/09-reference-research/README.md) · 保留 | 参考章统一术语并提供研究/论文/IP模板与案例扩展入口 | 保留跨资料比较所需稳定字段 | 适用边界：研究工具导航，不新增IP/性能事实 | “本章输出物”明确完成语义、研究记录与案例回接，6个入口齐全。 |
| [案例索引](../../../series/microarchitecture/DMA/wiki/09-reference-research/case-index.md) · 保留 | 索引已有9类DMA系统案例并规定新增页四问题 | 扩展案例库时保持可比较路径和完成边界 | 新增chiplet/RDMA等案例→先写系统位置/完成/瓶颈/最小状态再接入 | “新增案例四件事”明确证据组织需求，建议未来案例未冒充现有能力或实现。 |
| [术语表](../../../series/microarchitecture/DMA/wiki/09-reference-research/glossary.md) · 已修订 | 统一DMA任务、协议事务、并发、可见性和完成术语 | 同名completion不先定域就无法比较延迟 | 设备可提前通知或不同commit域→completion_visible−transfer_done不必为非负等待 | completion visibility定义无条件“数据完成后”与model-schema条件偏序矛盾；改引用具体设备域与条件。transaction不等于每TLP（一个MRd可多CplD），burst是beat集合/地址规则而非“连续事务”。<br>**独立复核** 按特定设备契约判断可计算的完成域差值；PCIe 请求与多个返回 TLP、AXI burst 与 beats 均有正确定义。 |
| [IP 分析模板](../../../series/microarchitecture/DMA/wiki/09-reference-research/ip-analysis-template.md) · 已修订 | IP卡把定位、功能、微架构、系统接入及风险归档 | 集成决策需接口边界和可追溯能力证据 | 同产品不同版本/配置→OS、coherence和错误恢复可能不同，必须分记录 | 模板缺手册版本/URL/章节、配置与能力证据、未知/推测标记；补这些字段及验证场景/验收结果，避免feature勾选被当已验收实现。<br>**独立复核** 模板包含 IP/配置版本、章节与来源、测量/文档/推测/未知标签，具备能留空的独立验收证据位。 |
| [论文卡模板](../../../series/microarchitecture/DMA/wiki/09-reference-research/paper-card-template.md) · 已修订 | 论文卡记录问题、机制、指标、代价和未解决范围 | 结果数字只有对应baseline/负载/模型才可迁移 | 提升X%若baseline/输入/模型保真度不同→不能与另一论文直接横比 | “基本信息/关键指标”缺作者/出处链接、实验baseline/workload配置/模型层级/数据口径；补出处与页码、作者报告vs独立复现、误差/限制，保持机制记录结构。<br>**独立复核** 模板记录 DOI/作者、工作负载与 baseline、指标窗口/误差、作者报告和独立复现，能复查性能口径。 |
| [阅读问题清单](../../../series/microarchitecture/DMA/wiki/09-reference-research/reading-questions.md) · 保留 | 阅读清单从系统角色、路径、提交、并发、语义和瓶颈追问资料 | 先建立系统画像再解释feature和marketing数字 | 资料混写done→进阶问题要求拆完成阶段并找可观察事件 | 必读7问/进阶4问覆盖context、counter及可折叠状态，作为研究入口充分。 |
| [研究模板](../../../series/microarchitecture/DMA/wiki/09-reference-research/study-template.md) · 保留 | 统一记录研究对象、机制、指标、瓶颈判断与限制 | 跨论文/IP/性能问题复用同一语义框架 | 完成边界不同→必须单列后再比较latency/queue收益 | 模板含coherent/IOMMU假设、完成边界、为什么不是别处与最大风险，适用范围清楚。 |
