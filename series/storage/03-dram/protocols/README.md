# DRAM 命令与接口

上级：<span id="dram-协议层"></span>[存储系统](../../README.md)

相关：[DRAM 单元与阵列](../foundations/README.md) · [DRAM 控制器](../../04-dram-controller/README.md) · [原有 RAM 阅读入口](../../reading-and-reference/01-reading/README.md)

## DRAM 协议层：接口契约包括什么？ {#这页在回答什么问题}

“DRAM 协议层”从常见显式命令出发，解释时序、PHY 训练和接口家族。它回答器件允许做什么；控制器如何选择请求和安排命令，留给[控制器专题](../../04-dram-controller/README.md)。

## 从阵列约束到接口协议

ACT、列访问和 PRE 将行状态暴露给控制器；时序参数限制命令与数据的相对时间。PHY 在电气接口上发送和接收信号，需要遵循初始化及训练要求。DDR、LPDDR、GDDR、HBM 根据不同系统目标组织接口，具体能力要按代际、模式与产品核对。

并非所有采用 DRAM 单元的器件都向主机公开相同命令。例如 [Infineon 的 PSRAM](https://www.infineon.com/products/memories/psram-pseudostatic-dram) 将动态存储管理与 SRAM 类外部接口组合；不能从内部单元直接推断外部命令集。

## 阅读顺序

1. [同一个 DRAM bank 的三笔读取](./commands-act-rd-wr-pre.md)：跟着三笔请求走过未开行、行命中和行冲突，把 ACT、RD、PRE 与每次等待联系起来。
2. [DDR 双沿传输](./why-double-data-rate.md)
3. [DRAM PHY 初始化与训练](./dram-interface-init-training.md)
4. [DDR1 到 DDR5](./ddr-generation-evolution.md)
5. [DRAM 接口家族比较](./ddr-lpddr-gddr-hbm-tradeoff-map.md)
6. [LPDDR 与低功耗](./lpddr-low-power-mobile.md)
7. [GDDR 与高带宽](./gddr-graphics-bandwidth.md)
8. [HBM 堆叠与宽接口](./hbm-stacked-wide-io.md)

想比较系统选型，可以从[接口家族比较](./ddr-lpddr-gddr-hbm-tradeoff-map.md)进入对应接口。要建立命令级模型，可先用这[三笔读取](./commands-act-rd-wr-pre.md#three-reads)检查一条时间线，再到[控制器专题](../../04-dram-controller/README.md)看多笔请求怎样排队和调度。

## 一句话理解

命令与时序定义器件契约，PHY 实现电气传输，不同接口家族再选择各自的组织与工作目标。

## 建模启示

明确器件模式、命令采样沿、数据位宽、burst、时序和初始化状态；不要把理论数据率当作可持续带宽，也不要把一种 DDR 代际的规则直接套用于其他接口。
