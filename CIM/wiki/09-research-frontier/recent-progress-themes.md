# 近期研究主题：超低比特、3D 集成 CIM、新型 Cell

上级：[09 研究前沿](README.md)
相关：[Paradigm × Memory Crossmap](../03-compute-paradigms/paradigm-memory-crossmap.md), [电路与 Macro](../04-circuit-and-macro/README.md), [应用负载](../07-workloads/README.md)

## 这页在回答什么问题

这页回答：近年的 CIM/PIM/NMC 研究为什么集中在低比特、mixed precision、新器件、3D/advanced packaging 和 LLM memory-bound workloads。

**低比特与 mixed precision** 是 SRAM-CIM 和 analog CIM 的共同方向。低比特降低 ADC/DAC、adder tree、bit-serial cycle 和 array energy；mixed precision 则承认不同 layer、不同 tensor、不同 token 阶段的精度敏感性不同。TSMC 16nm multi-mode gain-cell CIM macro 的研究价值就在这里：它不是只做 INT8，而是把 MX、INT、FP 多种格式拉进 CIM macro 内部，减少 system-to-CIM 的格式转换和数据搬移。

**新器件 CIM** 继续集中在 ReRAM、PCM、Flash、MRAM。ReRAM/PCM/Flash 的吸引力是非易失和高密度，适合固定权重推理；难点是 conductance drift、retention、write-verify、endurance 和 array 非理想性。东大 2025 ReRAM CiM work 的研究价值不是“ReRAM 已经产品化”，而是把多值存储、10 年保持和 MAC compensation 放在同一个问题里处理。

**3D 集成与 advanced packaging** 是两条路线的交汇点。CIM 研究希望把 memory arrays、logic、ADC/SA、local reduction 贴得更近；PIM/NMC 研究希望利用 HBM stack、base die、interposer、chiplet 和 CXL-like expansion 近数据计算。这些问题与 [FAB wiki 的 HBM/3DIC/advanced packaging](../../../FAB/wiki/README.md) 强相关，研究难点从单 macro 能效扩展到热、TSV、die-to-die link、test 和 yield。

**LLM 与 Transformer workload** 改变了研究重心。CNN 让 CIM 擅长的 weight-stationary matrix/vector compute 很自然；LLM decode 则把 KV cache、attention、embedding、activation movement 和 batch-size sensitivity 推到前台。CIM 研究开始讨论哪些子图适合 array-resident weights，PIM/NMC 研究开始讨论 HBM/GDDR/near-data offload 能否降低 memory-bound 阶段的 energy/byte。

**工具链与建模** 正在变成研究对象本身。CIM 论文不能只给电路指标，还要说明 mapping、quantization、noise-aware training、fallback、runtime scheduling 和 system-level modeling；PIM 论文要说明 command model、host offload ratio、kernel library 和 synchronization。没有这些，研究结果很难进入架构探索或产品评估。

## 一句话理解

近期研究从“证明存内能算”转向“证明它在精度、可靠性、封装、软件和真实 workload 下仍然有收益”。

## 研究启示

未来高质量工作会越来越跨层：device paper 要解释模型精度，macro paper 要解释 data movement，architecture paper 要解释电路约束，software paper 要解释硬件非理想性。只在单层给漂亮数字的论文，研究参考价值会下降。
