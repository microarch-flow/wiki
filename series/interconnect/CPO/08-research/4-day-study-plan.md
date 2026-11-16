# 4 天学习计划与阅读提问清单

上级：[08 研究模板与术语](./README.md)

相关：[CPO 入门必读 10 篇](./reading-pack-cpo-top-10.md)、[论文阅读模板](./paper-review-template.md)

## 这页怎么用

这页不是替代论文，而是帮你控制阅读顺序和阅读深度。

目标不是 4 天读完后记住所有细节，而是 4 天后你能建立一套稳定判断框架：

- 先看系统问题
- 再看器件和光引擎
- 再看封装与装配
- 最后看可靠性和商业化边界

## Day 1：先建立问题地图

阅读：

1. [Co-packaged optics (CPO): status, challenges, and solutions](./reading-pack-cpo-top-10.md)
2. [In-Package Optical I/O: Bridging the Gap Between Moore's Law and Amdahl's Law in Modern Compute Systems](./reading-pack-cpo-top-10.md)

### 今天的核心目标

- 搞清 CPO 到底在解决什么问题
- 搞清为什么“更近的光 I/O”是系统问题，而不是模块形态问题
- 搞清 AI / HPC 为什么比传统数据中心更需要它

### 读完后必须回答

1. CPO 替换的到底是哪一段电链路
2. 如果继续用 pluggable，系统瓶颈最可能出现在哪里
3. 为什么说 CPO 的驱动力来自计算系统扩展，而不只是光通信升级
4. 这两篇材料里，哪些结论是系统判断，哪些只是方向判断

### 如果你读完还说不清

- `CPO`、`NPO`、`pluggable` 的边界
- `system bandwidth density` 和 `module upgrade` 的区别

说明你还没真正建立系统层视角，需要回看 [01-overview/taxonomy.md](../01-overview/taxonomy.md) 和 [03-architecture-platform/system-stack.md](../03-architecture-platform/system-stack.md)

## Day 2：进入 optical I/O chiplet 和封装平台

阅读：

1. [TeraPHY: A High-density Electronic-Photonic Chiplet for Optical I/O from a Multi-Chip Module](./reading-pack-cpo-top-10.md)
2. [Connectorized Optical I/O Chiplet with V-groove for AI and High Performance Computing](./reading-pack-cpo-top-10.md)
3. [Optoelectronic Glass Substrates for Co-packaging of Optics and ASICs](./reading-pack-cpo-top-10.md)

### 今天的核心目标

- 搞清为什么 optical I/O 往往以 chiplet 形态出现
- 搞清 connectorized、KGD、V-groove 这些词为什么重要
- 搞清 substrate 为什么也可能成为 CPO 的关键平台变量

### 读完后必须回答

1. 为什么 chiplet 形态比单纯器件 demo 更接近真实系统
2. KGD 在 optical I/O chiplet 里解决了什么问题，又没解决什么问题
3. 玻璃基板或其他高密度平台，到底改变了哪个系统约束
4. 这一天的 3 篇里，哪些在证明“能集成”，哪些在证明“更可制造”

### 今天最容易掉进的坑

- 把 chiplet 直接等价成“已量产”
- 看到高密度封装平台，就默认热、测试和维修也自动解决

## Day 3：进入模块与装配

阅读：

1. [Photonic Modules with High Density Polymer Waveguide Interface](./reading-pack-cpo-top-10.md)
2. [Co-Packaged Optics (CPO) Technology Full Module Test Vehicle Demonstrations](./reading-pack-cpo-top-10.md)
3. [Co-packaged optics module with single mode polymer waveguide](./reading-pack-cpo-top-10.md)

### 今天的核心目标

- 搞清 polymer waveguide interface 为什么反复出现
- 搞清 full module、reflow、JEDEC、optics-last assembly 这些词为什么是工程信号
- 搞清从“部件可行”到“模块可行”的关键跨越是什么

### 读完后必须回答

1. polymer waveguide interface 相比传统 fiber attach 解决了什么
2. optics-first 和 optics-last assembly 分别对应什么制造考量
3. 为什么 reflow compatibility 和 JEDEC stress 比峰值链路速率更能说明落地性
4. 这几篇材料是否已经回答了系统级散热和维护问题，如果没有，还缺什么

### 今天最值得你记住的一件事

如果一篇论文开始认真谈 assembly order、pitch、reflow、pre-conditioning、stress test，它通常比只报链路指标的论文更接近真实量产问题。

## Day 4：进入连接与可靠性

阅读：

1. [Improved connectorization of compliant polymer waveguide ribbon for silicon nanophotonics chip interfacing to optical fibers](./reading-pack-cpo-top-10.md)
2. [Experimental Identification of the Failure Modes and Failure Mechanisms of Fiber to Waveguide Couplings Under Cyclic Tensile Loading](./reading-pack-cpo-top-10.md)

### 今天的核心目标

- 搞清为什么 attach、stress、connectorization 是 CPO 的硬问题
- 搞清实验室对准和高吞吐制造之间的差距有多大
- 搞清很多系统失败并不是因为链路跑不起来，而是因为长期不稳定

### 读完后必须回答

1. 单模光学高精度要求为什么会把装配变成瓶颈
2. 自对准、strain relief、adhesive 这些词为什么重要
3. 可靠性论文真正告诉你的，是哪个最脆弱的接口
4. 如果要把 CPO 商业化，哪些测试和寿命问题必须提前回答

### 今天结束后你应该形成的判断

如果一个 CPO 方案没有清楚回答连接和可靠性问题，它离真正可部署系统通常还很远。

## 每篇论文都该问的 8 个问题

1. 它解决的是系统问题、器件问题、封装问题，还是连接与可靠性问题
2. 它默认的场景是什么：传统数据中心、HPC 还是 AI 集群
3. 它替换或缩短的是哪一段电链路
4. 它有没有诚实讨论热、测试、维护和良率
5. 它给出的收益是局部收益还是系统级收益
6. 它最强的证据是模型、实验样机、模块验证，还是可靠性测试
7. 它最关键的隐含前提是什么
8. 如果把它放进真实数据中心，最可能先暴露的问题是什么

## 读完 4 天后的验收标准

如果 4 天后你已经能稳定回答下面 5 个问题，说明这轮入门基本有效：

1. 为什么 CPO 不是“更高级的可插拔模块”
2. 为什么 external laser 和 optical I/O chiplet 会反复出现
3. 为什么 polymer waveguide interface 值得关注
4. 为什么 thermal / assembly / reliability 文献在判断落地性时权重很高
5. 为什么 AI / HPC 比一般网络更可能先推动 CPO

## 下一步怎么继续

- 如果你想继续偏系统：去扩展交换机架构、AI 网络、bandwidth density 与 TCO
- 如果你想继续偏工程：去扩展封装、connectorization、stress、JEDEC reliability
- 如果你想继续偏器件：去扩展 silicon photonics、modulator、detector、driver/TIA 协同
