# Bank group、prefetch 与 burst：组织和传输粒度

上级：<span id="bank-groupprefetchburst高频接口下的必然演化"></span>[DRAM 单元与阵列](./README.md)

相关：[双倍数据速率](../protocols/why-double-data-rate.md) · [DDR 代际演进](../protocols/ddr-generation-evolution.md)

## 这页在回答什么问题

Bank group、prefetch 和 burst 分别限制什么？三者有关联，却不是同一个参数，也不是所有 DRAM 都必须采用相同组织。

## 阵列与高速接口之间的速率匹配

**Prefetch** 在较慢的内部访问与较快的外部引脚之间组织并行数据；具体深度和内部路径依器件。**Burst length（BL）**是一次列操作在外部接口上的数据传输次数；有些模式还支持 burst chop，因此不能把 prefetch 深度与每次外部 BL 无条件画等号。

例如 x64 数据接口、BL8：每次 64-bit transfer，共 `64 × 8 / 8 = 64 B`。DDR 每 CK 传两次，数据传输占 4 CK；已经使用外部宽度和 BL，不再额外乘 prefetch 倍数。

**Bank group** 将 bank 归组，一些间隔对同组和跨组命令不同。假设某 DDR4 模式同组列命令间隔 `tCCD_L = 8 CK`、跨组 `tCCD_S = 4 CK`，且其他约束均已满足：四次同方向命令可分别在 `0、8、16、24` 或 `0、4、8、12` CK 发出。后者还要求适当分配 bank group，且 BL8 的四段 DQ 不重叠。数字只是构造示例，不是产品规格；方向切换、行状态及其他时序都可能增加空隙。

## 一句话理解

Prefetch 描述内外速率衔接，burst 描述外部传输粒度，bank group 影响部分命令的间隔。

## 建模启示

分别保存内部组织、有效 BL、bank group 和 DQ 占用；不要仅凭 bank 数或名义数据率推导有效带宽。
