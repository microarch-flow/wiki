# 计算数据通路逐篇评审

[返回九专题索引](README.md) · [COMPUTE 专题入口](../../../series/microarchitecture/COMPUTE/wiki/README.md)

## 专题入口

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [COMPUTE 域 Wiki:AI 算力单元为何长成这样](../../../series/microarchitecture/COMPUTE/wiki/README.md) · 已修订 | COMPUTE 入口按 datapath、阵列、时序、实现、片上组织和建模列出章节。 | 让读者从指定边界的有用工作和搬运量理解架构取舍。 | 固定 MAC 与外部字节，仅改变流水深度会改变 f、II、延迟及能耗，MAC/B 不变；GPU 的可编程 SM 和矩阵引擎需分别估计。 | 地图“GPU=平铺TPU”“全域…六个层级…计算/通信比”与已改的纲领页有冲突；改为 GPU/TPU 中局部矩阵结构可比，时钟与制造用各自指标。<br>**独立复核** 地图按边界定义 MAC/B，把时钟的路径/II、可配置性和芯片组织分别建模；读者能定位权重复用和局部 GPU/TPU 矩阵单元。 |

## 01 · 总览：计算资源与数据供应

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [01 · 总览：计算资源与数据供应](../../../series/microarchitecture/COMPUTE/wiki/01-overview/README.md) · 保留 | 第 01 章导航将问题定义、边界指标和阅读顺序分开。 | 在后续讨论阵列或面积前先固定单位与工作量。 | 若要比较复用跳到 MAC/byte，比较电路实现则跳到门数/面积；页面不承担参数模型。 | 三项入口各有用途说明，末句明确固定工作量、边界和单位。 |
| [计算、数据移动与硬件成本：先确定指标边界](../../../series/microarchitecture/COMPUTE/wiki/01-overview/compute-communication-ratio.md) · 保留 | 算术强度是给定工作量的有效 MAC 数除以该统计边界实际字节，另列面积、带宽与能量。 | 避免将同一字节跨多个边界重复充为片外流量，或从 MAC/B 推断绝对性能。 | 相同 6 MAC，热权重 3+8 B→6/11 MAC/B，首次加装权重 6 B→6/17；频率/争用另行求吞吐。 | “算术强度”手算和“面积、带宽、吞吐与能耗”表给出单位、包含项与 N_useful>0 的能量边界。 |
| [算力单元需要同时满足计算和供数](../../../series/microarchitecture/COMPUTE/wiki/01-overview/problem-statement.md) · 保留 | 算力单元接收操作数与控制，算术结果依赖数据供应、选择和结果写回。 | 门数代理说明选择逻辑量级，不能直接校准真实面积或性能。 | 三组 8:1、p 位网络与 p×4 核在假设代理下为 24p 与 4p；实际 RF 端口冲突会延迟接纳，需事件调度。 | “一个选择网络的简化代理”明确缺省部件、工艺与时序条件；“用相同边界”明确冷/热流量。 |
| [学习路线与域边界:原语 → 阵列 → 流水 → 布局](../../../series/microarchitecture/COMPUTE/wiki/01-overview/taxonomy-and-roadmap.md) · 已修订 | 从门、MAC、阵列、流水、存储和顶层组织建立跨域阅读路径与职责边界。 | 正确选择参数所有者，避免把时间、面积、功耗均塞进搬运分母。 | 在架构与流量都不变时提高 f 或改变库不会改变 MAC/B；跨域接口分别传带宽、延迟、路由、能量或 PPA 参数。 | “每上一层…搬运吃掉面积”“GPU=平铺 TPU”“每层抬高比值”“array 边界 x 量级带宽”应按边界与时刻重写，独立说明工艺/时序目标，移除通用等号及未定义 x。<br>**独立复核** 固定工作量和跨边界字节，换流水深度或工艺库不改变 MAC/B；阵列按方向/时刻提出字节需求，NoC 按资源和仲裁服务。 |

## 02 · Datapath 基础

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [02 · Datapath 基础](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/README.md) · 保留 | 列出乘加、进位归约、位宽、数值格式和操作数选路五篇的责任边界。 | 让门数、综合面积和运行时数据分母各有对应入口。 | 若改变编码，先查存储/转换；改变压缩树则查组合路径与综合，无须在导航页增设参数。 | 起首明确区分三种量，五个链接逐一标明主题和下一章。 |
| [压缩树与进位结构：从多行部分积到结果](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/dadda-and-adder-trees.md) · 已修订 | 3:2 compressor 把同权位转为本位和与高一列进位；Dadda 预定列高，Wallace 尽早压缩，最终两行交 CPA。 | 推迟横向进位，分别控制压缩层深、加法器数量和布线。 | Dadda 目标从 2 起，向上取 floor(1.5d) 得 2、3、4、6…；最大列高 5 时按 4→3→2 压。固定流量改树只影响面积/延迟等实现指标。 | “使用阶段目标高度安排压缩”未说明目标如何构成和何时需要压缩；给一组列高/阶段例，并说明当前列加入前列转移进位后再满足高度。<br>**独立复核** Dadda 目标 2、3、4、6 反向使用，最大列高5时依次压到4、3、2；本列5位加低列来1位，经1个 FA 留4位、向上列送1进位，权值守恒。 |
| [从部分积到 MAC：整数范围、归约与累加](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/multiply-accumulate-from-gates.md) · 保留 | MAC 将乘积加入既有累加状态，位权排列的部分积可用 carry-save 树归约后进位。 | 用明确整数范围和舍入/溢出语义保证数值模型与硬件一致。 | 两项 15×15 和为 450，无符号 8 位溢出，9 位能精确保存；回绕/饱和/不同累加初值生成不同结果。 | “累加位宽与数值语义”和 full adder 恒等式同时给范围、构造及实现独立的时序边界。 |
| [mux 与数据移动：选择网络的实现成本](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/mux-and-data-movement-cost.md) · 保留 | n:1、p 位选择网络从多个来源取一组操作数，RF 的实际读口可有多种实现。 | 把选择门、布线/面积与运行时 RF 访问和外部搬运成本分开。 | 增加源数或并行端口可能扩大选路；拆 bank 可降低单组扇入，但同 bank 争用会增加等待。 | “两个门数代理”限定 24p/4p 的假设，“面积代理与流量”区分代理比、MAC/B 与端口事件。 |
| [AI 数字格式：位字段、块缩放与存储成本](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/number-formats-for-ai.md) · 已修订 | 数值格式以符号、指数、显式尾数或整数码表达元素，MX 另为一组元素记录共享 scale。 | 在相同 nominal bit 下分别算表示误差、块字节与原生硬件执行能力。 | 同为 8 bit，E4M3/E5M2 的范围、ULP 和特殊值不同；32 元素 MXFP4 无填充为 17 B，裸 FP4 为 16 B；纯整数运算无需量化参数。 | 首节“INT 使用整数码与量化参数”混淆整数类型与量化映射；限定 scale/zero-point 属仿射量化，纯整数按补码/无符号解释；保留现有详尽 FP 与 MX 例。<br>**独立复核** 整数编码同仿射量化的 scale/zero-point 分开；OCP MX v1.0 下 32×4+8=136 bit=17 B，E4M3/E5M2 的最大有限值及 Inf/NaN 均与表2一致。 |
| [乘法位宽、实现面积与有效吞吐](../../../series/microarchitecture/COMPUTE/wiki/02-datapath-foundations/quadratic-bitwidth-scaling.md) · 保留 | p×q 是生成全部无符号部分积时的结构规模，浮点、累加和实际门库另算。 | 解释为什么两输入同时减半会缩减乘法核心，却不能推出整芯片速度比例。 | p 和 q 一起减半则此类部分积为 1/4，只降一侧为 1/2；供数、指数、累加器或固定资源限制可使吞吐不变。 | “整数乘法器的结构估计”“浮点和累加的边界”及 Strassen 段按实现、算法、误差约束限定结论。 |

## 03 · Systolic Array：局部复用与数据流

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [03 · Systolic Array：局部复用与数据流](../../../series/microarchitecture/COMPUTE/wiki/03-systolic-array/README.md) · 保留 | 导航局部 PE 复用、stationary 映射、顶端载权及阵列尺寸。 | 在研究吞吐前区分运行时流量、硬件资源与时序边界。 | 需要估冷启动转载权时序，需要比较 PE 空置转 sizing；导航标明 x 宽、y 拍为指定接口。 | 四个链接逐项说明复用、带宽、局部存储和尺寸问题，适于作章节入口。 |
| [阵列 sizing：容量、供数与利用率](../../../series/microarchitecture/COMPUTE/wiki/03-systolic-array/array-sizing-tradeoff.md) · 保留 | 给定张量、精度、预算与数据流，选择 PE 阵列行列数及供数资源。 | 更大峰值阵列可能增加填充损失、端口和时序代价。 | RF 面积固定且供数够时从 64² 到 128² 的 RF 面积/PE 变 1/4；32² 工作映射在 128² 的空间填充仅 1/16。 | “固定 RF 假设”“利用率与边界带宽”提供两个独立手算，明确多任务和真实供数会改变收益。 |
| [Dataflow：权重、部分和与输入如何复用](../../../series/microarchitecture/COMPUTE/wiki/03-systolic-array/dataflow-taxonomy.md) · 已修订 | stationary 规定指定层与时间窗口内权重、输入或部分和的复用/归约位置。 | 驻留减少该层重复搬运，但仍要计算首次装载、换块及输出。 | 若阵列是片上 PE，在 PE 存权时权重已在片上；片外读取是否发生取决于首次供应或逐出重装，是否跨请求复用另由驻留区间决定。 | WS 段“权重驻留在阵列不意味着它已驻留在片上”自相矛盾；区分当前 PE 驻留、上层另有副本和上一次运行之前是否已装入。<br>**独立复核** 片上 PE 已驻留的权重在当时已在片上；本次是否从外存装入取决于起始状态、驱逐和上层副本，和跨请求复用分别记录。 |
| [权重载入与 trickle-feed：宽度、周期和重叠](../../../series/microarchitecture/COMPUTE/wiki/03-systolic-array/weight-loading-and-trickle-feed.md) · 保留 | 顶端 x 路权重每边沿与内部各行同步移位，y 行装满需 y 拍，目标 bank 决定能否覆盖。 | 用窄入口装满阵列，同时避免把一次内部移位和稳态重叠重复收费。 | 2×3 示例 3 拍满；3 拍装/6 拍算的两 tile 在单 bank 18 拍，资源独立且双 bank 时 15 拍。 | “机制与接口”给逐拍占位，“首块、换 tile 与覆盖条件”给冷启动和竞争反例。 |
| [Systolic array：用局部传递和复用组织计算](../../../series/microarchitecture/COMPUTE/wiki/03-systolic-array/why-systolic-array.md) · 已修订 | 邻接 PE 按方向传递激活/部分和，独立 MAC 使用本地可复用的数据。 | 把穿越阵列的有用字节与 PE 内通信、算术峰值和实际时间区分。 | 同一向量完成六次 MAC，冷装权重改 6/11→6/17 MAC/B；纯 backpressure 仅延长完成时间，未引发重传/额外跨界读写时字节与强度不变。 | 在算术强度例后说“同步及 stalls 都会改变结果”易把时间损失扣到 MAC/B；逐项区分字节、窗口和吞吐。<br>**独立复核** 3×2 阵列一次有6 MAC，暖窗 3+8=11 B，冷窗加6 B；单纯停顿只改完成时间与 MAC/s，发生重传才增加分母字节。 |

## 04 · 时钟与流水

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [04 · 时钟与流水](../../../series/microarchitecture/COMPUTE/wiki/04-clocking-and-pipeline/README.md) · 保留 | 索引时钟边沿、setup/hold、前馈流水、反馈依赖与吞吐。 | 让不同的时间单位和约束选到正确的细节页。 | 本域所有有效 setup 约束决定可用周期，hold 独查；跨域协议引入不同数据可见和同步事件。 | 四条索引和末段给出路径约束、II 与延迟的各自用途。 |
| [反馈环的时钟约束：依赖、频率与启动间隔](../../../series/microarchitecture/COMPUTE/wiki/04-clocking-and-pipeline/feedback-loop-clock-constraint.md) · 已修订 | 反馈循环从旧状态生成新状态；结果返回时刻和迭代距离限制单链启动间隔。 | 在不破坏累加次序及溢出/舍入语义的条件下提高总体接纳率。 | 两条本来独立序列可交错发射且无需互相合并；把一项归约拆成两部分累加才需末端合并，并检查浮点或饱和对重排的影响。 | “两个独立累加状态…并需额外合并”混淆两个独立任务与同一任务的两个部分和，补两种输出语义和资源前提。<br>**独立复核** 反馈2拍时单链 II≥2；两个独立任务可交错且各自输出，同一归约拆两链需合并并检查浮点舍入/饱和顺序。1.4 ns 的域内最慢路径给约714 MHz。 |
| [频率、延迟与吞吐：分别定义再比较](../../../series/microarchitecture/COMPUTE/wiki/04-clocking-and-pipeline/frequency-is-not-throughput.md) · 保留 | 频率为周期/秒，吞吐为有效工作/秒，单任务延迟由输入到完成。 | 将硬件可运行的频率与给定映射的有效工作量分开。 | 有效 MAC/拍 w 在流水排空或带宽争用下变小，即使 f 上升，w·f 也可能持平或下降；batch 还改变队列时延。 | “频率与有效工作量”和“Batch 与工作点”给出 w、f、A 的度量及必要假设。 |
| [时钟同步：采样边沿与时序约束](../../../series/microarchitecture/COMPUTE/wiki/04-clocking-and-pipeline/global-clock-synchronization.md) · 保留 | 同步寄存器的 launch/capture 边沿与数据最大/最小传播时间分别约束 setup、hold。 | 检查各时钟域所有有效路径，在 PVT/时钟条件内选可验证频率。 | 以捕获晚到为正 skew，放宽 setup 同时收紧 hold；1/1.4 ns≈714 MHz，对短路径的 hold 失败降频不能自动修复。 | 两条简式、符号约定、异步跨域与例外条款均完整，已有逐域反例和证据限制。<br>**保留页抽查** 以 capture−launch 为 skew 时，setup 减 skew、hold 加 skew 的符号一致；hold 不由降频解决。1.4 ns 对应约 714 MHz，且同沿/同域/单周期、PVT 与 CDC 例外明确。 |
| [Pipeline register 插入：路径、延迟与吞吐的权衡](../../../series/microarchitecture/COMPUTE/wiki/04-clocking-and-pipeline/pipeline-register-insertion.md) · 保留 | 寄存器把前馈组合路径分成多级，改变事务经过的边沿数与阶段约束。 | 提高可能的工作频率并保持吞吐，付出时钟/面积和控制延迟对齐成本。 | 2 ns→max(1.2,1.3) ns 的例中，若各级均可每拍接纳则 II 保持 1；协议、valid 或反压不允许时不能由寄存器数推断 II。 | “一次前馈切分”“前提与代价”分别给具体周期、级数、协议和保留的事务属性。 |

## 05 · FPGA vs ASIC：可配置性的实现代价

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [05 · FPGA vs ASIC：可配置性的实现代价](../../../series/microarchitecture/COMPUTE/wiki/05-fpga-vs-asic/README.md) · 保留 | FPGA/ASIC 导航界定可配置逻辑、互连、硬块与固定逻辑的对比。 | 避免将历史面积比较用作所有现代设计的价格或功耗倍率。 | 更改目标工艺、DSP/存储器映射或工作负载时，需要重新取得面积、关键路径和活动能耗数据。 | 正文明确同一逻辑映射及 90 nm 历史 benchmark 的适用条件。 |
| [FPGA vs ASIC：可配置性、LUT 与实现开销](../../../series/microarchitecture/COMPUTE/wiki/05-fpga-vs-asic/lut-mux-and-10x-overhead.md) · 保留 | LUT4 用 16 位真值表实现四输入函数，可配置互连另付成本，专用硬块改变映射。 | 评估可更新性与面积、速度、动态功耗及 NRE 的实际取舍。 | 乘法映到 DSP 或容量映到硬块会缩小选定 90 nm 样本的差距；LUT 数、功率比都不能直接给 J/task。 | 四输入 AND 的真值表示与 Kuon/Rose 论文对照均限定实现、工作点和指标量纲，足以指导重测。 |

## 06 · 存储 discipline：cache 与 scratchpad

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [06 · 存储 discipline：cache 与 scratchpad](../../../series/storage/reading-and-reference/01-reading/cache-scratchpad-introduction.md) · 保留 | 导航软件显式放置与 cache 自动放置，区分位置确定和服务时间确定。 | 选择需要记录初态、替换策略还是需要记录 DMA、端口和仲裁。 | SPM 同 bank 可排队，已定初态和访问规则的 cache 可重复模拟；题目自带可追溯链接。 | 短文已对两边分别给一个可改变服务时间或命中行为的条件。 |
| [Cache 与 scratchpad：数据放置和访问时间](../../../series/storage/01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md) · 保留 | cache 靠 tag/替换/填充自动管理，scratchpad 依靠软件约定的地址与生命周期。 | 两类存储各自还有共享端口、服务延迟与仲裁，需明确可见完成时间。 | 同 bank 单读口，周期 0 两个已知地址同时请求，先发者周期 1 完、后者周期 2 完；改 bank 或优先级影响结果。 | “同时访问的反例”给到达、接纳、完成，cache 亦明确确定性模拟所需初态和资源。 |

## 07 · 芯片顶层组织

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [07 · 芯片顶层组织](../../../series/microarchitecture/COMPUTE/wiki/07-chip-organization/README.md) · 保留 | 总览 CPU/GPU 资源、动态功率与 GPU/TPU 顶层互连三个问题。 | 防止从选择网络的抽象门数跨层推断完整商用芯片性能或面积。 | 不同器件、数据映射、局部资源与跨阵列通信边界要求分别建模；链接明确每页处理哪一项。 | 三条导航描述与末段关于器件/边界的范围约束清楚。 |
| [频率、动态功耗与每任务能量](../../../series/microarchitecture/COMPUTE/wiki/07-chip-organization/brain-vs-chip-power.md) · 保留 | 功率是单位时间能量，任务能量是功率对执行时间的积分，CMOS 动态项受活动率、电容、电压和频率控制。 | 审查降频、不同计算系统或不同负载的能量结论所需条件。 | 固定 V 和任务总跃迁，降频使耗时翻倍时动态功率约减半、动态能量近恒定；固定漏电功率对应的能量翻倍。 | “固定电压下的降频例子”区分 W、J/task 和 DVFS 等边界，未对生物和芯片给无依据等价。 |
| [CPU 与 GPU 的资源组织：控制、并行与存储](../../../series/microarchitecture/COMPUTE/wiki/07-chip-organization/cpu-vs-gpu-core-area.md) · 已修订 | CPU core 与 GPU SM 的控制、线程状态、算术和存储共享粒度不同。 | 解释为什么面对单线程控制流、并行与访存等待时，两者需要不同资源。 | CPU 误预测引发清空/重取；NVIDIA SIMT warp 分歧会产生掩码及不同路径发射；可就绪的其他 warp 可隐藏部分等待，驻留受寄存器/共享内存约束。 | 正文主要展开“分支预测”，GPU 只说有调度和控制；补一个限定 GPU 架构的 warp/驻留情形并指明可观测的有效 lane、等待、吞吐，勿猜面积比例。<br>**独立复核** 以 A100 SM 和32线程 warp 为界，分支活动掩码决定有效 lane，其他 ready warp 可隐藏等待；面积份额与分歧开销未给伪精确值。 |
| [GPU 与 TPU 的顶层组织：局部资源和跨单元通信](../../../series/microarchitecture/COMPUTE/wiki/07-chip-organization/gpu-as-tiled-tpu.md) · 已修订 | 不同架构将矩阵引擎、向量通路、调度和存储放在不同层级，可切分阵列提供受约束的多组执行模式。 | 用具体分工区分 SM 的可编程并行控制与 TPU MXU 的矩阵数据流，解释跨单元的流量。 | 规整 GEMM 可用矩阵单元；小块或多任务能否切分看支持模式、局部资源和输出归约，非矩阵操作要走独立向量/通用路径。 | 整篇“计算阵列…按不同粒度分组”只给泛化表，未交代 GPU/TPU 各一个实物组织；用 CUDA SM + 代际限定的矩阵引擎、Jouppi TPU v1 matrix unit + accumulator 说明为何不能互相平铺。<br>**独立复核** A100 SM 含通用通路和 Tensor Core；一代 TPU 的256×256 8-bit MXU 配 accumulator/统一缓冲/激活单元，两者局部矩阵功能可比，整芯片组织有各自明示边界。 |

## 08 · 面向 archax 的建模建议

| 页面与处理 | 概念或用途 | 设计动机 | 触发条件与可观察结果 | 原文诊断与修订后复核 |
|---|---|---|---|---|
| [08 · 面向 archax 的建模建议](../../../series/microarchitecture/COMPUTE/wiki/08-modeling-for-archax/README.md) · 保留 | 本章给 archax 读者提供带边界的建模建议和指标入口。 | 防止把建议的事件或资源字段误当指定工具版本已实现。 | 若需声明已支持某字段，必须核对目标版本；这些文章可先用于设计参数与观察量。 | 入口明确“各项是建议”，并链接独立的指标定义与具体模型页。 |
| [面向 archax 的建模建议：边界、事件与资源](../../../series/microarchitecture/COMPUTE/wiki/08-modeling-for-archax/modeling-insights.md) · 保留 | 用七组建模建议把计算、边界字节、编码、阵列/RF、权重加载、调度和时钟联系起来。 | 将可比较的事件、单位、数值编码和资源约束交给架构探索。 | 零流量不定义 MAC/B，MXFP4 满块 17 B；单口仲裁改变完成拍，载重可否隐藏由双 bank 与带宽控制，所有 setup 路径决定域周期。 | 每组都给前提与可复算观测，清楚限定为建议；用单端口及 714 MHz 例覆盖两种不同时间边界。 |
