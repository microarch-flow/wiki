# SK hynix AiM/AiMX：属于 PIM 不是 CIM

上级：[公司卡片](README.md)
相关：[DRAM-PIM 深入](../../02-memory-technologies/dram-pim-deep-dive.md), [LLM decode 与 CIM](../../07-workloads/llm-decode-and-cim.md), [运行时与调度](../../06-software-stack/runtime-and-scheduling.md)

## 这页在回答什么问题

这页回答：SK hynix GDDR6-AiM/AiMX 为什么归 PIM，以及它的 prototype/card 演示说明了什么产业状态。

| 字段 | 内容 |
| --- | --- |
| 公司/对象 | SK hynix GDDR6-AiM 与 AiMX accelerator card |
| 本 wiki 分类 | PIM |
| 技术路线 | 在 GDDR6 memory chip 中加入 computational functions；多个 GDDR6-AiM 组成 AiMX card |
| compute paradigm | memory-chip/bank-level processing，不是 cell-level CIM |
| 产品层级 | GDDR6-AiM sample、AiMX prototype accelerator card |
| 目标市场 | AI/HPC、大数据、LLM/generative AI demo |

SK hynix 官方 2022 年公告说，GDDR6-AiM 是采用 PIM 技术的第一款产品 sample，并在 GDDR6 memory chips 中加入 computational functions。这个定义符合 PIM：计算位于 memory chip 内的独立功能单元，compute 与 DRAM cell 分离。来源：[SK hynix 2022 GDDR6-AiM announcement](https://news.skhynix.com/sk-hynix-develops-pim-next-generation-ai-accelerator/)。

2023 年，SK hynix 又展示 AiMX prototype accelerator card，多个 GDDR6-AiM 芯片组合在卡上用于 generative AI。官方公告明确称其为 prototype，并展示 OPT 13B 服务器系统 demo；其中 performance 条件还依赖 AiM Control Hub 以 ASIC 形式实现。来源：[SK hynix 2023 AiMX prototype announcement](https://news.skhynix.com/sk-hynix-debuts-first-gddr6-aim-accelerator-card-aimx-for-generative-ai/)。

这条路线的产业含义是：memory vendor 试图把 [RAM wiki 中的 GDDR/DRAM 高带宽路径](../../../../RAM/wiki/05-dram-protocol-families/README.md) 和 memory-side compute 结合起来，面向 [LLM decode](../../07-workloads/llm-decode-and-cim.md) 这类 memory-bound 场景减少数据搬移。它和 CIM 的差异在于，AiM/AiMX 不依赖 DRAM cell 做 analog MAC，也不需要把 bitline 当累加器；它更像一套 memory-attached/vector-like offload 机制，重点是 command、controller、runtime 和 [BUS/host integration](../../../../BUS/wiki/README.md)。

AiMX 的风险也来自这个层级。prototype card 可以证明技术方向和 demo workload，但客户部署还需要稳定 SDK、host integration、编译/库支持、热设计、memory controller 策略和供应链计划。对 SK hynix 这样的 memory vendor，最关键的商业问题不是“能不能做出一个 PIM chip”，而是“是否能把它变成客户愿意在 server/accelerator 系统中长期支持的 memory product”。

主要风险：

| 风险 | 为什么重要 |
| --- | --- |
| prototype 到产品 | AiMX 公开口径是 prototype，不能等同 volume shipment |
| runtime/SDK | PIM offload 需要可维护的软件接口，否则客户难以迁移模型 |
| control hub | card-level 控制逻辑影响实际性能和可部署性 |
| workload fit | 对 memory-bound LLM/kernel 更有价值，对 compute-bound 算子收益有限 |
| memory ecosystem | GDDR/HBM 客户采购受容量、带宽、标准和供货约束影响 |

## 一句话理解

SK hynix AiM/AiMX 是 GDDR6 memory-side PIM，不是 CIM；它证明了 memory vendor 可以做 generative AI demo，但从 prototype 到客户部署仍隔着软件和系统集成。

## 产业启示

PIM 产品化必须跨过 memory component、card control、host runtime 和 workload library 四道门。AiMX 的产业价值在于展示 memory vendor 对 LLM memory bottleneck 的回应；它的产业风险在于没有成熟生态时，PIM 很容易停在 prototype/demo 层级。
