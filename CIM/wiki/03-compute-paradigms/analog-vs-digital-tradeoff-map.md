# Analog vs Digital：能效、精度、可扩展性、工程可实现性的全景对比

上级：[03 Compute Paradigms](./README.md)
相关：[Analog CIM 基础](./analog-cim-fundamentals.md), [Digital CIM 基础](./digital-cim-fundamentals.md), [Mixed-Signal CIM](./mixed-signal-cim.md)

## 这页在回答什么问题

Analog vs digital 不是“能效 vs 精度”这么简单。真正的取舍由 memory technology、目标位宽、ADC/DAC、模型容错、工艺节点、校准成本、软件栈和产品场景共同决定。

## 维度一：能效来源

Analog CIM 的能效来自省掉局部数字乘法器和加法树，让电流、电压或电荷自然完成乘加。这个优势在低精度 MVM 中最明显，尤其是 ReRAM/Flash 这类 cell 状态能表达权重的 memory。

Digital CIM 的能效来自减少 array read-out 和局部搬运，而不是消除数字计算。它仍然需要 logic、popcount、accumulator，但可以避免把每个 bit 都搬到远端 MAC array。

真实边界在 ADC。低比特 analog 可能更强，高比特 analog 会被 ADC、DAC、reference 和校准稀释。一个 4-bit column ADC 在小 macro 中可能占掉约 30-60% macro 能耗或面积预算；8-bit ADC 的比较次数、参考精度和布局开销会更快上升，常常足以抵消理想 crossbar MVM 的能效优势。Digital 的峰值不如理想 analog 激进，但面积和能耗增长更可预测。

## 维度二：精度与可扩展性

Digital CIM 的精度由 bit-width、bit-serial 周期和 accumulator 宽度决定，扩展路径清楚，代价是面积和周期。Analog CIM 的有效精度受 ADC bit、noise、variation、IR drop、temperature 和 calibration 共同限制；8-bit 等效精度远难于 4-bit 级低精度演示。

因此，低比特 CNN、binary/ternary network 和固定模型 edge 场景更利于 analog/mixed-signal；INT8/FP8 甚至更高精度要求更利于 digital 或强 digital correction 的 mixed-signal。

## 维度三：工程可实现性

Digital CIM 更接近标准数字 SoC 流程，DFT、STA、formal、timing closure 和软件调试都更熟悉。Analog CIM 需要 device characterization、PVT corner、calibration、reference design、ADC/DAC layout 和模型级误差补偿，工程难度高一个层级。

这解释了为什么 SRAM-CIM 商业化更偏 digital/mixed-signal，而 ReRAM/Flash analog CIM 更常停在研究样片、专用 edge 产品或 startup 尝试。

## 维度四：工艺节点

Digital CIM 能更直接跟随先进 CMOS 节点。Analog CIM 不一定从先进节点受益，因为低电压、device mismatch、噪声和 analog headroom 会变得更难。Mythic 等 Flash analog CIM 选择成熟节点，是在用工艺稳定性和 analog 友好性换取低功耗固定模型路线。

## 维度五：可重构性与动态权重

Digital CIM 更适合频繁切换模型、动态 sparsity、可变 bit-width 和在线更新，因为权重和 partial sum 都以离散状态管理。Analog CIM 更适合固定权重或低频更新场景；ReRAM/Flash/PCM 的写入、verify、drift 和 endurance 会让动态权重成本明显上升。

## 维度六：可靠性与误差容忍

Analog CIM 需要 workload 能吸收噪声、variation 和量化误差，或者通过 QAT、calibration、redundancy 把误差关进预算。Digital CIM 的错误更多表现为 timing、fault、soft error 或设计 bug，虽然仍需 ECC、BIST 和 DFT，但 worst-case 建模更接近传统 SoC。面向车载、工业和长寿命边缘设备时，可靠性经常比 peak TOPS/W 更早决定路线。

## 决策表

| 场景 | 更合适路线 | 原因 |
| --- | --- | --- |
| 低比特固定权重 edge inference | analog / mixed-signal | 能容忍误差，重视 energy per inference |
| 可量产 SRAM-CIM SoC | digital / mixed-signal | CMOS 集成、验证和软件更稳 |
| ReRAM crossbar 研究 | analog / mixed-signal | conductance MVM 是核心价值 |
| INT8/FP8 主流推理 | digital 或强校正 mixed-signal | 精度、可重复性和工具链更重要 |
| LLM decode memory-side | PIM/NMC，不按本表直接判断 | 瓶颈在 memory-side access，不是 CIM macro paradigm |

## 常见误解

常见误解：analog 一定比 digital 省电。实际上，只有在低精度、外围计入后仍受益、且模型能吸收误差时才成立。

常见误解：digital CIM 只是妥协。实际上，digital CIM 用可验证性和确定性换取产品路径，在 SRAM-CIM 中是强路线。

常见误解：mixed-signal 能取两者优点。实际上，边界设计不好时，它会同时继承 analog 的校准成本和 digital 的面积开销。

## 一句话理解

Analog vs digital 的边界不是信仰问题，而是低精度能效、有效精度、工艺、校准、软件和产品风险共同决定的工程选择。

## 研究启示

当前研究前沿在三个方向：极低比特 analog 的极致能效、数字 CIM 的 INT8/FP8 可扩展实现、以及 mixed-signal macro 的边界优化。产业状态更偏数字和 mixed-signal，因为客户要的是可部署精度和可验证系统，而不是单个 array 的理想能效。
