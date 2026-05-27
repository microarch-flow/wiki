# 模型适配与图划分

## 为什么“支持模型”不是一句空话

很多 `CIM` 方案都会说自己“支持 CNN”或“支持 LLM”，但这类表述往往过于粗糙。

更准确的问题应该是：

- 支持的是整个模型，还是其中一部分子图
- 加速的是主要瓶颈，还是只是某个容易映射的局部算子
- 为了把模型跑起来，系统是否需要频繁 fallback

因此，模型适配的核心不是证明“某个层能算”，而是判断：

1. 哪些部分真的值得放到 `CIM`
2. 哪些部分必须留在 host 或其他加速器
3. 划分后的 `hybrid execution` 是否仍然成立

## 先把模型适配看成三步

1. 识别模型中的 `CIM-friendly` 子图
2. 判断哪些部分必须 fallback
3. 评估划分后的系统代价

这三步里，最后一步最容易被低估。很多方案前两步都能做，但一旦算上数据往返和调度开销，收益就会显著缩水。

## 什么样的算子更适合 CIM

一般来说，更适合 `CIM` 的子图有几个共同特征：

- 结构规整
- 矩阵乘或向量乘占主导
- 权重复用率高
- 控制流简单
- 输入输出形状相对稳定

因此最常见的 `CIM-friendly` 对象是：

- `GEMM / MVM`
- `Conv` 中可规整映射的部分
- `Transformer` 里的 `projection / FFN`
- 某些 memory-bound 的 `KV cache` 相关路径

## 什么样的算子通常不适合直接放上去

通常包括：

- `softmax`
- `normalization`
- `sampling`
- 稀疏、不规则控制流
- 大量标量逻辑或分支

这些部分不是完全不能加速，而是更常见的现实是：

- 不适合 array-native 执行
- 即使能做，代价也可能高于收益
- 更适合留在 `CPU / GPU / NPU` 或传统数字单元

## 一个实用的判断标准

如果某个子图满足：

- 需要频繁跨步同步
- 中间张量很大
- 算子本身不规整
- 控制和归约远重于矩阵乘

那么它即使局部可映射，也未必值得映射到 `CIM`。

## 图划分到底在解决什么

`graph partition` 的本质，是在模型图里找到：

- 哪些部分放到 `CIM` 收益最大
- 哪些部分留在 host 更划算
- 哪些边界会导致最低的数据往返成本

这不是单纯的编译问题，而是系统优化问题。

## 三种常见划分粒度

### 1. Layer-level

优点：

- 简单
- 实现和验证成本低

缺点：

- 粒度粗
- 容易错过局部收益
- 某些层内部只有部分子图真正适合 `CIM`

### 2. Subgraph-level

优点：

- 更贴近真实部署
- 能把适合 `CIM` 的一段连续算子一起下沉

缺点：

- 编译和 runtime 复杂度上升
- 边界管理更难

### 3. Op-level

优点：

- 理论上最灵活
- 能更精细利用硬件特征

缺点：

- 最容易导致碎片化执行
- host 同步与数据搬运成本高

在真实系统里，很多产品化路线更可能停在 `layer-level` 或 `subgraph-level`，因为 `op-level` 很容易在系统上得不偿失。

## Hybrid Execution 为什么是常态

绝大多数 `CIM` 路线都不是“整模型独占执行”。

更现实的情况是：

- `CIM` 负责规整矩阵类子图
- `CPU / GPU / NPU` 负责控制、归约、归一化或不规则部分

这就意味着 `hybrid execution` 不是例外，而是默认状态。

真正的问题变成：

- 切换频率多高
- 张量在不同执行单元之间怎么流动
- 数据重排是否会吞掉收益

## 判断 Hybrid Execution 是否成立，要看三件事

### 1. 划分边界是否自然

如果 `CIM` 子图和 fallback 子图之间需要频繁来回跳转，那么理论收益通常很难落地。

### 2. 中间结果是否过大

有些算子本身计算不重，但中间张量很大。一旦来回搬运，系统收益会明显恶化。

### 3. Host 是否变成瓶颈

如果 host 需要频繁参与调度、同步和后处理，那么 `CIM` 的局部高效很可能换不来端到端收益。

## CNN：为什么它常常是最先跑通的

`CNN` 是很多早期 `CIM` 论文的主战场，不是偶然。

原因通常是：

- 卷积或其 lowering 后形态较规整
- 权重复用率高
- 数据流更容易设计
- 边缘场景与固定模型推理较匹配

但要注意：

- `Conv -> GEMM` 的 lowering 可能引入额外 buffer 成本
- `CNN benchmark` 容易掩盖现代 workload 已转向 `Transformer / LLM`

因此，`CNN` 跑通说明路线对规整工作负载有潜力，但不自动代表它对当前主流模型也成立。

## Transformer：不能按“一个模型”看

`Transformer` 必须拆成多个功能完全不同的模块来看。

更适合 `CIM` 的通常是：

- `Q / K / V projection`
- `FFN`

更需要谨慎的是：

- `attention score`
- `softmax`
- `normalization`
- `sampling`

这里最常见的误区是：

- 只展示 `projection` 或 `FFN` 的加速
- 然后把结论外推成“支持 Transformer”

这通常不够严谨。

## LLM：要把 Prefill 和 Decode 分开

### Prefill

特点：

- 大矩阵乘多
- batch 或 sequence 可能较大
- 传统 GPU / NPU 已很强

更该问的是：

- `CIM` 到底减少了哪一段系统成本
- 是算力占优，还是搬运占优

### Decode

特点：

- 每步工作量小
- 重复频繁
- `KV cache` 和 memory access 更显著

这时更值得看的不是“单次 GEMM 多快”，而是：

- `KV cache` 路径是否被优化
- host 和 memory-side 往返是否减少
- token latency 是否改善

## 不同 workload 的适配逻辑并不一样

## 1. Fixed-weight edge inference

通常更适合：

- `SRAM-CIM`
- 某些 `ReRAM-CIM`
- 小模型、规整图、固定权重路径

## 2. CNN-class workload

通常更适合：

- 规整卷积层
- 可复用权重较多的路径

## 3. Transformer / LLM

通常更适合局部切入，而不是整网替代。

更常见的切入点：

- `FFN`
- `projection`
- `KV cache`

## 4. 稀疏与不规则 workload

通常更难直接映射，因为：

- 控制流复杂
- 访问模式不规整
- fallback 和 host 协同成本更高

## 做模型适配时最该记录的字段

- 模型类别
- 目标子图
- fallback 子图
- 划分粒度
- 输入输出张量大小
- 权重是否常驻
- host 参与点
- 端到端收益口径

## 一个常见错误：只看“可映射”，不看“值不值得映射”

一个子图可以被切到 `CIM`，不代表它值得这样做。

至少还要继续问：

- 节省的是计算还是搬运
- 边界张量会不会太大
- fallback 是否会把收益吐回去
- 客户关心的是峰值算力，还是端到端延迟 / 能耗

## 读论文或公司材料时建议直接追问

1. 支持的是整个模型，还是某些层 / 子图？
2. 加速的是主瓶颈，还是只是最容易映射的一段？
3. fallback 的部分占总执行比例多高？
4. 指标是 kernel-level，还是 end-to-end？
5. `Prefill`、`Decode`、`KV cache` 是否被分开分析？

## 一个最实用的判断原则

如果一个方案声称“支持某类大模型”，但没有清楚说明：

- 哪些子图在 `CIM`
- 哪些子图仍在 host
- 图划分粒度
- 中间张量怎么流动
- 指标是否包含 hybrid execution 代价

那么它更可能是在证明“局部可加速”，而不是“模型已可有效部署”。

## 与本章其他页面的关系

- [编译器与 Runtime](./compiler-runtime.md)：更关注从模型到执行的编译与调度链
- [量化与映射](./quantization-mapping.md)：更关注位宽、量化与硬件误差约束

本页重点放在：

- 哪些模型和子图适合 `CIM`
- 图划分粒度
- hybrid execution 边界
- workload 级适配逻辑

## 后续可补充内容

- `CNN / Transformer / LLM` 子图划分示意图
- `prefill / decode` 适配比较表
- edge workload 与 data center workload 的划分差异
