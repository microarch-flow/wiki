# 微架构与物理实现学习入口

本 wiki 面向希望理解芯片，并建立可解释模拟器的读者。建议先读[电路到时序的共用基础](./electrical-timing-foundations.md)。它从电容充电算到采样边沿，再说明这些连续过程如何成为离散事件模型的参数。

网站版的本地预览、内容维护与 GitHub Pages 发布方法见[网站构建与维护](./website/README.md)。

## 先回答哪些问题

1. **电路为何需要时间？** 电压变化需要电流给电容充放电；互连还有传播与反射。先读[共用基础](./electrical-timing-foundations.md)。
2. **时钟边沿为何约束频率？** 数据必须在采样前满足 setup；频率取决于路径、工艺、电压、温度和时钟关系。继续读 [COMPUTE 时钟与流水线](./COMPUTE/wiki/04-clocking-and-pipeline/README.md)。
3. **数据如何保存、运算和移动？** 根据下表选专题。先定义资源、请求、服务过程和可观测结果，再决定模型需要保留什么细节。
4. **模型与真实芯片怎样对应？** 把参数、适用条件、校准来源和误差分开记录。理想估算不等于实测，也不自动证明性能或硬件正确性。

## 九个专题

| 学习问题 | 入口 | 与模拟器的关系 |
| --- | --- | --- |
| SRAM 和 DRAM 如何保存并提供数据？ | [RAM 专题主页](./RAM/wiki/README.md)；[RAM：存储层级](./RAM/wiki/01-overview/README.md) | 时序、容量、bank 冲突、带宽 |
| 运算单元如何形成吞吐？ | [COMPUTE 专题主页](./COMPUTE/wiki/README.md)；[COMPUTE：数据通路](./COMPUTE/wiki/02-datapath-foundations/README.md) | 流水线、操作延迟、资源占用 |
| 多个模块如何共享片上通路？ | [BUS 专题主页](./BUS/wiki/README.md)；[域入口](./BUS/README.md)；[BUS：互连基础](./BUS/wiki/02-fundamentals/README.md) | 仲裁、握手、背压 |
| 多节点如何路由和争用？ | [NOC 专题主页](./NOC/wiki/README.md)；[NOC：路由器](./NOC/wiki/02-router-microarchitecture/README.md) | 路由、缓冲、排队和流控 |
| 数据搬运如何与计算重叠？ | [DMA 专题主页](./DMA/wiki/README.md)；[域入口](./DMA/README.md)；[DMA：基础](./DMA/wiki/02-fundamentals/README.md) | 描述符、请求并发、完成事件 |
| 主机与设备如何交换事务？ | [PCIe 专题主页](./PCIE/wiki/README.md)；[PCIe：链路与事务](./PCIE/wiki/02-link-transaction-basics/README.md) | TLP、credit、completion 和往返延迟 |
| 存储内计算如何改变数据路径？ | [CIM 专题主页](./CIM/wiki/README.md)；[域入口](./CIM/README.md)；[CIM：电路与宏](./CIM/wiki/04-circuit-and-macro/README.md) | 阵列、外围电路、精度及服务时间 |
| 电信号怎样转换为光链路？ | [CPO 专题主页](./CPO/wiki/README.md)；[CPO：光链路基础](./CPO/wiki/04-optical-engine/optical-link-basics.md) | 转换、传输、功率预算和误码假设 |
| 工艺、封装和测试如何约束设计？ | [FAB 专题主页](./FAB/wiki/README.md)；[FAB：封装信号完整性](./FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md) | PVT、寄生参数、良率和可靠性边界 |

各专题的 `wiki` 是现行内容；`wiki.old` 是历史归档。产业与产品资料具有时效性，需要按原始来源和日期核验。

[九专题基线问题与正文证据](./reviews/2026-11-09-topic-review.md) · [第二轮逐篇评审](./reviews/round-2/README.md) · [第三轮有限资源盲测](./reviews/round-3/README.md)
