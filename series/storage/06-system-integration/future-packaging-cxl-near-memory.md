# 存储扩展与近存计算：接口、计算位置和集成

<span id="cxl近存计算与未来封装方向"></span>

上级：[存储系统集成与选型](./README.md)
相关：[存储层次与系统角色](../01-memory-hierarchy/01-system-basics/memory-hierarchy-as-system.md) · [CXL 与 PCIe 的边界](../../interconnect/PCIE/07-advanced-topics/cxl-and-pcie-boundary.md) · [HBM-PIM 案例](../../microarchitecture/08-in-memory-computing/09-research-frontier/case-study-samsung-hbm-pim-research-angle.md)

## 这页在回答什么问题

当本地内存的容量或数据搬运成为约束时，增加可访问的存储层、把计算移近数据、改变物理封装，分别能解决什么问题？这些方法可以组合，但它们作用于不同系统边界。

## 协议、计算位置与封装的边界

| 方法 | 改变什么 | 需要进一步核对 |
| --- | --- | --- |
| CXL 内存扩展 | 主机通过支持的协议访问设备连接的内存 | 设备类型、拓扑、内存映射、共享能力与软件配置。 |
| 近存计算 / PIM | 在存储附近或存储结构中执行部分操作 | 操作位置、支持的算子、数据所有权和同步。 |
| 封装集成 | 芯片及互连的物理组织 | 连接密度、供电、散热、测试和可维护性。 |

物理距离、协议语义和计算位置是三个不同维度。CXL 可以用于不同设备和拓扑；不能仅凭 CXL 名称认定某条路径一定远于或慢于所有本地内存路径。也不能只因设备可寻址，就假定数据会自动放在最合适的层次。

### CXL：区分扩展、池化和共享

以 Type 3 内存扩展为例，主机可通过所支持的 CXL.mem 模式访问设备连接的内存。容量池化是对资源进行分配和回收；多个主机能否**同时访问同一物理内存位置**以及如何保持一致性，是另一个问题。

[CXL 联盟对 2.0 池化的说明](https://computeexpresslink.org/blog/cxl-2-0-specification-memory-pooling-questions-from-the-webinar-part-2-2391/)指出该版本的相应池化模式不提供多个主机对同一设备物理位置的共享。[CXL 3.0 白皮书](https://computeexpresslink.org/wp-content/uploads/2023/12/CXL_3.0_white-paper_FINAL-1.pdf)进一步介绍了共享能力；具体系统仍须具备相应设备、拓扑、协议和配置。

扩展内存的价值可能是容量配置或资源利用率，而非降低每次访问延迟。评估时要测量具体路径的服务时间、带宽、竞争和负载分布，并确认操作系统或运行时的数据放置与迁移策略。协议方向和设备类型见 [CXL 与 PCIe 的边界](../../interconnect/PCIE/07-advanced-topics/cxl-and-pcie-boundary.md)。

### 计算移近数据：先描述执行位置

近存计算通常指将部分处理移到靠近数据的位置；PIM（processing in memory）用于描述不同程度的存储侧处理。名称的使用范围会随资料变化，因此比较时应明确：计算在独立逻辑、内存 die 的处理单元，还是阵列及其外围电路中执行；数据通过哪些接口移动；支持哪些操作。

<span id="hbm-pim-data-path"></span>

例如，[Samsung 的 HBM-PIM 技术介绍](https://semiconductor.samsung.com/news-events/tech-blog/hbm-pim-cutting-edge-memory-technology-to-accelerate-next-generation-ai/)描述了在 HBM 中加入处理能力。它并不意味着 DRAM cell 本身完成所有算术，也不表示所有应用都能获益。具体 bank、命令和软件约束见 [HBM-PIM 案例](../../microarchitecture/08-in-memory-computing/09-research-frontier/case-study-samsung-hbm-pim-research-angle.md)。

以 Aquabolt-XL 为例，权重已放进一个 DRAM bank。选中一行后，权重从阵列的局部 I/O 送到同一片 DRAM die 上紧邻 bank 的处理单元，与寄存器里的输入相乘。这样省下的是把这份权重送出 HBM 再计算的那一程。输入若来自主机，仍要送进来；触发执行的命令也要经过内存控制器。多个 bank 可随同一条命令并行工作。若两组结果共用同一条对外数据通路，读回它们仍要分时占用这条通路。[Samsung 的芯片结构与命令图](https://hc33.hotchips.org/assets/program/conference/day1/20210813_HC33_Aquabolt-XL_PIM_Jin_Kim_slide.pdf)

假设把同一个点积拆给 A、B 两组本地单元，A 算出 23，B 算出 −11，并约定由主机合并。23 刚出现在 A 的累加寄存器时，主机能从结果地址读到它了吗？程序要先把两组各自的结果向量写回预留的 bank 地址，结束存储侧执行并恢复普通读取。主机侧的内存控制器随后从 HBM 读回包含部分和的数据块。主机取出对应的两项，相加才得到 12。[跟着 23 走出本地寄存器](../../microarchitecture/08-in-memory-computing/02-memory-technologies/dram-pim-foundation.md#read-back-local-sum) · [检查两份结果何时都可读](../../microarchitecture/08-in-memory-computing/02-memory-technologies/dram-pim-deep-dive.md#when-partials-are-visible)

把计数器放在 HBM 与主机之间的数据接口上。若点积仍在主机执行，只加宽接口而保持请求序列和传输粒度不变，同一批权重仍要跨过它，改变的是每拍最多能送多少字节。若改在 bank 旁执行，这批驻留权重的本地读取可以从跨接口流量中扣掉，但主机送入的操作数、读回 23 和 −11 所在数据块的实际字节都要计入。若预算覆盖整台加速器，就把它所有 HBM 接口在同一时间窗内的读写字节加起来，再除以这台加速器同期生成的 token 数。[按每 token 的实际流量估算持续带宽](./hbm-vs-lpddr-for-npu.md#budget)

假设一个操作原来要将大量输入送到处理器、计算后只返回少量结果。若存储侧支持该操作，且任务能在那里访问输入，则减少跨边界传输可能有利；但还要计入启动、数据布局、同步、局部计算能力和结果搬运。数据需要频繁在主机和存储侧交替修改时，这些代价可能抵消收益。

## 一句话理解

CXL 定义可支持的系统互连语义；近存计算改变操作位置；封装改变物理组织。判断收益必须检查三者的具体组合。

## 建模启示

对每个存储层记录容量、访问者、带宽、服务时间、共享与一致性范围；对连接记录拓扑和竞争；对计算能力记录支持的操作、并发、启动及同步成本。如果某层的端到端延迟已经包含链路和协议，就不能再将相同链路延迟加一次。HBF 的 NAND 路径和软件管理另见 [HBF 专题](../05-hbf/README.md)。
