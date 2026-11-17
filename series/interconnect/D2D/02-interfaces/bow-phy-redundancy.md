# BoW PHY 2.0：一条数据线坏了怎样绕过？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

并行接口把不同的数据位分配给不同的物理线。如果一条线长期无法正常工作，单纯重新发送可能反复遇到同一故障。支持冗余的接口可以改用备用线，但发送端和接收端必须对数据位的位置达成一致。

本文使用 [BoW PHY 2.0 第 13 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)的映射规则，说明一个单向 slice 怎样绕过坏线。正常的数据线与随路时钟关系先见 [BoW PHY 2.0](../bow-phy.md)。

## 先区分逻辑数据位和物理线

假设芯粒 A 的发送 slice 向芯粒 B 的接收 slice 传输 16 个逻辑数据位，编号 D0–D15。正常映射下，逻辑 D0 由物理 D0 承载，逻辑 D1 由物理 D1 承载，依此类推。

本例的 slice **支持冗余**，并包含可作为备用 I/O 的 AUX 和 FEC 两条线。CLK+、CLK− 为随路时钟。本例假设两端及其配置兼容，备用线和时钟线都正常；这里只讨论 A → B 方向。

规范要求支持这一冗余机制的 slice 能绕过包括 AUX、FEC 在内的最多两条缺陷数据线。它不为 CLK+、CLK− 凸点定义同样的冗余机制；是否支持冗余也不能从“使用 BoW”这一名称单独推断。[BoW PHY 2.0，第 13 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

## 物理 D4 坏了

假设测试发现物理 D4 不可用，而 AUX、FEC 和其他数据线可用。按规范中的单线修复规则，逻辑 D4 及其以下的逻辑位向低编号方向移动一条线。结果如下：

| 逻辑数据位 | 正常时使用的物理线 | 绕过 D4 后使用的物理线 |
| --- | --- | --- |
| D0 | D0 | AUX |
| D1 | D1 | D0 |
| D2 | D2 | D1 |
| D3 | D3 | D2 |
| D4 | D4 | D3 |
| D5–D15 | D5–D15 | D5–D15，逐位对应 |

发送端将各逻辑位送到新位置，接收端按相同映射取回它们。例如，接收端要把从物理 AUX 采样的位还原为逻辑 D0。物理 D4 被绕开，FEC 在这个单线例子中未用于承载数据。[BoW PHY 2.0，第 13 节的映射示例](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

如果只修改发送端，接收端仍按原位置取数，就会把逻辑位混淆。**备用线可用和两端映射一致，都是恢复正确数据所需的条件。**

## 两条坏线与备用资源

规范还举例：若物理 D4 和 D6 都有缺陷，逻辑 D0–D4 使用 AUX、D0–D3；逻辑 D5 仍用物理 D5；逻辑 D6–D15 使用物理 D7–D15 和 FEC，逐位对应。这样两侧备用线都参与承载，坏的 D4、D6 被绕过。

冗余有资源代价。AUX 和 FEC 的名称不表示它们永远闲置，也不表示 PHY 自身一定实现了 FEC 算法。[BoW Memory Addendum 第 13 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)指出，在其内存应用中，如果这两条线已经用于 ECC 数据而系统还需要冗余，就需要增加备用线。不能把一条线同时按两种用途重复计数。

## 怎样判断修复是否有效

发现错误并不自动说明哪条物理线坏了。系统需要结合受支持的测试路径、已知码型和观察结果定位故障；采用何种检测、配置和报告方式，取决于接口及实现。

一个可检查的流程是：先确定可疑线，再按支持的规则配置两端映射，然后重新检查传输和上层访问。测试通过只说明该次测试覆盖的条件下获得了预期结果；仍需考虑工作速率、时序和故障是否间歇出现。[链路测试与故障定位](../03-system-design/link-testing-and-diagnosis.md)

这里的映射示例说明怎样使用备用连接，不保证某个产品支持运行中无中断修复，也不保证超过冗余能力的故障可以恢复。对于瞬时传输错误，系统还可能使用检错、纠错或重放；这些机制与绕过物理坏线的职责不同。[跨芯粒链路错误检测与重放](../03-system-design/link-reliability.md)

## 接下来怎么读

- [BoW PHY 2.0](../bow-phy.md)：认识 slice、数据线和时钟。
- [跨芯粒链路错误检测与重放](../03-system-design/link-reliability.md)：比较坏线重映射与重新发送数据。
- [链路测试与故障定位](../03-system-design/link-testing-and-diagnosis.md)：查看检测路径和定位边界。
- [芯粒互操作与启动](../03-system-design/interoperability-and-bring-up.md)：了解两端配置及链路就绪的其他条件。
