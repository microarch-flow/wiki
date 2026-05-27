# 权重到 Array 的映射：Tiling、Duplication、Folding

上级：[06 Software Stack](./README.md)
相关：[Dataflow Mapping](../05-architecture-and-system/dataflow-mapping-on-cim.md), [Memory Hierarchy with CIM](../05-architecture-and-system/memory-hierarchy-with-cim.md), [RAM: SRAM Array](../../../RAM/wiki/02-sram-foundations/sram-array-organization.md), [NoC: Reduction Networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)

## 这页在回答什么问题

权重矩阵放进 CIM array 时到底发生了什么？它不是简单 memcpy，而是受 array shape、cell capacity、bit encoding、signed representation、tile topology、write cost 和 error map 共同限制的 placement 问题。

## 三个基本动作

Tiling 把大矩阵切成符合 array shape 的块。切得太大，IR drop、variation、ADC range 或 SRAM bitline load 变重；切得太小，macro 数、NoC traffic 和 peripheral amortization 变差。

Duplication 复制权重以提高并行度或降低 activation broadcast。它适合高复用 fixed-weight inference，但会增加 on-array capacity 需求和 write/program 成本。

Folding 把一个逻辑矩阵分多轮映射到有限 array 上。它降低硬件容量要求，却增加 latency、activation 重放和 partial sum 合并。

Padding 处理 shape 与 array size 不整除的问题。padding 可以提高实现规则性，却会浪费 cell、降低 utilization，并让 partial sum merge 多出无效区域。

## 三条 Paradigm 的映射差异

Analog ReRAM/Flash CIM 更偏离线 weight placement。权重写入、verify、calibration 和 drift 会让频繁 remap 变贵；mapping 要感知坏列、conductance range、差分编码和 IR drop。

Digital SRAM-CIM 的权重更新更快，适合更动态的 tiling 和 bit-plane mapping。代价是 bit-serial cycle、accumulator width、array utilization 和 local buffer pressure。

Mixed-signal CIM 要同时映射数值和校正信息。权重位置、scale、ADC range、calibration table 和 tile-level accumulation 必须一致，否则模型层量化假设会失效。

SRAM buffer + MAC 不是 SRAM-CIM mapping。只有 cell、wordline、bitline、sense path 或紧邻 array path 参与 bitwise、popcount、charge/current accumulation 时，mapping pass 才是在映射 CIM；否则只是把权重放入 scratchpad，再由普通 MAC 执行。

## Mapping 失败的常见原因

第一，array utilization 高但 system utilization 低。矩阵块塞满 array，不代表 activation supply、partial sum reduction 和 fallback 边界高效。

第二，忽略 signed value 和 zero-point。differential pair、offset current、two's complement 和后处理会改变 cell 数、读出次数和 accumulator 宽度。

第三，忽略坏块和工艺分布。analog CIM 尤其需要 variation-aware mapping；digital CIM 也要处理 faulty bit、ECC/BIST 和 spare row/column。

## PIM/NMC 对照

DRAM/HBM/GDDR-PIM 不做本页意义上的 weight-to-array placement，而是把 kernel 或 command 映射到 bank/channel/device 内 processing unit。NMC 则把任务映射到 memory-adjacent accelerator；HBM base die、interposer 或 package-side compute 都属于这个边界，重点是数据放置、die-to-die/package bandwidth 和 host offload latency。

## 一句话理解

权重映射是把模型矩阵、物理 array 和系统数据流对齐的过程；tiling、duplication 和 folding 共同决定容量、并行度、误差与搬运成本。

## 工具链启示

mapping pass 必须读取 array shape、available cells、bad block map、encoding rule、write cost、buffer capacity 和 reduction topology。工具链不能只输出权重地址表，还要输出 padding policy、scale、calibration、partial sum plan 和 remap/fallback 策略。
