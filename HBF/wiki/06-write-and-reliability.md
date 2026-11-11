# 写入、FTL 与可靠性管理

上级：[HBF Wiki](./README.md)

HBF 适合讨论读密集数据，但底层仍是 NAND。写入顺序、擦除、磨损、数据保持和错误恢复，都需要明确责任。下面先区分常见 SSD 的管理模式，再说明 OCP HBF v0.7 的边界。

## 常见 SSD 的 FTL 做什么

普通块设备接口通常让 host 使用逻辑块地址。SSD 中的 Flash Translation Layer（FTL）维护逻辑地址到物理位置的映射，并配合垃圾回收、坏块管理、错误纠正和磨损均衡。不同 SSD 的具体功能、缓存和恢复保证仍不同。

例如，覆盖一个逻辑地址时，控制器可能把新数据写到其他空闲位置并更新映射。之后回收旧 block 时，它可能先搬走仍有效的数据，再擦除 block。这个过程为 host 提供便利，但会占用内部带宽和擦写寿命。背景见 [Western Digital Flash 101](https://documents.sandisk.com/content/dam/asset-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-sandisk-flash101-management.pdf)。

## OCP v0.7 的 HBF 写入约束

HBF 不是没有控制器。v0.7 让 base die 执行内部管理，同时让 host 参与更明确的数据布局和可靠性处理。对 **NAND 区域**，规范第 5.4 节描述了下列要点：

1. base die 将写数据收集到 4 KiB 的 core-die 写入粒度。host 必须在配置的时间限制内完成需要的数据；超时可能返回错误。
2. 规范对 channel 局部地址和 NAND block 内的 4 KiB 写入顺序施加约束。软件不能假定任意小范围都能像 SRAM 一样直接覆盖。
3. 写入某 NAND block 的 page 0 时，规范描述设备自动擦除该 block。系统必须先处理其中仍有效的数据，避免覆盖造成数据丢失。
4. NAND 写响应在数据写入 core die 之后完成。这个接口完成条件不能单独证明应用级事务、断电恢复或跨设备持久性。

具体命令、地址计算、错误及产品扩展，以 [OCP v0.7 第 5.4–5.7 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)和目标产品为准。可选 SRAM scratchpad 的写入粒度和断电行为不同，不能与 NAND 区域混为一谈。

## 磨损均衡、映射和垃圾回收

program/erase（P/E）会使 NAND 逐渐磨损。高频写入若长期集中在少数 block，会更早消耗这些区域的寿命。均衡磨损的目标是让写入消耗更合理地分布；它不消除有限寿命。

OCP v0.7 第 11.4 节允许选择产品相关的 base-die 驱动磨损均衡，或 host 控制的 zone remapping。该版本明确说设备不提供自动垃圾回收或有效数据搬迁；需要区分**改变映射**与**实际搬走有效数据**。host 控制 zone 交换时，规范要求先确认相关数据已失效且不再有读取，并遵守 zone 与 NAND block 的粒度约束。[OCP v0.7，第 11.4 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)

一种常用指标是**写放大 = NAND 实际编程字节数 / host 写入字节数**。比较时，分子与分母必须使用同一时间窗口，并明确是否包含刷新、迁移和冗余。写放大不是单独就能算出产品寿命的充分信息；还需要容量、磨损分布、P/E 限额和工作条件。

## 数据刷新不是 DRAM refresh

NAND 非易失，但电荷保持、温度、P/E 磨损和读干扰会影响数据可靠性。对 NAND 的数据刷新通常意味着在可靠性条件要求时重新保存或恢复数据；它不同于 DRAM 为保持电容电荷而进行的周期性刷新。

OCP v0.7 的软件指南要求按产品可靠性条件安排数据刷新，并讨论按保持时间或读次数触发。文档给出通常 24–48 小时的示例表述，但具体保持时间、触发阈值和操作方法是产品相关参数，不能把该区间视为所有 HBF 的保证。刷新若与工作负载共享 die 或通路，也会影响可用带宽和延迟。[OCP v0.7，第 11.5 节](https://www.opencompute.org/documents/ocp-hbf-architecture-specification-v0-7-0-final-pdf/)

## ECC、错误和恢复

ECC 可以纠正能力范围内的错误，但不能保证修复所有数据。v0.7 区分可纠正错误、不可纠正错误、重试和其他状态；部分状态需要 host 刷新数据或从备份恢复。一次读取是否成功，应由响应状态与数据有效性共同判断。

例如：base die 报告不可纠正错误时，若系统有有效副本，可以从副本恢复并按规范重写；若没有副本，不能假设 ECC 一定能恢复原数据。高读取次数也可能导致读干扰，所以“写一次、读很多次”虽然降低写入压力，仍需要考虑刷新和数据健康。

下一篇把这些约束放回[AI 工作负载和模型](./07-workload-and-modeling.md)。
