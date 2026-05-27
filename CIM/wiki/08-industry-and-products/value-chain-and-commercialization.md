# CIM 商业化路径：从论文到 Tape-Out 到量产的真实门槛

上级：[08 产业与产品](README.md)
相关：[制造与测试挑战](manufacturing-and-test-challenges.md), [软件栈](../06-software-stack/README.md), [边缘 AI](../07-workloads/edge-ai-and-cim.md)

## 这页在回答什么问题

这页回答：为什么 CIM/PIM/NMC 从论文指标到可交付产品之间隔着一条很长的工程链。

一条完整商业化路径至少包含七段：

| 阶段 | 证明内容 | 还不能证明什么 |
| --- | --- | --- |
| research macro | array、ADC/SA、bitline compute 或 bank compute 可工作 | 系统性能、良率、软件可用性 |
| test chip | 工艺和基本接口可 tape-out | 客户模型、量产测试、长期可靠性 |
| product chip | 有封装、I/O、功耗管理、compiler/runtime | 客户部署和 volume shipment |
| board/card/module | 能接入 PCIe/M.2/DIMM/SoC 或 memory controller | 客户工作流和运维成熟 |
| software stack | 模型转换、量化、runtime、driver 可用 | 长尾模型和客户自定义算子覆盖 |
| customer validation | 在真实 workload 上跑通 POC | 量产采购、SLA、现场维护 |
| volume shipment | 可持续制造、测试、交付、支持 | 下一代路线仍需重新验证 |

CIM 的特殊门槛在于“计算正确性”不是纯数字逻辑问题。Analog Flash/ReRAM CIM 需要写入-校验、温度/老化校准、ADC 精度选择、坏点管理和 noise-aware retraining；SRAM digital CIM 需要证明 timing closure、DFT/BIST、array disturb、低比特量化和编译映射。客户真正采购的是稳定吞吐、可复现精度和可维护 SDK，而不是单个 macro 的峰值 TOPS/W。

PIM/NMC 的门槛不同。Samsung HBM-PIM、SK hynix AiM/AiMX 的关键不是 cell 物理，而是 memory command、controller、host runtime 与系统软件配合；这会牵动 [RAM 的 DRAM command/timing](../../../RAM/wiki/04-dram-foundations/README.md) 和 [BUS 的 host-visible command/doorbell/completion](../../../BUS/wiki/README.md)。UPMEM 这类 DIMM/server 近数据路线则要求开发者显式划分 host code 与 DPU code，处理数据搬移和同步。

“技术可行”“样片可跑”“demo 可展示”“客户可部署”“可量产交付”是五个不同状态。公司新闻稿里出现 demo、prototype、evaluation system、shipping、available、production，含义都不一样：demo 证明场景可演示；evaluation system 证明开发者可试用；shipping 需要看对象是样机、评估板还是量产 SKU；production 还要看是否有客户量产导入。

## 一句话理解

CIM 商业化不是把 macro 放大，而是把电路、芯片、封装、软件和客户验证串成可交付产品。

## 产业启示

真正稀缺的是跨层工程能力：能把 calibration/test/yield 做进制造流程，把 quantization/mapping 做进工具链，把 host integration 做进客户系统。没有这条链，论文级能效不会自动变成商业价值。
