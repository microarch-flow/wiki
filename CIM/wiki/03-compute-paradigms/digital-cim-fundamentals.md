# Digital CIM：Bitwise Compute 与 SRAM 阵列的结合

上级：[03 Compute Paradigms](./README.md)
相关：[Digital CIM 深入](./digital-cim-deep-dive.md), [SRAM-CIM 基础](../02-memory-technologies/sram-cim-foundation.md), [RAM: SRAM Applications](../../../RAM/wiki/03-sram-applications/README.md)

## 这页在回答什么问题

Digital CIM 为什么更接近工程落地？因为它把计算限制在离散 bit、logic、popcount 和确定性累加路径里，牺牲一部分理想 analog 能效，换来可验证、可综合、可测试和可集成。

## Digital CIM 的基本形式

Digital CIM 不是“SRAM 旁边放 MAC”。按 01 章 taxonomy，只有 cell、read bitline、wordline、sense path 或紧邻 array path 参与 bitwise operation、popcount、bit-serial multiply 等计算时，才进入 CIM。普通 SRAM buffer + 外围 MAC 仍然是 memory-adjacent accelerator，不进入 CIM。

典型路径是：

```text
input bits
  -> WL / read path activation
  -> SRAM cell / BL / SA 产生 bitwise 结果
  -> popcount / local accumulator
  -> multi-bit digital accumulation
```

## 主要落在哪些 memory 上

SRAM 是 digital CIM 的主战场，因为 SRAM 和数字逻辑同属 CMOS 流程，read path、sense amp 和外围控制可以被工程化修改。MRAM 只有在 read/sense path 参与 bitwise compute、比较或局部归约时才可作为 digital-like CIM 研究对象；如果 MRAM 只是权重存储旁接数字 MAC，就不算 CIM。

ReRAM/Flash 也能做 digital CIM，但这会削弱它们多状态 analog 权重和 array-native summation 的核心优势。若把 ReRAM/Flash 只当 NVM 存权重，再把计算交给外围数字逻辑，read path、sense path 和 multi-level state 没有参与 compute，方案会退化为 NVM + accelerator。若强行做数字读写，endurance、write-verify、sense margin 和外围编码会吃掉密度收益。

DRAM/HBM/GDDR-PIM 可以有 digital processing unit，但那属于 PIM，不属于本章 digital CIM。边界在于：PIM 的数字单元是 memory die/bank 上的独立 processing block；digital CIM 要求 cell、bitline、wordline、sense path 或紧邻 array path 本身参与计算。

## 为什么 digital 不等于低价值

Digital CIM 的收益来自减少 read-out 和局部数据搬运，而不是把乘加变成物理连续量。它可以更稳地支持 INT4/INT8、bit-serial expansion 和 deterministic accumulation。对产品来说，确定性精度、DFT、时序收敛和软件可预测性经常比理论 TOPS/W 更重要。

代价是面积和周期。bit-serial 会把多比特乘法展开成多个周期；bit-parallel 会增加 cell、wire 和 local logic；popcount 和 accumulator 会占据阵列外围面积。Digital CIM 的核心问题是：这些新增数字逻辑是否仍比读出到外部 MAC 更便宜。

## 一句话理解

Digital CIM 是把离散逻辑和局部累加推进到 SRAM 等 array path 中，用工程可控性换取不那么激进但更可部署的近数据计算收益。

## 研究启示

Digital CIM 的研究应证明它不是“普通 MAC 拆碎贴到 SRAM 旁边”。关键证据包括 array path 参与计算的位置、与 SRAM buffer + MAC baseline 的公平比较、bit-width 扩展代价、DFT/时序可行性和真实模型映射。产业上，这条路线比 analog CIM 更适合作为 SRAM-CIM 商业化第一步。
