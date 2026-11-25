# HBF 写入与可靠性：主机和设备如何分工

<span id="写入ftl-与可靠性管理"></span>

上级：[HBF 高带宽闪存](./README.md)

写入、FTL 与可靠性管理需要由谁负责？HBF 面向读密集数据，但底层仍是 NAND。写入顺序、擦除、磨损、数据保持和错误恢复都需要明确责任。下面先区分常见 SSD 的管理模式，再说明 OCP HBF v0.7 的边界。

## 常见 SSD 的 FTL 做什么

普通块接口 SSD 让主机读写逻辑块地址。主机更新 A 时，控制器可以先把新 A 写到空闲页，再更新闪存转换层（FTL）的映射。旧块中的 B 此刻可以留在原处。等控制器选中旧块回收，才需要先搬走仍有效的 B，再擦除整个块。这些额外的编程和擦除会消耗内部带宽和擦写寿命。[SSD 怎样更新映射](./02-nand-foundations.md#ftl) · [回收旧块时谁来搬 B](./02-nand-foundations.md#gc)

SSD 控制器还要协调坏块管理、纠错和磨损均衡。各产品的缓存与故障恢复保证不同。[Western Digital Flash 101](https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-sandisk-flash101-management.pdf)

## OCP v0.7 的 HBF 写入约束

OCP HBF v0.7 把数据聚合和块擦除交给 base die，主机要按接口规定安排写入顺序和数据保护。下面的约束适用于 **NAND 区域**。

1. base die 将写数据收集到 4 KiB 的 core-die 写入粒度。收到该逻辑单元的第一个 64 B 写入后，其余数据必须在主机配置的时限内到达 base die。超时后，该逻辑单元已发出的写请求会收到错误响应。若主机选择重试，可以重新发送完整 4 KiB。
2. 规范对 channel 局部地址和 NAND block 内的 4 KiB 写入顺序施加约束。软件不能假定任意小范围都能像 SRAM 一样直接覆盖。
3. 写入某 NAND block 的 page 0 时，规范描述设备自动擦除该 block。系统必须先处理其中仍有效的数据，避免覆盖造成数据丢失。
4. NAND 写响应在数据写入 core die 之后完成。这个接口完成条件不能单独证明应用级事务、断电恢复或跨设备持久性。

第 5.4 节还对 channel 局部地址的跳跃作出限制；第 11.5.2.6 节则说明多个 NAND block 可以同时写入，并要求各 block 内按顺序写。两处表述的具体适用范围应结合目标产品核实。不要把块内顺序直接解释为整个 channel 的所有写入必须按一个全局地址序列执行。

具体命令、地址计算、错误及产品扩展，以 [OCP v0.7 第 5.4–5.7 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)和目标产品为准。可选 SRAM scratchpad 的写入粒度和断电行为不同，不能与 NAND 区域混为一谈。

沿用 SSD 主文的 A、B，现在换成 HBF 的同块重写。假设这个 block 中要保留的数据只有 page 0 的 A 和 page 1 的 B。主机要把新 A 写回**这个块的 page 0**。在 SSD 的异地更新例子中，旧块可以等到回收时再处理。在这次 HBF 操作中，page 0 的写请求就会触发擦除。主机要在发这笔请求前先为 B 找好去处。[对照 SSD 中 A 更新后、旧块回收前的映射](./02-nand-foundations.md#gc)

1. 在发起 page 0 写入之前，host 先在其他位置保护仍需保留的 B，并准备好新 A。若要求断电后恢复，还须确保发生擦除前存在满足该恢复要求的有效副本。
2. 按目标设备的地址与写入规则，从 page 0 开始写入新 A。设备收到 page 0 写入时自动擦除该 block；host 在时间限制内送齐该 4 KiB，并检查写入响应。
3. 在前一 page 已按要求发送后，按顺序写入 page 1 的 B，并检查响应。这里选择等待前一 page 成功后再写下一页，以简化例子；这不规定所有实现都必须串行等待响应。
4. 两页成功后，系统才能按自己的事务规则更新对外可见的元数据。若超时、编程失败或中途断电，恢复依赖有效副本及系统的提交规则，不能假定旧 block 的内容仍完整。

对于同一 64 B 地址，v0.7 还规定混合读写顺序：若读命中 base die 已收集的写数据，可以从该数据返回；若对应部分仍未收到，则返回读取错误。它不是对任意部分写入提供透明成功读取的保证。[OCP v0.7，第 5.4.3、11.5.2 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)

## 磨损均衡、映射和垃圾回收

program/erase（P/E）会使 NAND 逐渐磨损。高频写入若长期集中在少数 block，会更早消耗这些区域的寿命。均衡磨损的目标是让写入消耗更合理地分布；它不消除有限寿命。

OCP v0.7 第 11.4 节允许选择产品相关的 base-die 驱动磨损均衡，或 host 控制的 zone remapping。该版本明确说设备不提供自动垃圾回收或有效数据搬迁；需要区分**改变映射**与**实际搬走有效数据**。host 控制 zone 交换时，规范要求先确认相关数据已失效且不再有读取，并遵守 zone 与 NAND block 的粒度约束。[OCP v0.7，第 11.4 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)

一种常用指标是**写放大 = NAND 实际编程字节数 / host 写入字节数**。比较时，分子与分母必须使用同一时间窗口，并明确是否包含刷新、迁移和冗余。写放大不是单独就能算出产品寿命的充分信息；还需要容量、磨损分布、P/E 限额和工作条件。

## 数据刷新不是 DRAM refresh

NAND 非易失，但电荷保持、温度、P/E 磨损和读干扰会影响数据可靠性。对 NAND 的数据刷新通常意味着在可靠性条件要求时重新保存或恢复数据；它不同于 DRAM 为保持电容电荷而进行的周期性刷新。

OCP v0.7 的软件指南要求按产品可靠性条件安排数据刷新，并讨论按保持时间或读次数触发。文档给出通常 24–48 小时的示例表述，但具体保持时间、触发阈值和操作方法是产品相关参数，不能把该区间视为所有 HBF 的保证。刷新若与工作负载共享 die 或通路，也会影响可用带宽和延迟。[OCP v0.7，第 11.5 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)

同一规范第 9 节列出 **85 °C 通电保持 24 小时**的指标，并提醒断电后的保持不能按通电条件推断。第 11.5 节要求产品给出通电和断电时的保持条件。这里的指标和示例都不是对任何具体产品长期断电保存的证明。若把刷新穿插在正常负载中，规范要求主机避免同时向同一 die 发出刷新和读取命令，以免增加读延迟。[OCP v0.7，第 11.5 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/#page=118)

## ECC、错误和恢复

ECC 可以纠正能力范围内的错误，但不能保证修复所有数据。v0.7 区分可纠正错误、不可纠正错误、重试和其他状态；部分状态需要 host 刷新数据或从备份恢复。一次读取是否成功，应由响应状态与数据有效性共同判断。

例如：base die 报告不可纠正错误时，若系统有有效副本，可以从副本恢复并按规范重写；若没有副本，不能假设 ECC 一定能恢复原数据。高读取次数也可能导致读干扰，所以“写一次、读很多次”虽然降低写入压力，仍需要考虑刷新和数据健康。

[OCP v0.7 的安全章节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)还描述可选的上电擦除和 sanitize 等功能。是否提供、如何配置以及重启后哪些数据可读，必须查看目标产品和系统的安全策略。

下一篇把这些约束放回[AI 工作负载和模型](./07-workload-and-modeling.md)。
