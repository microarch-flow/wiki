# 模型适配：Noise-Aware Training、QAT、Retraining

上级：[06 Software Stack](./README.md)
相关：[Reliability and Error Tolerance](../05-architecture-and-system/reliability-and-error-tolerance.md), [Quantization for CIM](./quantization-for-cim.md), [BUS: DMA Path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md), [NoC: Reduction Networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)

## 这页在回答什么问题

模型适配在 CIM 中解决什么问题？它不是为了让硬件误差“看起来没事”，而是把可建模的量化误差、analog noise、device variation 和 mapping mismatch 纳入训练或校准闭环。

## 三类适配

QAT 把低比特量化纳入训练，使模型学习 scale、rounding 和 saturation 的影响。它适合 digital CIM，也适合 mixed-signal CIM 的数字校正段。

Noise-aware training 把硬件噪声、ADC quantization、conductance drift、SA offset 或 tile mismatch 注入训练。它更贴近 analog/mixed-signal CIM，但要求误差分布可测、可复现、可稳定建模。

Retraining 或 fine-tuning 在实际 mapping 后重新调整模型。它可以补偿坏块、tile 差异和特定 calibration 状态，但会增加部署流程复杂度和客户导入成本。

Layer sensitivity analysis 决定哪些层值得低比特、哪些层需要保留更高精度，哪些层应直接 fallback。没有 sensitivity 分析，QAT 容易把全模型压到一个不适合硬件和任务质量的统一位宽。

## 三条 Paradigm 的适配差异

Analog CIM 对模型适配依赖最重。ReRAM/Flash/PCM 的 drift、write variation 和温度敏感性会让一次性 QAT 不够，工具链需要支持 hardware-in-the-loop 或 silicon-profile-aware adaptation。

Digital CIM 主要适配 bit-width、bit-serial accumulation 和 overflow/saturation。它的误差更稳定，很多场景可用标准 QAT 加少量硬件约束完成。

Mixed-signal CIM 需要同时适配 analog 局部误差和 digital correction。scale、calibration、tile health 和 retry/fallback 策略都可能进入训练配置。

模型适配还必须和 graph partition 绑定。GEMM/MVM、Conv、projection 和 FFN 更适合 CIM；attention score、softmax、normalization、KV cache 管理和 sampling 要单独评估。声明“支持 Transformer/LLM”没有意义，必须说明哪些子图在 CIM，哪些在 CPU/GPU/NPU/PIM/NMC fallback，以及边界 tensor transfer 和 host synchronization 成本。这里的 PIM 指 DRAM/HBM/GDDR memory-side processing；HBM base die、interposer 或 package-side compute 属于 NMC，fallback 到这些目标时要重新计算 DMA、NoC/reduction 和 host synchronization。

## 适配边界

模型适配只能吸收稳定、统计可描述、部署时仍成立的误差。随机 aging、极端温度、retention 失效、写入失败和不可预测 host fallback 不能靠训练完全解决。

因此，适配工具必须和 silicon measurement、calibration flow、runtime health monitor 相连。FAB wiki 的 [final test methodology](../../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md) 提醒我们，产品级误差模型来自测试与筛选，不是只来自仿真。

## 一句话理解

CIM 模型适配的价值在于把硬件误差变成训练可见、部署可验证的约束；不可测或会漂移的误差不能被软件魔法消除。

## 工具链启示

训练/部署工具链需要统一保存 hardware profile、noise model、calibration version、tile health、layer sensitivity、QAT recipe 和 validation result。graph partition 的收益必须扣除 fallback、tensor transfer、host synchronization 和 format conversion。runtime 若发现温度、漂移或坏块超出训练假设，必须能触发 remap、fallback 或重新校准。
