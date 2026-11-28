# 从硅到系统

这份笔记记录从模型到芯片的工程问题。[首页序章《第一个字出现之前》](https://microarch-flow.github.io/wiki/)讲述这些笔记的来由。想从器件开始，可先读[半导体与电路基础](./series/semiconductor-foundations/README.md)，从硅原子间的共价键读到门电路与时钟边沿。

网站版的本地预览、内容维护与 GitHub Pages 发布方法见[网站构建与维护](./website/README.md)。

整理 Wiki 和博客时的写作、技术核查、导航与视觉要求见 [Wiki 与博客设计规则](./docs/wiki-blog-design-rules.md)。这些规则可以根据后续需求调整。

## 系列源码入口

### 硬件怎样工作？

| 系列 | 内容 |
| --- | --- |
| [半导体与电路基础](./series/semiconductor-foundations/README.md) | 硅、掺杂、晶体管、门电路与寄存器采样 |
| [计算微架构](./series/microarchitecture-v2/README.md) | 运算、流水线、指令控制、并行执行、异步搬运与资源协作（新版逐步发布；[旧版资料](./series/microarchitecture/README.md)） |
| [存储系统](./series/storage/README.md) | SRAM、DRAM、HBM 和高带宽闪存 |
| [芯片与系统互连](./series/interconnect/README.md) | 片上总线、网络、PCIe、SerDes 和光互连 |

新版 [存储系统导读](./series/storage-v2/README.md) 正在独立建设，覆盖存储介质、访问机制与系统组织。详见[存储系统重构计划书](./docs/storage-v2-plan.md)，原存储资料仍可阅读。

### 模型怎样计算，一次推理怎样跑起来？

| 系列 | 内容 |
| --- | --- |
| [算法与模型](./series/workload/README.md) | 模型组件、视觉、自动驾驶、机器人和芯片工作负载 |
| [推理运行时](./series/inference-runtime/README.md) | 请求路径、模型执行、状态管理、调度、解码、分布式服务与性能验证 |

新版 [编译器与运行时系统](./series/compiler-runtime/README.md) 正在独立建设，将覆盖从编译器、设备驱动到推理服务的完整软件栈。详见[重构计划书](./docs/compiler-runtime-plan.md)，原推理运行时资料仍可阅读。

### 一颗真实芯片怎样设计、实现和交付？

| 系列 | 内容 |
| --- | --- |
| [芯片架构实例](./series/chip-architectures/README.md) | 具体产品代际的计算、存储、互连和软件映射 |
| [芯片开发与实现](./series/chip-development/README.md) | 开发流程、晶圆制造、封装与测试 |

网站首页的[从哪里读起](https://microarch-flow.github.io/wiki/#series)提供各系列的阅读入口。源码目录归属与网站的文件级导航归属可以不同。

## 先回答哪些问题

1. **电路为何需要时间？** 电压变化需要电流给电容充放电；互连还有传播与反射。先读[共用基础](./series/microarchitecture/02-pipeline/electrical-timing-foundations.md)。
2. **时钟边沿为何约束频率？** 数据必须在采样前满足 setup；频率取决于路径、工艺、电压、温度和时钟关系。继续读 [流水线、时序与时钟域](./series/microarchitecture/02-pipeline/README.md)。
3. **数据如何保存、运算和移动？** 根据下表选专题。先定义资源、请求、服务过程和可观测结果，再决定模型需要保留什么细节。
4. **模型与真实芯片怎样对应？** 把参数、适用条件、校准来源和误差分开记录。理想估算不等于实测，也不自动证明性能或硬件正确性。

## 常用跨系列入口

| 学习问题 | 入口 | 与模拟器的关系 |
| --- | --- | --- |
| SRAM 和 DRAM 如何保存并提供数据？ | [RAM 专题主页](./series/storage/reading-and-reference/01-reading/README.md)；[RAM：存储层级](./series/storage/01-memory-hierarchy/README.md) | 时序、容量、bank 冲突、带宽 |
| 运算单元如何形成吞吐？ | [从门电路到 AI 计算单元](./series/microarchitecture/reading-and-reference/01-routes/README.md)；[运算数据通路](./series/microarchitecture/01-datapath/README.md) | 流水线、操作延迟、资源占用 |
| 多个模块如何共享片上通路？ | [BUS 专题主页](./series/interconnect/BUS/README.md)；[BUS：互连基础](./series/interconnect/BUS/02-fundamentals/README.md) | 仲裁、握手、背压 |
| 多节点如何路由和争用？ | [NOC 专题主页](./series/interconnect/NOC/README.md)；[NOC：路由器](./series/interconnect/NOC/02-router-microarchitecture/README.md) | 路由、缓冲、排队和流控 |
| 数据搬运如何与计算重叠？ | [DMA 专题主页](./series/microarchitecture/05-dma/README.md)；[域入口](./series/microarchitecture/05-dma/09-reference-research/repository-notes.md)；[DMA：基础](./series/microarchitecture/05-dma/02-fundamentals/README.md) | 描述符、请求并发、完成事件 |
| 主机与设备如何交换事务？ | [PCIe 专题主页](./series/interconnect/PCIE/README.md)；[PCIe：链路与事务](./series/interconnect/PCIE/02-link-transaction-basics/README.md) | TLP、credit、completion 和往返延迟 |
| 存储内计算如何改变数据路径？ | [CIM 专题主页](./series/microarchitecture/08-in-memory-computing/README.md)；[域入口](./series/microarchitecture/08-in-memory-computing/10-reference/source-notes.md)；[CIM：电路与宏](./series/microarchitecture/08-in-memory-computing/04-circuit-and-macro/README.md) | 阵列、外围电路、精度及服务时间 |
| 电信号怎样转换为光链路？ | [CPO 专题主页](./series/interconnect/CPO/README.md)；[CPO：光链路基础](./series/interconnect/CPO/04-optical-engine/optical-link-basics.md) | 转换、传输、功率预算和误码假设 |
| 工艺、封装和测试如何约束设计？ | [FAB 专题主页](./series/chip-development/FAB/wiki/README.md)；[FAB：封装信号完整性](./series/chip-development/FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md) | PVT、寄生参数、良率和可靠性边界 |
| 高速串行数据怎样跨通道并恢复？ | [SerDes 专题主页](./series/interconnect/SERDES/README.md)；[SerDes：全局链路](./series/interconnect/SERDES/01-overview/README.md) | 通道、收发、训练、设计验证与系统建模 |
| NAND 怎样在计算附近提供高带宽？ | [HBF 专题主页](./series/storage/05-hbf/README.md)；[HBF：一次读取](./series/storage/05-hbf/04-read-walkthrough.md) | 地址映射、阵列并行、维护与可靠性 |

各专题的现行正文位于系列目录；`wiki.old` 和 `docs/archive/` 保存历史资料。产业与产品资料具有时效性，需要按原始来源和日期核验。

[九专题基线问题与正文证据](./docs/reviews/2026-11-09-topic-review.md) · [第二轮逐篇评审](./docs/reviews/round-2/README.md) · [第三轮有限资源盲测](./docs/reviews/round-3/README.md)
