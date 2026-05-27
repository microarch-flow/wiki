# 指标与术语表

## 这页的作用

后续所有页面尽量复用这里的定义，减少同一术语在不同页面里含义飘移。

更具体地说，这一页主要解决四类问题：

- 同一个词在不同页面里是不是在说同一件事
- 一个性能或能效数字到底属于哪个层级
- 不同论文和公司材料里的口径能不能直接比较
- 读笔记时该补哪些最小必要字段

因此，本页最好被当成：

- 术语定义页
- 指标口径页
- 研究记录的最小规范页

## 一条最重要的原则

任何性能、能效、容量、精度数字，如果没有说明：

- 层级
- 精度条件
- workload
- 是否包含外围
- 数据来源

那它的可比较性通常都很弱。

## 一. 层级相关术语

### Cell-level

指标只覆盖：

- 单个 bitcell
- 单个器件
- 或局部最小计算单元

它更适合证明物理机制或电路机制，不适合直接推导系统价值。

### Macro-level

指标只覆盖一个局部阵列宏，通常不包含完整 chip 的互联、控制和外部存储访问。

使用时要补充：

- 是否包含 `ADC / DAC / SA`
- 是否包含局部 buffer
- 是单宏仿真、post-layout 还是 silicon

### Tile-level

指标覆盖一个由多个宏、局部 buffer 和控制逻辑组成的更大执行单元。

这一层比 `macro-level` 更接近系统真实执行单元，但通常还没包含整颗芯片的全局开销。

### Chip-level

指标覆盖整颗芯片，包括主要片上互联、全局 buffer、调度和控制结构。

使用时要继续确认：

- 是否包含外部 DRAM / HBM 访问
- 是否包含 host interface
- 是否来自真实 workload

### System-level

指标覆盖端到端部署环境，可能进一步包含：

- host
- 外部内存
- runtime
- driver
- 真实 workload 和系统协同

这一层最接近客户实际感知。

## 二. 性能与能效术语

### TOPS

每秒万亿次操作，通常用于整数、低比特或专用算子吞吐描述。

使用时至少要确认：

- operation 的定义是什么
- 是否把 `MAC` 算成 1 op 还是 2 ops
- 是峰值还是有效吞吐

### TOPS/W

每瓦每秒万亿次操作，常用于整数或低比特运算能效描述。

使用时要补充：

- 操作定义是什么
- 是否包含外围和数据搬运
- 是峰值、仿真、post-layout 还是实测

### TFLOPS/W

每瓦每秒万亿次浮点操作，更多出现在浮点或研究级对比中。

使用时要确认：

- 精度格式是什么
- 是否把低比特操作换算成浮点等价值

### Peak Throughput

理论峰值吞吐，通常假设：

- 阵列满载
- 数据持续供给
- 无 stall
- 无额外系统争用

它适合看上限，不适合直接代表真实部署表现。

### Effective Throughput

真实有效吞吐，通常已经受：

- 数据搬运
- 调度
- stall
- fallback
- host 协同

影响。

对系统判断来说，它通常比 `peak throughput` 更重要。

### Energy per op

单次操作平均能耗。

使用时要继续确认：

- op 的定义是什么
- 是否包含外围
- 是 `kernel-level` 还是 `system-level`

### Energy per byte moved

每搬运一个字节的数据成本。

这个指标在：

- `PIM`
- `near-memory`
- `LLM decode`
- `KV cache`

等 memory-bound 场景里尤其重要。

### Area Efficiency

单位面积吞吐，常见写法如：

- `TOPS/mm^2`
- `GOPS/mm^2`

使用时必须确认：

- 面积是否只算阵列
- 是否包含 `ADC / DAC / buffer / controller`
- 是 layout 面积还是估算面积

### Utilization

资源利用率，常见可细分为：

- `array utilization`
- `tile utilization`
- `chip utilization`

低利用率通常意味着理论峰值很难兑现。

### Latency

完成一次任务、一次推理步或一次 kernel 的时间。

对 `LLM` 特别要分清：

- 单 kernel latency
- 单 token latency
- end-to-end request latency

## 三. 瓶颈与系统行为术语

### Memory-bound

系统瓶颈主要来自带宽、访存延迟或数据搬运，而不是纯计算吞吐。

### Compute-bound

系统瓶颈主要来自计算单元吞吐，而不是存储或通信。

### Reduction-bound

系统主要受 partial sum 合并、归约树或跨 tile 聚合限制。

### Control-bound

系统主要受调度、同步、控制流、host 协同或 runtime 开销限制。

### Host Stall Ratio

主处理器或协同执行单元因为等待：

- 数据
- 子图执行完成
- memory-side 返回结果

而产生的停顿比例。

它是判断系统协同是否顺畅的重要信号。

### Host Offload Ratio

原本在 host 执行的任务里，有多少真正被下沉到：

- `CIM`
- `PIM`
- memory-side accelerator

这个指标高不一定更好，还要结合同步和数据回传成本。

## 四. 数据流与映射术语

### Weight-stationary

一种数据流策略，尽量让权重驻留在阵列或 tile 中，减少重复装载。

### Input-stationary

一种数据流策略，尽量让输入驻留，权重分批流入。

### Output-stationary

一种数据流策略，尽量在本地保留和累加 partial sum，减少中间结果搬运。

### Graph Partition

把模型图划分成：

- 适合 `CIM` 的子图
- 必须 fallback 的子图
- 由其他执行单元承担的子图

### Fallback

原本目标是下沉到 `CIM` 的执行路径，最终仍保留在：

- `CPU`
- `GPU`
- `NPU`
- 传统数字单元

的部分。

它不是异常，而是现实系统中的常态。

### Hybrid Execution

模型并非完全由单一硬件执行，而是由：

- `CIM`
- host
- 其他加速器

共同完成。

评价时必须把切换和同步成本算进去。

## 五. 模型与场景术语

### KV Cache

Transformer / LLM decode 阶段缓存的 key-value 状态，用于后续 token 的 attention 计算。它常常是长上下文和低 batch 推理中的关键访存压力来源。

### Prefill

LLM 推理中处理输入上下文、生成初始状态的阶段。

通常特点是：

- 大矩阵乘多
- 传统 GPU / NPU 已较强
- 更偏 compute-intensive

### Decode

LLM 推理中逐 token 生成的阶段。

通常特点是：

- batch 小
- 重复频繁
- `KV cache` 和 memory 访问更关键

### Long Context

长上下文推理场景，通常会放大：

- `KV cache`
- 外部内存访问
- 带宽与容量压力

### Edge Inference

面向边缘端、终端设备的推理场景。

通常更关注：

- 功耗
- 成本
- 封装
- 固定模型或小模型部署

## 六. 研究记录时建议统一补的字段

后续读论文、公司资料或产品资料时，建议至少补这几项：

- 指标层级：`cell / macro / tile / chip / system`
- 精度条件：`INT4 / INT8 / mixed precision`
- workload：`MVM / GEMM / CNN / Transformer / decode`
- 是否包含外围：`ADC / DAC / buffer / NoC / DRAM / control`
- 数据来源：仿真、post-layout、silicon、系统 demo
- 产品形态：`macro / chip / card / module / system`

## 七. 最常见的误用

### 1. 只写 `TOPS/W`，不写层级

这是最常见的问题之一。

没有层级时，`TOPS/W` 很容易把：

- 宏指标
- 芯片指标
- 系统指标

混成一个数字。

### 2. 把不同 op 定义直接横比

不同论文可能对：

- `MAC`
- bit operation
- analog accumulate

使用不同统计口径。

如果不统一 op 定义，横比常常没有意义。

### 3. 只看峰值，不看有效吞吐

峰值更适合展示上限，不足以代表真实部署。

### 4. 只看阵列，不看外围

如果没有明确写入：

- `ADC`
- `DAC`
- buffer
- `NoC`
- DRAM

那么数字通常只代表局部，不代表系统。

## 八. 使用这些术语时的最小注意事项

- 所有性能数字尽量标明层级：`macro / tile / chip / system`
- 所有能效数字尽量标明是否包含 `ADC / NoC / DRAM / control`
- 所有 workload 术语尽量标明场景：`CNN / FFN / decode / long context`
- 所有精度数字尽量说明权重、激活、partial sum 是否同口径
- 所有产品描述尽量说明它是 `macro / chip / card / system`

## 后续可补充内容

- 指标换算示例
- 常见 benchmark 口径说明
- 不同论文的 op 定义差异
