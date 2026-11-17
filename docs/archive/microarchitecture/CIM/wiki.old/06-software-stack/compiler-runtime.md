# 编译器与 Runtime

## 为什么这一页是硬门槛

很多 `CIM` 路线在硬件论文里看起来成立，但一到真实模型部署就暴露出另一个问题：

> 阵列能算，不代表模型能自动跑上去。

`CIM` 的软件栈不是附属品，而是决定路线能否进入产品的关键门槛之一。原因很简单：

- 不是所有算子都适合映射到 `CIM`
- 即使算子适合，也未必能自动切分到 array / tile
- 很多模型必须以 `hybrid execution` 方式运行
- host、runtime、memory transfer 的开销可能吃掉硬件收益

因此，这一页的目标不是讲某个具体框架 API，而是建立一条从模型到执行的通路图。

## 一条更实用的软件栈视角

可以把 `CIM` 软件栈看成五层：

1. 前端模型表示
2. 编译 IR 与 operator lowering
3. graph partition 与 mapping
4. runtime 调度与数据搬运
5. host 与外部加速器协同

这五层里，只要有一层过弱，硬件优势就很难落到真实 workload。

## 1. 前端模型表示

### 要解决什么问题

首先要明确：

- 输入来自 `PyTorch`、`TensorFlow`、`ONNX` 还是私有 IR
- 模型图里哪些 op 可以被识别为 `CIM-friendly`
- 哪些 op 一开始就应标记为 fallback

### 这一层的关键判断

如果前端只能支持手工改写模型，或者只能支持很窄的一组网络，那么软件栈成熟度通常还比较低。

### 常见难点

- 模型图中的算子粒度和硬件可执行粒度不一致
- 训练时使用的算子组合与推理部署图不完全一致
- `Transformer / LLM` 中存在大量非矩阵核心路径

## 2. 编译 IR 与 Operator Lowering

### IR 为什么重要

`CIM` 不是普通矩阵加速器的简单替代，因为它常常需要表达：

- array-level operation
- tile-level execution
- 数据搬运与重排
- quantization / encoding 约束
- host 与外部单元的切换边界

如果 IR 里表达不了这些约束，后面的 mapping 只能靠手工补。

### IR 至少要能表达什么

- 张量形状与布局
- 精度与量化约束
- op 是否可落到 `CIM`
- 分块与映射信息
- 数据驻留位置
- fallback 目标

### Operator Lowering 在做什么

它的作用是把前端算子转成更接近硬件执行形态的中间表示。

例如：

- `GEMM` 拆成 array-friendly block
- `Conv` 决定是否 lowering 成矩阵乘
- `Attention` 拆成 projection、score、softmax、value aggregation

### 一个关键现实

很多路线真正难的不是“支持一个大 op”，而是：

- 一个前端算子要被拆成多个硬件子步骤
- 其中只有部分步骤适合 `CIM`

这时软件栈必须显式管理中间结果和执行边界。

## 3. Graph Partition 与 Mapping

### 为什么一定要单独看这一层

真实模型很少是“整网都适合 `CIM`”。更常见的是：

- 一部分子图适合 `CIM`
- 一部分保留在 `CPU / GPU / NPU`
- 一部分由传统数字单元处理

因此必须做 `graph partition`。

### 常见划分粒度

- `layer-level`
- `subgraph-level`
- `op-level`

粒度越细，理论利用率可能越高，但 runtime 和数据搬运复杂度也更高。

### Mapping 在做什么

当一个子图被判定适合 `CIM` 后，还要继续解决：

- 如何切到 array shape
- 如何映射到 tile
- 权重是否常驻
- 激活从哪里来
- partial sum 在哪里合并

### 这一层最常见失败点

- 划分过碎，数据往返太多
- 映射依赖人工调参
- array 利用率看似高，但 system 利用率很低
- fallback 路径不清楚，导致整图执行不稳定

## 4. Runtime 调度与数据搬运

### Runtime 真正在负责什么

runtime 不只是“发指令”，它通常还要负责：

- 子图执行顺序
- tile / macro 调度
- buffer 与 scratchpad 管理
- DMA / memory transfer
- host 同步
- fallback 执行协调

### 为什么 runtime 会吃掉收益

即使编译阶段找到了可映射子图，runtime 仍可能因为：

- 频繁切换执行单元
- 数据重排太重
- host 同步过多
- 调度粒度太细

把理论收益消耗掉。

### 这层最该盯的指标

- launch overhead
- transfer overhead
- host stall ratio
- execution overlap 能否成立
- 子图切换频率

## 5. Host 与外部加速器协同

### 为什么 `CIM` 很少独立存在

大多数 `CIM` 路线都不是完整通用计算平台，而是系统中的一个专用执行单元。

因此要明确：

- 哪些 op 在 `CIM`
- 哪些 op 在 `CPU / GPU / NPU`
- 中间张量如何在它们之间流动

### 这层最容易被低估

很多方案在 paper 中只展示被加速部分，但在系统里真正决定收益的是：

- 切换代价
- 数据回传代价
- host 是否成为瓶颈

### 针对 LLM 特别要问

- 加速的是 `FFN`、projection，还是 `KV cache` 访问路径
- `softmax`、normalization、sampling 是否仍在 host
- `decode` 每步是否都要来回同步

## 一条简化执行路径

可以把一次典型执行理解成：

1. 前端模型导入
2. 编译器识别可映射 op / subgraph
3. lowering 到硬件友好的 IR
4. partition 成 `CIM` 与 fallback 路径
5. mapping 到 array / tile / memory hierarchy
6. runtime 调度执行与数据搬运
7. host 汇总结果并继续后续图执行

这条链上，任何一段不成熟，都会让“硬件支持某个算子”与“模型可部署”之间出现巨大落差。

## 三个最核心的问题

## 1. 是否真的支持自动映射

如果一个路线需要工程师手工指定：

- 子图划分
- 数据布局
- 权重切块
- tile 分配

那么它更像研究工具链，而不是成熟产品软件栈。

## 2. fallback 成本是否可控

成熟的软件栈不是没有 fallback，而是能清楚管理：

- 哪些 op fallback
- fallback 频率多高
- fallback 造成多少额外数据搬运

如果 fallback 成本不可控，最终系统表现往往会明显弱于 kernel benchmark。

## 3. runtime 是否理解硬件真实约束

`CIM` runtime 不能只像通用 graph executor 一样排 op，它还必须理解：

- array 容量
- tile 并行度
- 局部缓存限制
- 数据编码与量化约束
- host 协同边界

## 不同路线的软件难点并不一样

## SRAM-CIM / Digital CIM

更容易承接现有数字编译和部署流程。

但仍要解决：

- 权重驻留与切块
- 局部算子映射
- 与片上 NPU / CPU 的协同

## ReRAM / Analog CIM

软件栈还要额外承接：

- 精度限制
- 编码方式
- 非理想因素感知 mapping
- 校准后的参数适配

也就是说，它的软件问题不只是“调度”，还包括“误差感知执行”。

## DRAM / HBM-PIM

更偏系统和 runtime 协同问题。

要重点解决：

- host 与 memory-side 协作
- memory command / interface 扩展
- 哪些 workload 真正值得 offload

## 一个实用的成熟度判断框架

可以把软件栈成熟度粗分成四级：

### Level 1：论文脚本级

特点：

- 手工 mapping
- 只支持少量 benchmark
- 缺少通用前端入口

### Level 2：研究编译器级

特点：

- 有 IR、有 lowering
- 可支持若干标准模型
- fallback 和 runtime 仍较脆弱

### Level 3：原型产品级

特点：

- 支持主流模型导入
- 有稳定 partition / mapping 流程
- 有较清晰的 runtime 与 host 协同机制

### Level 4：可部署产品级

特点：

- 接近标准部署工具链
- 自动化程度较高
- 客户不需要深度理解底层 array 才能使用

## 读公司或论文时建议直接追问

1. 支持哪些前端模型格式？
2. 哪些算子是原生支持，哪些必须 fallback？
3. mapping 需要用户手工参与到什么程度？
4. runtime 如何处理数据搬运和 host 同步？
5. 指标是否包含 fallback 与协同成本？

## 一个最实用的判断原则

如果一个方案只证明：

- 某类阵列能算
- 某个 kernel 很高效
- 某个模型能在定制脚本里跑通

但没有清楚回答：

- 模型如何导入
- 子图如何划分
- fallback 如何处理
- runtime 如何调度

那么它的软件栈大概率还不足以支撑真实产品落地。

## 与本章其他页面的关系

- [量化与映射](./quantization-mapping.md)：更聚焦位宽、编码与硬件约束下的精度问题
- [模型适配与图划分](./model-adaptation.md)：更聚焦哪些模型和子图适合 `CIM`

本页重点放在：

- 编译流程
- IR 与 lowering
- runtime 调度
- host 协同与 fallback

## 后续可补充内容

- 编译流程图
- `GEMM / Conv / Attention` lowering 例子
- runtime 调度示意
- software maturity checklist
