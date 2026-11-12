# PCIe 链路训练案例：从现象到证据

上级：[初始化与链路训练](./README.md)

PCIe 使用链路训练与状态机（LTSSM）管理链路建立和状态变化。下面以 PCIe 5.0 系统的可观察过程为例，说明状态与物理条件如何配合；完整状态、转移条件和定时要求应查对应版本的 PCIe 规范。

## 建立链路的几个观察点

常见建立路径会经过 `Detect`、`Polling`、`Configuration`，进入可传输业务的 `L0`。实际状态机包含更多子状态、条件和返回路径，不能把这四个名称画成只允许前进的完整流程。

PCI-SIG 对 PCIe 5.0 的说明指出，链路从 `2.5 GT/s` 开始，再向双方支持的较高速率训练。最终速率和宽度需要以实际协商及训练结果为准；不能仅凭两端标称能力断言一定达到某一速率。速率变化及恢复可以涉及 `Recovery` 等状态，具体过程取决于版本和触发条件。[PCI-SIG：PCIe 5.0 测试问答](https://pcisig.com/blog/pcie%C2%AE-50-protocol-and-electrical-compliance-testing-deep-dive-webinar-qa)

| 观察 | 能说明什么 | 还不能说明什么 |
| --- | --- | --- |
| TX PLL 锁定 | 某个本地时钟状态满足器件定义 | 对端已收到正确数据 |
| 接收端恢复时钟 / 对齐 | 对应接收路径满足其状态定义 | 整条协议链路已经进入 L0 |
| 链路进入 L0 | 该时刻链路进入规定运行状态 | 所有速率、环境和长期误码条件都合格 |
| 读到 `8 GT/s`、`x4` | 该观察时刻的速率与宽度 | 降速原因或应用吞吐量 |

## 一个假设的日志片段

假设两端都支持 PCIe 5.0 和至少 x4。日志先显示 `2.5 GT/s`、链路进入 `L0`，之后进入 `Recovery`；恢复后读到 `8 GT/s`、`x4`。这是人为构造的观察，不代表所有设备会依这个顺序进入每个状态。

它表明最终观察到的是 Gen3 速率和 x4 宽度，不能仅由此判断是配置、兼容性、通道余量还是其他原因。若速率与宽度保持不变，该方向仅扣除 `128b/130b` 的理论上限约为 `3.938 GB/s`；实际有效吞吐还要考虑协议和业务开销，计算见[怎样计算带宽和每比特能耗？](../05-signaling-and-metrics/bandwidth-power-efficiency.md)。

接下来应取得两端能力与目标配置、完整 LTSSM 日志、每 lane 状态、错误计数和环境条件。需要时按对应标准和器件手册执行电气及互通测试。PCI-SIG 将电气合规、状态机压力测试与系统互通区分开来；其中一项通过不能自动证明其他项通过。[PCI-SIG：PCIe 5.0 系统实现](https://pcisig.com/sites/default/files/files/PCI-SIG-Seamless_Transition_to_PCIe_5.0_in_System_Implementations_FINAL.pdf)

相关背景可读现有 [PCIe 分层架构](../../../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)与[链路降级案例](../../../PCIE/wiki/06-workloads-case-studies/link-downgrade-case-card.md)。

## 接下来怎么读

读[设计与验证：怎样建立可信证据？](../07-design-and-validation/README.md)，继续了解需求、仿真和实验室测试。也可以回到 [SerDes Wiki：从比特到可恢复的信号](../README.md)，查阅术语、资料与自测。
