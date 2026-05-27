# PCM 和 MRAM 作为 CIM 介质：与 ReRAM 的异同

上级：[02 Memory Technologies](./README.md)
相关：[ReRAM 作为计算元件](./reram-as-compute-element.md), [Memory Tech Comparison Matrix](./memory-tech-comparison-matrix.md)

## 这页在回答什么问题

PCM 和 MRAM 都是非易失 memory，为什么它们不能简单并入 ReRAM-CIM？因为它们的状态变量、写入机制、可多值性、耐久和读出方式不同，导致适配的 compute paradigm 也不同。

## PCM：接近 analog multi-level，但写入和漂移重

PCM 通过材料相态改变电阻，理论上可以表达多级电导，因此适合 analog 或 mixed-signal CIM 研究。它与 ReRAM 一样可以把权重映射到 conductance，再用阵列电流做 MVM。

代价在写入和漂移。PCM programming 需要热过程，写能耗和延迟较高；相态随时间可能出现 resistance drift，多级状态越多，读出 margin 越紧。对固定权重推理，离线写入和校准可以被接受；对频繁更新、训练或动态模型，PCM 的写入和漂移会成为硬约束。

## MRAM：只有 read path 参与计算时才进入 CIM

MRAM 通过磁态保存信息，优势是非易失、耐久和与 CMOS 集成潜力。按 01 章 taxonomy，MRAM 只有在 cell/read path、sense path 或 array-level current/voltage behavior 参与 bitwise operation、comparison、accumulation 或 sensing-based compute 时，才进入 MRAM-CIM 讨论。

如果只是把 MRAM 当低泄漏非易失存储，再在旁边接数字 MAC、ALU 或 accumulator，那是 near-array compute 或 NMC-like 对照，不是 CIM。MRAM 不是不能做 analog/multi-level 研究，但它的主流优势不在稳定多级 analog conductance。把 MRAM 强行推向 ReRAM 式 analog MVM，可能会丢掉它在 endurance、retention 和二值可靠性上的优势。

## 与 ReRAM 的共性和差异

共性是非易失和靠近权重存储。三者都适合问：模型是否固定，写入频率多高，权重状态是否能长期保持，读出误差如何影响 accuracy。

差异是主导矛盾。ReRAM 的核心是 conductance variation、IR drop、sneak path 和 write/verify；PCM 的核心是 programming energy、resistance drift 和 thermal behavior；MRAM 的核心是二值可靠性、读写电流、面积和与数字逻辑的协同。

## Paradigm 映射

| Memory | Analog | Digital | Mixed-signal |
| --- | --- | --- | --- |
| PCM | 有 multi-level 潜力，但 drift 重 | 可做但不突出 | 更现实，用数字校正补偿 drift |
| MRAM | 不自然，除非特殊研究路线 | 只有 read/sense path 参与 bitwise compute 时才算 CIM | 若外围不属于 array path，则应归 near-array/NMC-like 对照 |
| ReRAM | 最自然 | 存在但削弱主要优势 | 主流研究落点 |

## 一句话理解

PCM/MRAM 不是 ReRAM 的同义替代：PCM 更像带漂移问题的 analog multi-level 候选，MRAM 更像可靠非易失 binary/digital 路线候选。

## 研究启示

PCM/MRAM for CIM 的研究价值在于扩展非易失 memory 的设计空间，但产业判断必须尊重 device 本性。PCM 需要证明 drift 和写入成本能被模型与系统吸收；MRAM 需要证明 read/sense path 参与计算后仍保留 non-volatility 和 endurance 优势，而不是只把普通 digital compute 换了存储介质。两者都更适合作为特定场景路线，而不是短期通用 CIM 主线。
