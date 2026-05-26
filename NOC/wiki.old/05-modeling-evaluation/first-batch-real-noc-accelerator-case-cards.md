# 第一批真实 NoC / Accelerator Case Cards

上级：[建模与评估](./README.md)

相关：[AI Accelerator NoC Case Cards 与论文卡模板](./ai-accelerator-noc-case-cards-templates.md)

## 为什么先做一批“够用”的真实案例卡

模板本身还不够。  
你需要先有几张真实卡，后面记录新案例时才知道颗粒度应该到哪里。

下面这批卡不追求全量细节，而是服务于你的 NoC（片上网络）学习主线。

## Case 1：Google TPU 风格阵列互连

### System Goal

- 高吞吐矩阵计算
- 强调规则数据流

### Compute Organization

- 大规模规则 PE（处理单元）/ array（阵列）
- 强数据流导向

### Memory Organization

- 片上 buffer + 外部高带宽存储配合

### NoC / Interconnect Organization

- 更偏规则、局部、阵列式数据移动
- 强依赖编译器与数据流映射

### Main Traffic Types

- activation（激活值）/ weight（权重）有结构的数据移动
- 局部 forwarding（转发）

### Likely Bottlenecks

- 阵列边界的数据供给
- buffer / mapping 与数据复用匹配度

### 为什么值得参考

- 它代表“规则 workload + 强编译器驱动”的一类设计

## Case 2：Cerebras WSE 风格大规模二维互连

### System Goal

- 极大规模片上并行
- 尽量减少离片通信依赖

### Compute Organization

- 超大规模 2D spatial fabric（二维空间阵列结构）

### Memory Organization

- 更强调片上分布式资源

### NoC / Interconnect Organization

- 大规模二维邻接通信
- 强调可扩展和规则结构

### Main Traffic Types

- 邻近通信
- 局部数据交换
- 大规模同步 / 分布式流动

### Likely Bottlenecks

- 长路径通信
- 大规模同步传播
- 全局热点规避

### 为什么值得参考

- 它代表“二维规则扩展到极大规模”时 NoC 会遇到什么

## Case 3：Tenstorrent / Tensix 风格 tile dataflow

### System Goal

- 以 tile（计算单元）为单位组织计算与数据搬运
- 强调 dataflow-aware execution（数据流感知执行）

### Compute Organization

- tile / core / local memory 组合
- 数据流与计算紧耦合

### Memory Organization

- 本地 SRAM（静态随机存储）/ scratchpad（便签存储）很关键

### NoC / Interconnect Organization

- 更关注 tile-to-tile forwarding
- 更强调 stream、control、DMA 协同

### Main Traffic Types

- stream（数据流）
- DMA（直接内存访问）
- control（控制消息）
- 局部 pipeline forwarding（流水线转发）

### Likely Bottlenecks

- destination buffering（目的端缓冲）
- local memory arbitration（本地存储仲裁）
- stream backpressure（数据流反压）

### 为什么值得参考

- 这类设计和你的主学习目标最接近

## Case 4：Groq 风格编译驱动数据通路

### System Goal

- 最大化确定性和编译时调度

### Compute Organization

- 强静态调度
- 强软件规划

### Memory Organization

- 更强调静态已知的数据路径和供给关系

### NoC / Interconnect Organization

- 非常值得从 source routing（源路由）/ compiler-driven（编译器驱动）视角去理解

### Main Traffic Types

- 静态规划的数据通路
- 更少运行时不确定性

### Likely Bottlenecks

- 路径静态化后的局部热点
- 设计灵活性与确定性的平衡

### 为什么值得参考

- 它代表“把更多复杂度推给编译器”这条路线

## 这四张卡怎么用

可以把它们当成四种 archetype（架构原型）：

- 规则阵列型
- 超大二维扩展型
- tile dataflow（计算单元数据流）型
- 编译驱动静态路径型

后面遇到新论文或新产品时，优先问：

- 它更像哪一种
- 它在哪个维度和这几类不同

## 记录真实案例时的注意点

- 不要因为公司名知名就默认它的 NoC 一定“先进”
- 优先记录它解决了什么问题，而不是只记营销名词
- 把“对我自己的 simulator 有何启发”写出来

## 本页结论

第一批真实案例卡的价值，在于先建立几个足够清晰的参考 archetype。  
后面无论看论文还是看公司架构，你都可以更快把新信息放进已有判断框架里。
