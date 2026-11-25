# 非理想性总览：Noise、Mismatch、Variation、Retention

上级：[电路、外围与计算宏](./README.md)
相关：[同一个输入的重复读出](../03-compute-paradigms/analog-cim-deep-dive.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md), [FAB: Process Nodes and PPA](../../../chip-development/FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

为什么 CIM 的难点不是“电路会有误差”这么简单？因为误差会从 device、array、peripheral、calibration 和模型层逐级传播，最终决定 macro 指标能否变成可部署 accuracy。

## 误差分层

| 层级 | 典型误差 | 影响 |
| --- | --- | --- |
| device | ReRAM conductance variation、Flash threshold drift、PCM resistance drift、SRAM Vt mismatch | weight state 和读出分布 |
| array | IR drop、sneak path、line resistance、coupling、read disturb | 大阵列 MVM 偏差和行列不均匀 |
| circuit | SA offset、ADC quantization、DAC mismatch、reference noise、thermal noise | 判决、量化和有效位数 |
| temporal | retention、aging、temperature drift、write noise | 校准失效和长期稳定性 |
| system | mapping mismatch、tile reduction error、model sensitivity | 最终 accuracy 和重训练成本 |

### 读数从 23 变成 26，先量哪一段？ {#trace-weight-error}

先记住这列的标定：每个点积单位对应 0.2 µA。低位窗只打开第二行，高位窗把两行都打开。在这个教学例中，第二行单元的电导从目标 50 µS 写到了 56 µS。两次选通都加 20 mV，因此两个窗各多出 0.12 µA。低位列电流从 1.00 变到 1.12 µA，高位从 1.80 变到 1.92 µA。按最近码舍入，两窗各多报一个码。高位码在数字端乘 2，所以结果共多出 3。

只看到最后的 26，还不能断定单元写偏了。可以先只开第一行，看另一条支路是否也有偏差，再用已知参考电流直接激励读出链，跳过单元和行线。下面这张图只改变第二行电导，把两个 ADC 判决分别画出。想比较另外两种也能产生 26 的原因，可以顺着相同的两个观察点做对照。[逐次读数与对照实验](../03-compute-paradigms/analog-cim-deep-dive.md#repeat-read)

<figure class="micro-diagram" tabindex="0" aria-label="第二行写偏时，低位与高位的电流分别越过各自的判决门槛" markdown="1">

![同一处写入偏差让两次读数分别跨过 1.10 与 1.90 µA 的门槛。两个码都增加 1，按位权合并后结果增加 3。](../03-compute-paradigms/img/analog-error-readout.svg)

<figcaption>与模拟求值深入篇共用此图。两次转换采用相同刻度。最终误差由两次判决及各自的位权共同决定。</figcaption>
</figure>

## 三条 Paradigm 的误差形态

Analog CIM 把误差放进数值路径本身。ReRAM/Flash 的 conductance 或 threshold 不稳定会直接变成 MAC 误差；SRAM charge/current-domain 路线会受 PVT、leakage、bitline mismatch 和 sense margin 影响。

Digital CIM 的误差更接近传统数字设计：timing violation、read disturb、soft error、faulty bit、popcount 或 accumulator bug。它仍需要 BIST、ECC、redundancy 和 corner signoff，但误差更容易离散建模。

Mixed-signal CIM 最复杂，因为 analog 误差和 digital correction 同时存在。校准可以降低 bias，却会引入存储、时间、能耗和软件模型复杂度；如果误差分布随温度或时间漂移，离线校准会失效。

## Memory Technology 的差异

SRAM-CIM 的主要风险是 read disturb、half-select disturb、multi-row activation、PVT、sense margin、bitline coupling、timing closure 和外围面积。ReRAM-CIM 的风险从 device 开始：forming、write variation、conductance drift、IR drop 和 sneak path。Flash-CIM 要面对 threshold drift、program variation 和 retention。PCM 的 resistance drift 是核心难点；MRAM 若做 read/sense-path compute，则重点是 read current、read/write disturb、sense margin、TMR variation 和 sense offset。

DRAM/HBM/GDDR-PIM 也有 DRAM refresh、retention、timing 和 PHY 问题，但它们不属于本页 CIM macro 非理想性主线；PIM 更关心 memory command、bank conflict、thermal 和 host offload。

## 校准的代价

校准不是免费按钮。它需要 reference、测试向量、存储校准参数、运行时更新策略和模型侧适配。缩短物理线长可降低 I·R 压降和线长相关的空间误差，但器件固有阈值/电导失配不会仅因切分而重抽或自动变小；切分还可能增加 ADC、buffer、controller 和归并开销。写入偏差在 program/verify 时产生并持续到下次写入，不应当作每读一次的新噪声。差分编码可抑制 common-mode error，却把 cell 数翻倍或增加读出次数。

## 一句话理解

CIM 非理想性是从 device 到模型的误差传播问题；analog/mixed-signal 路线尤其需要把误差预算当成架构对象，而不是电路脚注。

## 研究启示

研究应报告误差源、误差分布、是否可校准、校准频率、温度/老化条件和模型 accuracy 影响。产业实现更需要硅后统计和量产测试方法；没有 corner、retention 和 calibration cost 的 accuracy 数字很难说明产品价值。
