# HBM 的堆叠与封装内互连

<span id="hbm-的-25d3d-集成与-tsv-技术"></span>

上级：[存储模块、封装与集成](./README.md)
相关：[HBM 接口与伪通道](../../03-dram/protocols/hbm-stacked-wide-io.md) · [HBM 成本](./why-hbm-is-expensive.md)

## 这页在回答什么问题

HBM 的 DRAM die 怎样在 stack 内连接？stack 又怎样连接计算 die？这两个问题分别涉及垂直堆叠和封装内互连，不能只用“3D 封装”一个词回答。

## TSV、堆叠与近距宽接口

HBM 将多个 DRAM die 组织成 stack，并通过宽接口与计算侧通信。TSV（through-silicon via，硅通孔）提供穿过硅片的垂直连接路径，配合键合等结构，将堆叠 die 的信号和供电连接起来。stack 的容量与内部连接，不等于计算 die 到 stack 的完整接口。

| 观察范围 | 要回答的问题 | 常见实现 |
| --- | --- | --- |
| HBM stack 内部 | 多层 DRAM die 如何连接？ | die 堆叠与 TSV 等垂直互连。 |
| 计算 die 到 stack | 大量信号如何在封装内连接？ | 硅中介层、RDL 中介层或局部硅桥等。 |
| 系统级 3D | 计算与其他 die 是否垂直集成？ | 取决于产品，不能仅凭 HBM stack 是 3D 推出。 |

“DRAM die 堆叠”也不等同于在一个 die 内把存储单元做成立体结构。[DRAM 工艺与堆叠](../../03-dram/foundations/dram-process-stacking-trends.md)进一步区分这些层次。

2.5D 常用于描述多个 die 在封装内并排、通过高密度结构互连。实现不局限于完整的硅中介层：[TSMC CoWoS](https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm)分别介绍硅中介层、RDL 及结合局部硅互连的方案；[Intel Agilex 7 M 系列](https://www.intel.com/content/www/us/en/docs/programmable/773264/23-4-3-0-0/hbm2e-in-m-series-devices.html)使用 EMIB 硅桥连接 HBM2E。两者是具体实现，不代表所有 HBM 系统都相同。

### 宽接口怎样形成带宽

在指定方向和 payload 位宽下，接口理论峰值可按 **每引脚传输率 × 数据引脚数 ÷ 8** 计算；多个独立接口可以在满足相同统计条件时相加。传输率已用每秒传输次数表示时，不再额外乘以 DDR 的双沿系数。

例如，假设一个 stack 有 1,024 条 payload 数据线、每条为 3.2 Gb/s，单方向理论峰值为 **409.6 GB/s**。这是用于理解数量关系的接口估算，不包含刷新、命令限制、竞争和上游供数损失。实际 HBM 代际、通道和伪通道组织见 [HBM 接口文章](../../03-dram/protocols/hbm-stacked-wide-io.md)。

近距互连使高密度布线更可行，但不消除供电、信号完整性、热、机械应力和测试问题。比较“带宽密度”时，还须说明分母是接口边缘长度、封装面积，还是其他基准。

## 一句话理解

HBM 的垂直堆叠和计算侧宽互连解决不同的问题；一个系统可以同时使用两者。

## 建模启示

分别记录 stack 数量、每 stack 容量和接口组织，以及计算侧连接、共享路径、供电和热边界。峰值带宽是接口上界；实际带宽需要结合访问形状和测量窗口。制造和测试细节可进一步阅读 [FAB 的 HBM 封装案例](../../../chip-development/FAB/wiki/04-back-end-packaging/hbm-as-case-study/README.md)。
