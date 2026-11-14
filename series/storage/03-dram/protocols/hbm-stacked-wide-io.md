# HBM：堆叠、宽接口与伪通道

上级：<span id="hbm从协议层面看它和-ddr-的根本不同"></span>[DRAM 命令与接口](./README.md)

相关：[GDDR 高速接口](./gddr-graphics-bandwidth.md) · [HBM 的 2.5D/3D 集成与 TSV](../../06-system-integration/packaging/hbm-2.5d-3d-tsv.md) · [HBM 成本](../../06-system-integration/packaging/why-hbm-is-expensive.md) · [HBM 与 LPDDR 选型](../../06-system-integration/hbm-vs-lpddr-for-npu.md) · [SerDes：HBM 与 3D 堆叠](../../../interconnect/SERDES/wiki/08-system-applications/hbm-and-3d.md)

## HBM：从协议层面看它和 DDR 的根本不同？ {#这页在回答什么问题}

从协议层面看 HBM 和 DDR 的根本不同在哪里？本页解释堆叠 DRAM 的宽数据接口和通道组织；封装、散热与成本在相关专题展开。不同 HBM 代际和控制器的组织不完全相同。

## 宽 I/O、距离与堆叠约束

HBM 将多个 DRAM die 与相关逻辑组织为 stack，并通过宽接口连接计算侧。近距离宽连接有利于提供高带宽密度，但需要相应封装、供电和散热；能耗、成本和最终性能必须在具体系统中比较，不能仅凭接口名称断言。

以 [AMD HBM2 控制器拓扑](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Topology)为例：一个 stack 有 8 个 128-bit channel，每个 channel 分为两个 64-bit pseudo channel。两个 pseudo channel 的数据路径可分别使用，但共享命令、地址和控制总线，部分操作与时序仍有关联。该控制器的 pseudo-channel 模式使用 BL4，因此每次 64-bit 数据传输组的名义数据量为 `64 × 4 / 8 = 32 B`；不要把它当成所有 HBM 产品的固定粒度。

[AMD 的另一项配置示例](https://docs.amd.com/r/en-US/pg313-network-on-chip/Raw-Throughput-Evaluation)以 1,600 MHz 时钟、双沿 3.2 Gb/s/数据引脚计算：一个 64-bit pseudo channel 理论峰值 `64 × 3.2 / 8 = 25.6 GB/s`；16 个合计 `409.6 GB/s`，两个独立 stack 合计 `819.2 GB/s`。这里使用十进制 GB，且不含协议损失；上游 NoC 端口、地址分布、刷新与访问模式可能限制实际吞吐。

后续代际的宽度、速率与集成方式会变化，例如 [Micron HBM4 产品信息](https://www.micron.com/products/memory/hbm/hbm4)描述了不同接口配置。HBM 仍需要管理行、bank、刷新和时序；宽接口不保证随机访问延迟或有效带宽自动优于其他系统。

## 一句话理解

HBM 将堆叠、多个通道与宽接口结合；有效并行度还受共享命令、控制器和上游路径约束。

## 建模启示

记录每 stack 的通道、pseudo channel、有效数据位宽、引脚速率、burst 和共享资源，再分别计算峰值与实际利用率。封装成本、热约束和能耗应来自目标系统数据。
