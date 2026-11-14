# DDR1 到 DDR5：接口与组织的演进

上级：<span id="ddr1-到-ddr5每一代的核心改变是什么"></span>[DRAM 命令与接口](./README.md)

相关：[双沿传输](./why-double-data-rate.md) · [DRAM 接口家族比较](./ddr-lpddr-gddr-hbm-tradeoff-map.md)

## 这页在回答什么问题

DDR1 到 DDR5 每一代的核心改变是什么？下面着重比较接口和组织，具体速率、电压、命令、模块和可靠性功能要按标准与产品核对。

## 接口速率与阵列组织的演化

| 代际 | 值得关注的方向 |
| --- | --- |
| DDR | 双沿数据传输；以目标器件的时钟、burst 和组织为准。 |
| DDR2 | 提高接口速率，并调整内部预取、供电和接口机制。 |
| DDR3 | 采用 8n 预取，继续提升数据率，并使用新的电压和协议配置。 |
| DDR4 | 保留 8n 预取，引入 bank group 等组织和时序差异；配置影响可用并行度。 |
| DDR5 | 采用 16n 预取，模块接口和刷新等机制进一步变化；器件可包含 on-die ECC。 |

[Micron 的 DDR 产品资料](https://www.micron.com/content/micron/us/en/products/memory/dram-components/ddr5-sdram.html)列出 DDR4 的 8n 与 DDR5 的 16n 预取；[DDR4 常见问题](https://www.micron.com/sales-support/sales/faqs)说明 DDR4 相对 DDR3 提高数据率时并未把预取从 8n 加倍。预取和实际 burst 的关系仍要按模式检查。

以非 ECC DIMM 的典型配置说明接口分段：[Micron DDR5 技术说明](https://my.micron.com/content/dam/micron/global/public/products/white-paper/ddr5-new-features-white-paper.pdf)比较了 DDR4 的一个 64-bit 数据通道和 DDR5 的两个 32-bit 子通道。DDR4 BL8 为 `64 × 8 / 8 = 64 B`；DDR5 每个子通道 BL16 为 `32 × 16 / 8 = 64 B`。子通道可独立处理请求，但同子通道内部仍共享资源，控制器上游也可能共享。ECC 位、其他 burst 模式及具体模块另计。

数据率提高不等于每笔访问的绝对延迟同比下降。DDR5 器件内部 ECC 也不能直接替代系统 ECC；两者保护范围不同，见[DRAM 可靠性](../foundations/dram-reliability-retention-rowhammer-ecc.md)。代际之间的物理兼容性和模式不能仅凭相似的命令名称推断。

## 一句话理解

DDR 演进同时改变接口速率、器件组织和协议；比较时必须固定代际、模块和模式。

## 建模启示

针对每代分别配置 channel/子通道、bank 组织、burst、刷新和时序。以相同流量与资源边界比较有效性能，不把每代引脚速率直接当成请求延迟。
