# SRAM-CIM 基础：6T/8T/10T Cell 怎么变成计算单元

上级：[02 Memory Technologies](./README.md)
相关：[SRAM-CIM 深入](./sram-cim-deep-dive.md), [Digital CIM 基础](../03-compute-paradigms/digital-cim-fundamentals.md), [RAM: 6T SRAM Cell](../../../RAM/wiki/02-sram-foundations/6t-cell-bistable-storage.md)

## 这页在回答什么问题

SRAM 原本是 cache、scratchpad 和 register file 的存储阵列，为什么能被改造成 CIM macro？关键不是“SRAM 离计算近”，而是让 cell、wordline、bitline 或 sense path 参与 bitwise operation、popcount、charge sharing 或 current accumulation。

## SRAM-CIM 的起点是片上存储已经存在

现代 SoC 本来就有大量 SRAM。RAM wiki 的 [SRAM array organization](../../../RAM/wiki/02-sram-foundations/sram-array-organization.md) 和 [scratchpad vs cache](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md) 已经说明，SRAM 的价值在于低延迟、高带宽、片上可控访问。SRAM-CIM 的动机是在这条既有数据路径上减少“读出到 MAC，再写回”的局部搬运。

普通 SRAM 路径是：

```text
WL select -> cell drives BL/BLB -> sense amp -> digital data -> MAC array
```

SRAM-CIM 试图把一部分操作提前到 array path：

```text
WL/input activation -> cell/BL interaction -> local logic or accumulation -> SA/ADC/accumulator
```

如果只是把 MAC 放在 SRAM macro 旁边，仍然是 near-memory 或 near-array acceleration，不是本 wiki 的 SRAM-CIM。必须有 cell、bitline、wordline、sense path 参与计算。

## 6T、8T、10T 的本质差异

6T SRAM cell 面积最小，适合高密度片上 SRAM，但读写和计算路径耦合强。要让 6T 同时承担存储和计算，设计必须避免读 disturb、half-select disturb 和 bitline 电压扰动破坏原数据。它适合做面积敏感的 bitwise 或低复杂度操作，但对多行同时激活和 analog accumulation 更紧张。

8T/10T 通过额外 transistor 拆出 read port 或 compute path。代价是 cell 面积上升，收益是读路径与存储节点更好隔离，可以更安全地做多行激活、bitline accumulation 或 local sensing。很多 SRAM-CIM 论文选择 8T/10T，不是因为 6T 不能算，而是因为稳定性和可测性比最小面积更重要。

## SRAM 更自然走 digital / mixed-signal

SRAM 的主流优势来自 CMOS 兼容和数字系统集成，因此 digital SRAM-CIM 更接近产品化路径。典型做法包括 bitwise AND/XNOR、bit-serial multiply、popcount 和 local digital accumulation。它牺牲一部分理想 analog 能效，换来确定性、验证可控和与数字 SoC 工具链的兼容。

Mixed-signal SRAM-CIM 使用 charge-domain 或 current-domain 局部求和，再通过 SA/ADC 或数字外围完成判决、校正和累加。它的收益来自把局部 reduction 压进 bitline 或电荷路径，代价是读出精度、噪声、ADC/SA 设计和 PVT 变化。

Pure analog SRAM-CIM 比 ReRAM analog MVM 不自然。SRAM cell 只稳定保存二值状态，multi-bit 权重需要多 cell、多周期或外围编码；一旦需要高精度 ADC，SRAM 的 CMOS 兼容优势会被外围面积和功耗稀释。

## SRAM-CIM 与普通 SRAM Buffer + MAC 的边界

判断一个设计是否是 SRAM-CIM，可以按这条线看：

| 设计 | 是否 SRAM-CIM | 原因 |
| --- | --- | --- |
| SRAM 旁边放 MAC array | 否 | cell/bitline 不参与计算 |
| SRAM read 出多个 bit 后在外围 popcount | 边界案例 | 如果 popcount 完全在外围，接近 near-array logic |
| 多行 WL 激活并在 BL/SA 路径形成 bitwise/accumulation | 是 | array path 参与计算 |
| 8T read port 执行 current-domain accumulation | 是 | read path 承担局部计算 |

这条边界会影响后续评价。真正的 SRAM-CIM 要额外承担 cell 稳定性和 read path 约束，但也更有资格声称减少 array-to-compute 搬运。

## 一句话理解

SRAM-CIM 是把片上 SRAM array 从“只读出数据”改成“在 read/bitline/sense 路径中完成局部计算”，它更自然走 digital 或 mixed-signal，而不是追求 ReRAM 式纯 analog MVM。

## 研究启示

SRAM-CIM 的研究开放问题不在“SRAM 能不能算”，而在能否同时满足 cell 稳定性、低外围开销、可验证精度和系统级利用率。产业实现更偏 digital/mixed-signal，因为这条路能沿用 CMOS、DFT、STA、SRAM compiler 和 SoC 集成经验；研究论文中更激进的 charge/current-domain 方案需要用 post-layout、silicon measurement 和 workload-level accuracy 证明外围没有吞掉收益。

