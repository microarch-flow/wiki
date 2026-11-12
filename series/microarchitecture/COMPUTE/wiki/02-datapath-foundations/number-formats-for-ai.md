# AI 数字格式：位字段、块缩放与存储成本

上级：[02 · datapath 基础](./README.md)
相关：[位宽与乘法器](./quadratic-bitwidth-scaling.md)、[MAC 的输入与累加精度](./multiply-accumulate-from-gates.md)

## 格式如何影响计算与传输

格式定义数值编码；实现决定如何执行运算和搬运。INT 可按有符号补码或无符号码直接表示整数，不一定有量化参数。仿射量化另用 scale 和 zero-point 将整数码映射到实数，例如 `real = scale*(q-zero_point)`。浮点元素有符号、指数和尾数。低位宽可能减少数据量或部分乘法逻辑，但精度、缩放、累加、转换和数据布局也有代价。相同的标称位宽不保证相同动态范围或模型精度。

## 同位宽的指数与精度取舍

表中 `S/E/M` 分别是符号、指数和显式尾数位。“1 上方的间隔”列给出正数 1 到**其上方**下一个可表示正规数的间隔；它不是所有数值区间的绝对间隔。FP8 按 [OCP MX v1.0 表 2](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf)中的元素编码，不含共享 scale。

| 格式 | S/E/M | 1 上方的间隔 | 范围与特殊值 |
|---|---|---|---|
| IEEE FP16 | 1/5/10 | `2^-10` | 指数范围较 bf16 窄，支持 Inf、NaN |
| bf16 | 1/8/7 | `2^-7` | 指数范围接近 FP32；1 附近比 FP16 粗，支持 Inf、NaN |
| OCP FP8 E4M3 | 1/4/3 | `2^-3` | 最大有限正数 448；有 NaN，无 Inf 编码 |
| OCP FP8 E5M2 | 1/5/2 | `2^-2` | 最大有限正数 57344；有 Inf、NaN |

因此 FP16 与 bf16 同为 16 bit，前者在 1 附近更细，后者有更宽的指数范围。OCP E4M3 在 1 附近比 E5M2 更细，后者范围更宽。不同 FP8 变体和转换模式的特殊值、饱和与舍入规则可能不同；MX scale 还会影响块内最终值。数值模型要记录这些规则并验证误差、上溢和下溢；性能模型另行记录实现、带宽与指令能力，不能由字段表直接推出速度。

## MXFP4：元素指数和共享 scale 同时存在

[OCP Microscaling Formats v1.0，表 1](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf)定义 MXFP4 块：32 个 FP4 E2M1 元素共享一个 8-bit E8M0 scale。**每个元素仍是 4 bit 的 `S1/E2/M1`，其两位 exponent 没有被共享 scale 替代。**

忽略块布局填充、对齐和其他元数据时，一个完整 32 元素块：

```text
MXFP4     32 × 4 + 8 = 136 bit = 17 B = 4.25 bit/元素
裸 FP4    32 × 4     = 128 bit = 16 B = 4 bit/元素
裸 FP8    32 × 8     = 256 bit = 32 B = 8 bit/元素
```

因此 MXFP4 比同样打包的裸 FP4 多 1 B scale；它并不小于每元素名义 4 bit。以上裸 FP8 没计共享或其他 scale。若比较 MXFP8，则须按其块 scale、布局和元数据重新计数；真实张量还可能有尾块填充、对齐、缓存行或传输粒度。不同表示的精度及 scale 语义也不相同。

## 格式与吞吐不能只按位宽推导

部分积数量可以用整数乘法器 `p×q` 作结构估计；它不能直接推出浮点 MAC、整芯片面积或 FP4/FP8 的速度比。浮点要考虑指数、规格化、舍入与累加；同一硬件能否并行复用，还取决于 datapath、指令、scale 处理、带宽与编译映射。任何产品吞吐比较都须明确设备、格式、稀疏性、单位、频率及是否是峰值；没有普适的 2×、3× 或 4× 比例。

## 建模启示

```text
Format { element_type, element_bits, block_elems, scale_type, scale_bits,
         packing, alignment, tail_policy, accumulator_type }
```

按实际 block、有效元素、scale、对齐和接口粒度计算 `bytes`。分别配置该格式的运算支持、吞吐、转换延迟、能耗及数值误差。若实现未支持原生格式，还要计解码或转换。模拟器应报告各边界字节、计算事件与完成时间；不能从格式名称直接推断硬件性能。
