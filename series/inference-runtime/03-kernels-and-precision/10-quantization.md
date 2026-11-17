# 低精度执行：权重、激活与 KV 的不同代价

<div class="inference-legacy-anchors" aria-hidden="true"><span id="10-量化权重-激活-kv-quantization"></span></div>

上级：[本专题导读](README.md)

低精度改变的不只是“每个数占几个字节”。权重、激活与 KV 的生命周期和使用方式不同，必须分别分析其容量、执行路径和误差。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="格式与字节"></span><span id="2-三个旋钮打三个项回写-01"></span></div>

## 三种精度分别作用于哪里

| 对象 | 主要变化 | 还需检查 |
|---|---|---|
| 权重，$p_w$ byte/元素 | 常驻容量与读取载荷 | 打包、缩放参数、预排布、解量化内核 |
| 激活，$p_a$ byte/元素 | 中间存储与可用矩阵乘路径 | 校准、离群值、累加精度、转换 |
| KV，$p_{kv}$ byte/元素 | 请求状态容量与 Attention 读写 | 缩放粒度、误差累积、缓存兼容性 |

W4A16 表示权重采用约 4 bit 的有效编码、激活采用 16 bit；实际文件和显存字节还包含元数据与对齐。FP8 也存在不同编码，不能只按位宽推断范围和数值行为。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="权重量化weight-onlyw4a16awq-gptq"></span></div>

## 权重量化的执行路径

权重量化可以减少装载和读取成本。内核可能在使用前将低比特权重转换为计算格式，也可能使用支持的低精度计算路径。

AWQ 与 GPTQ 是不同的权重量化方法。理解运行时首先需要知道权重布局、分组和缩放格式，以及是否有匹配内核；不必在这里重复全部离线优化算法。

权重读取占主导时，压缩可能有明显收益。若转换代价较高、形状不合适，或其他资源已成为限制，收益会减小。也不能反过来断言权重量化对 Prefill 必然没有帮助。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="权重激活量化w8a8fp8-smoothquant"></span></div>

## 权重与激活共同量化

低精度矩阵乘能否使用，取决于硬件、内核、布局和模型精度要求。峰值规格翻倍只改变理论资源上界，不保证完整 Prefill 时间减半。

激活分布可能随层、输入和 token 位置变化。校准集合应覆盖目标任务；离群值处理、缩放粒度和累加精度都会影响质量与成本。某些算子保留较高精度，转换边界仍然存在。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="kv-量化p_kvfp8-int8-int4-kv"></span><span id="量化与公式-quantification"></span><span id="1-精度档表llama-3-70bp70e9textkv_texttoktextfp16320-kib"></span></div>

## KV 量化怎样影响内存

对[标准全注意力 KV 模型](../01-request-and-metrics/01-prefill-decode.md)，有效载荷与 $p_{kv}$ 成正比。示例中 16 bit KV 为 320 KiB/token，8 bit 有效载荷为 160 KiB/token。

假设固定 KV 预算为 10 GiB，每条请求保存 4,096 个位置，忽略块尾部和元数据。16 bit 时每条为 1.25 GiB，可放 8 条；8 bit 时为 0.625 GiB，可放 16 条。这个构造例子只证明固定池中有效载荷的容量比例。

整个服务能否获得两倍并发，还受权重、工作区、增长预留和执行速度限制。读流量减半也不能直接推出 ITL 减半。解量化、缓存命中和其他算子可能占据剩余时间。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="3-回写各篇这就是牵一发"></span><span id="4-质量代价有损必须实测"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 质量与性能要成对验证

固定模型修订、量化产物、框架、内核、输入分布和生成参数，再同时记录：

- 目标任务质量，以及长上下文、结构化输出等关键子集。
- 加载后与峰值内存；权重、KV 和工作区分别计数。
- 冷／热状态下的 TTFT、ITL、吞吐与失败率。
- 是否发生回退，以及量化前后的执行计划是否相同。

“某个公开基准接近原精度”不能替代目标任务验证。量化也不是唯一可能改变结果的优化；近似注意力和某些候选接受策略同样需要说明性质。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="延伸阅读-references"></span></div>

## 来源与关联

[AWQ](https://arxiv.org/abs/2306.00978)、[GPTQ](https://arxiv.org/abs/2210.17323)和 [SmoothQuant](https://proceedings.mlr.press/v202/xiao23c.html)分别说明相应方法。这里的字节算例是条件计算，不是它们的实测结果。

精度改变后应重算[内存预算](../04-state-and-memory/runtime-state.md)、[Attention 内核](05-attention-kernels.md)和[条件算例](../09-measurement-and-cases/15-quantitative-estimation.md)，不能只替换一个统一精度参数。
