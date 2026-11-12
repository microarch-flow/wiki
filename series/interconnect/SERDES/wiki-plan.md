# SerDes Wiki：目录与内容规划

状态：**规划与实施记录**。三个阶段的规划正文和图解已编写。实际检查范围和结果以本地构建与自检记录为准；专题内容不代替具体协议规范或产品验证。

输入包括[现有 Wiki 总览](../../../README.md)、[Wiki 与博客设计规则](../../../docs/wiki-blog-design-rules.md)，以及仅保存在本地的 Claude 对话记录。对话提供了读者问题和待核验观点，不作为技术结论的依据。本文列出的技术资料是起点；正文仍需逐条核实来源、适用对象和条件。

## 1. 定位与读者

SerDes Wiki 要回答一个主问题：**数字数据怎样经过一条高速串行链路，并在接收端被可靠恢复？**

读者了解比特、时钟和基本数字逻辑，但不要求已经掌握模拟电路、信号完整性或通信理论。正文从单向、单 lane 的电链路开始，逐步过渡到多 lane、协议、设计验证和系统建模。

学习完成后，读者应能：

1. 画出一条链路的数据路径和时钟、训练控制路径，并解释各模块的输入、输出及职责。
2. 区分物理通道、SerDes、PHY、PCS、协议与系统接口；知道这些名称的边界随标准和实现变化。
3. 根据明确假设换算并行接口速率、符号率、UI、名义带宽与有效数据率。
4. 解释通道损伤、均衡、采样和时钟恢复之间的因果关系，以及它们的代价和适用条件。
5. 看懂给定规格和测试报告中的关键条件，区分仿真、样片、互通、量产与长期可靠性的证据。
6. 根据问题选择波形级、行为级或系统级模型，并说明模型不能证明什么。

本文首先覆盖电 SerDes。光链路、DDR/HBM、UCIe 和其他近距接口用于比较系统边界；它们各自的协议和器件细节仍以对应专题与规范为准。本专题不预设每一种 PHY 都包含相同的 SerDes 结构，也不把所有芯粒连接都归为同一种接口。

## 2. 主线与阶段

### 2.1 一条最小数据路径

```text
上层 / 数字接口
     │ 并行数据与控制
     ▼
发送端 TX：串行化 ─ 发送均衡 ─ 驱动
                                   │
                                   ▼
                  通道：封装、走线、连接器等
                                   │ 受损的电信号
                                   ▼
接收端 RX：前端 / 均衡 ─ 采样与判决 ─ 解串
                                            │
                                            ▼
                                    并行数据 / 上层

发送时钟生成 ──► TX          RX 采样器 ◄── 时钟与数据恢复 CDR
配置 / 校准 / 链路训练 ───────► 两端的可调模块
```

这是教学抽象，不是固定的电路级串联图。TX 发送均衡可与驱动级合并；RX 的 DFE、采样和 CDR 可能相互耦合；具体实现可能包含 ADC、DSP、多个时钟相位或其他模块。正文要分别说明**数据路径**和**控制反馈路径**，避免把反馈画成单向流水线。[S1](#s1)、[S2](#s2)

### 2.2 分阶段交付

| 阶段 | 主要内容 | 预期产物 | 本阶段不声称 |
| --- | --- | --- | --- |
| **第一阶段** | 01 全局链路、02 电信号与通道、03 发送端、04 接收端 | 专题首页、四章首页、22 篇正文；配套基础术语、资料和贯穿案例 | 不声称已完成协议规范、芯片设计、流片或硬件测试 |
| **第二阶段** | 05 信号与指标、06 初始化与链路训练 | 两章首页、10 篇正文、图解、阶段术语、资料和自测 | 不把某协议的训练序列推广到所有链路 |
| **第三阶段** | 07 设计与验证、08 系统应用、09 建模、10 参考 | 三章首页、16 篇正文、图解、符号与单位、术语、资料和自测 | 不凭通用资料宣称某产品达到其未公开的参数 |

第一阶段引入 NRZ、UI、眼图和 BER 的**最小含义**，以支撑 TX/RX 主线；第五章进一步讨论定义、测量和边界。`10-reference/` 按阶段维护术语、资料、自测以及符号和单位；参考内容不能替代各协议与器件的具体文档。目录与标题可随资料核验继续调整。

## 3. 完整目录

下面是规划目录。文件名是建议的稳定路径；注释说明每篇要回答的核心问题。三个阶段的正文均已建立。

```text
SERDES/
├── wiki-plan.md                         # 本规划稿；不作为专题正文
└── wiki/
    ├── README.md                        # 专题入口、阅读路径、章节状态
    ├── 01-overview/                     # 第一阶段：建立整条链路
    │   ├── README.md
    │   ├── why-serdes.md                 # 为什么需要串并转换；串行也有代价
    │   ├── link-end-to-end.md            # 一组数据经过 TX、通道和 RX
    │   ├── phy-serdes-protocol.md        # PHY、SerDes、PCS 与协议边界
    │   └── rates-clocks-and-ui.md        # 并行速率、线速率、符号率、UI 与时钟
    ├── 02-signal-channel/                # 第一阶段：信号为什么会变形
    │   ├── README.md
    │   ├── voltage-current-and-switching.md  # 电压、电流、阈值和有限上升时间
    │   ├── differential-and-return.md       # 差分、共模、回流和非理想性
    │   ├── timing-skew-and-jitter.md         # 相位、skew、jitter 和采样窗口
    │   ├── impedance-and-reflection.md      # 传输线、特性阻抗、终端和反射
    │   ├── loss-db-and-s-parameters.md      # 插入损耗、dB、频率与参考面
    │   └── isi-noise-and-eye.md              # ISI、噪声和眼图为何影响判决
    ├── 03-transmitter/                   # 第一阶段：怎样产生并发送信号
    │   ├── README.md
    │   ├── parallel-to-serial.md         # 并行字怎样按顺序变成串行流
    │   ├── clock-pll-and-multiphase.md   # PLL、倍频、分频和多相时钟
    │   ├── driver-swing-and-termination.md  # 输出驱动、摆幅和阻抗约束
    │   ├── tx-equalization-ffe.md       # TX FFE 如何改变发送波形
    │   └── tx-path-worked-example.md     # 串起时钟、串行化和 TX 输出
    ├── 04-receiver/                      # 第一阶段：怎样恢复数据
    │   ├── README.md
    │   ├── receiver-signal-chain.md     # RX 各模块的输入、输出和反馈关系
    │   ├── analog-frontend-and-ctle.md   # 接收前端、增益与 CTLE
    │   ├── sampler-and-decision.md       # 采样、判决门限和噪声余量
    │   ├── cdr-and-timing-recovery.md    # 没有独立数据时钟时怎样找到采样相位
    │   ├── dfe-and-error-propagation.md   # DFE 如何利用历史判决、何时出错
    │   ├── deserializer-and-alignment.md # 解串、字边界、时钟域和对齐
    │   └── rx-cooperation-example.md    # CTLE、DFE、CDR、采样的联合案例
    ├── 05-signaling-and-metrics/         # 第二阶段：正确读指标
    │   ├── README.md
    │   ├── nrz-and-pam4.md               # 符号、电平、比特与速率取舍
    │   ├── coding-and-scrambling.md      # 线路编码、加扰、同步与转换密度
    │   ├── eye-and-jitter.md             # 眼高、眼宽、抖动与测量参考
    │   ├── ber-confidence-and-fec.md    # BER、置信度、突发错误及 FEC 前后
    │   └── bandwidth-power-efficiency.md # 线速率、有效带宽和 pJ/bit 口径
    ├── 06-link-operation/                # 第二阶段：链路怎样建立并维持
    │   ├── README.md
    │   ├── initialization-calibration.md # 上电、复位、锁定、校准与配置
    │   ├── training-and-adaptation.md    # 双端协商与本地自适应的边界
    │   ├── lane-alignment.md             # 多 lane 对齐、缓冲和允许范围
    │   ├── retraining-and-observation.md # 降速、重训、状态与错误观测
    │   └── pcie-training-case.md        # 指定版本的 PCIe 链路建立案例
    ├── 07-design-and-validation/         # 第三阶段：自研与可用性证据
    │   ├── README.md
    │   ├── requirements-and-contract.md # 协议、速率、通道、PVT 与目标
    │   ├── architecture-tradeoffs.md    # 模拟 / ADC-DSP、均衡和时钟选型
    │   ├── system-and-channel-models.md # 行为模型、通道模型和仿真范围
    │   ├── circuit-layout-and-pvt.md     # 电路、版图、寄生和工作条件
    │   ├── lab-compliance-interop.md     # 样片、BERT、合规、互通和可靠性
    │   └── in-house-evidence.md          # 自研范围与各阶段可支持的结论
    ├── 08-system-applications/           # 第三阶段：把链路放回系统
    │   ├── README.md
    │   ├── pcie-and-ethernet.md          # 共用原理与不同协议边界
    │   ├── lane-count-vs-rate.md         # 多 lane、单 lane 速率、岸线与功耗
    │   ├── chiplet-and-d2d.md            # 封装内串行与宽并行接口的选择
    │   ├── hbm-and-3d.md                 # HBM 外部接口、堆叠与垂直连接
    │   ├── cpo-electrical-optical.md     # 电链路与光引擎的接口位置
    │   └── product-claims-and-evidence.md # 读取公开规格及其时间和适用边界
    ├── 09-modeling/                      # 第三阶段：架构模型如何保留关键行为
    │   ├── README.md
    │   ├── modeling-scope.md             # 波形级、行为级、事件级的适用问题
    │   ├── rate-latency-power.md         # 可校准的带宽、延迟与能耗参数
    │   ├── link-state-and-failure.md     # 训练、可用、降速、重试的契约
    │   └── worked-model-and-limits.md    # 给定参数的例子与不能推断的结论
    └── 10-reference/
        ├── README.md
        ├── glossary.md                   # 第一阶段术语表
        ├── symbols-and-units.md          # 符号、单位和指标参考面
        ├── questions-and-self-check.md   # 概念、手算、反例和迁移题
        ├── sources.md                    # 第一阶段资料
        ├── phase2-glossary.md            # 第二阶段术语表
        ├── phase2-sources.md             # 第二阶段资料与适用范围
        ├── phase2-self-check.md          # 第二阶段自测
        ├── phase3-glossary.md            # 第三阶段术语表
        ├── phase3-sources.md             # 第三阶段资料与适用范围
        └── phase3-self-check.md          # 第三阶段自测
```

## 4. 第一阶段逐篇规划

每篇文章应围绕一个具体问题，说明必要条件、例子和适用边界。涉及模块或机制时，还要说明输入、输出、职责和执行过程。只有在比较方案有助于理解时才扩展对比；不要求每页套用相同模板。

### 4.1 全局链路：01

先把读者的问题放到同一条链路上，再进入模块。章首页按下表顺序列出文章。

| 文章 | 内容边界与重点 | 最小例子 / 阅读结果 |
| --- | --- | --- |
| `why-serdes.md` | 并行与串行接口的位宽、引脚、时钟、通道和功耗取舍；区分单 lane 与多 lane。不能说串行消除了所有 skew。 | 对比两种**假设的**数据路径，列出需要的引脚和对齐条件，不宣称任何一种必然更省功耗。 |
| `link-end-to-end.md` | 上层输入、TX、通道、RX 和输出；单方向 lane 与双向链路；数据、时钟和控制三条关系。 | 用第 5 节样例追踪一个并行字；能标出各观察点的数据形态。 |
| `phy-serdes-protocol.md` | SerDes 的窄义串并转换与收发器广义用法；PHY、PCS/PMA、协议和实现边界。用具体协议作例，不把划分当成所有标准的共同定义。 | 把一个给定收发器的数据路径与 PCIe 分层对应；解释同一 SerDes IP 支持某协议不等于完整产品已支持该协议。[S1](#s1)、[S3](#s3) |
| `rates-clocks-and-ui.md` | 比特率、符号率、并行字时钟、UI；NRZ 和 PAM4 的最小区别；发送与接收时钟可能不同。 | 核算 `32 × 312.5 MHz = 10 Gb/s` 的条件；反例：`32 × 156 MHz` 并不等于 `10 Gb/s`。[S4](#s4) |

入口需要先链接[共用电路与时序基础](../../microarchitecture/foundations/electrical-timing-foundations.md)，并指出高速电路可以使用分时、半速率或多相结构；不能把线速率直接等同于每一级数字逻辑的时钟。

### 4.2 电信号与通道：02

本章不重复完整的电路基础。它从发射和接收参考面之间的信号变化出发，解释为什么通道不是理想导线。

| 文章 | 内容边界与重点 | 最小例子 / 阅读结果 |
| --- | --- | --- |
| `voltage-current-and-switching.md` | 电压相对参考、负载电容、有限边沿、采样门限；数字与模拟是不同抽象，实际电路依赖连续电气行为。链接共用时序文章。 | 在假设电容、恒定电流及电压变化量下估计时间；指出驱动电流并非常数时该估算的限制。 |
| `differential-and-return.md` | 差模电压、共模电压、P/N 电流路径；共模抑制及实际不平衡、转换和回流。 | 给两根线叠加相同与不同的扰动，分别算差模变化；不假定所有干扰均被消除。[S5](#s5) |
| `timing-skew-and-jitter.md` | 周期与相位、线对内部 skew、多 lane skew、时钟 / 数据 jitter、采样窗口；区分来源和观察点。 | 假设两个 lane 到达时间相差若干 UI，计算需要吸收的相对时间；不由此直接推断 FIFO 的最终深度。[S6](#s6) |
| `impedance-and-reflection.md` | 何时需要传输线模型；特性阻抗、负载终端、不连续与反射；不同观察时间的电压。 | 使用固定 `Z0`、`RL` 和入射阶跃计算第一次负载反射；链接现有封装 SI 手算。[S7](#s7) |
| `loss-db-and-s-parameters.md` | 幅度比与功率比的 dB；插入损耗、参考阻抗 / 参考面、频率与差分 `Sdd21` 的基本读法。先解释意义，再引出完整 S 参数。 | 匹配且定义一致的教学条件下，从 `Sdd21 = −20 dB` 换算传输波幅度比 `0.1`；不把它直接等同于任意源端到 RX 电压比或 BER。[S8](#s8) |
| `isi-noise-and-eye.md` | 脉冲响应、前后符号的残留、随机噪声和眼图的关系；眼高、眼宽仅作入门定义。 | 用第 5 节两抽头通道手算两个采样值；指出眼图能提示余量，但不能单凭图形直接得到严格 BER。 |

### 4.3 发送端：03

每篇都标明输入输出和时钟关系。前两篇分别讲“位怎样排列”和“边沿从哪里来”；后两篇分别讲“电气输出”和“为何改变波形”。

| 文章 | 内容边界与重点 | 最小例子 / 阅读结果 |
| --- | --- | --- |
| `parallel-to-serial.md` | 并行字、位序、复用与边界；全速率、半速率或多相只是不同实现选择。 | 按约定的 MSB-first 顺序，把一个 32 位字映射到连续 32 个 UI；说明位序是接口约定。 |
| `clock-pll-and-multiphase.md` | 参考时钟、反馈、PLL / VCO、分频、相位与抖动；锁定有工作条件。 | 对理想整数倍频算一次输出；解释四个相位轮流服务并不意味着每个模块都以线速率时钟工作。[S9](#s9) |
| `driver-swing-and-termination.md` | 驱动、差分摆幅、负载、终端及输出阻抗；偏置 / 共模范围和实际器件约束。CML 只作一种实现。 | 给定理想差分电压和纯电阻负载，算电压 / 电流；标出功率计算的参考面和理想假设。 |
| `tx-equalization-ffe.md` | 抽头、当前和邻近符号的加权、预加重 / 去加重的命名；输出幅度、噪声和功耗代价。 | 计算 `y[k] = a[k] − 0.25a[k−1]`；说明初始历史、幅度归一化和线性抽象的假设。[S2](#s2) |
| `tx-path-worked-example.md` | 把并行输入、PLL / 多相、串行位序、FFE 和驱动连接起来；标出接口及未覆盖内容。 | 以第 5 节教学链路逐步给出一个符号的发送次序和参考时刻；不把逻辑示意当作晶体管波形。 |

### 4.4 接收端：04

先看总图，再分别解释幅度、时刻和历史符号。最后重组 RX，避免把 DFE 和 CDR 错写为必然依次发生的固定流程。

| 文章 | 内容边界与重点 | 最小例子 / 阅读结果 |
| --- | --- | --- |
| `receiver-signal-chain.md` | 接收端观察到的模拟信号、输入终端、CTLE、采样器、DFE、CDR、解串和输出；功能划分随实现变化。 | 在一张图上区分连续信号、离散判决、时钟与反馈；列出每个模块的输入输出。[S2](#s2) |
| `analog-frontend-and-ctle.md` | 接收摆幅与共模条件、增益和 CTLE 的频率选择；信号补偿也可能放大噪声。 | 对比两个假设频率点的通道与均衡器增益；不由两个点宣称整个频响已理想均衡。[S10](#s10) |
| `sampler-and-decision.md` | 采样时刻、参考门限、保持与判决；NRZ 两电平和 PAM4 多门限的入门关系。 | 给出信号、门限和一次噪声扰动，判断结果；说明一次正确判决不能证明 BER。 |
| `cdr-and-timing-recovery.md` | 频率与相位偏差、数据转换、相位检测、调整和锁定；参考时钟、长时间无转换及跟踪范围。 | 用提早 / 滞后的离散时间表解释反馈方向；区分时钟恢复与字边界对齐。[S11](#s11) |
| `dfe-and-error-propagation.md` | 由既往判决估计后游 ISI；抽头系数和反馈，误判后如何影响下一次判决。 | 用第 5 节离散抽样模型演算正确历史与错误历史；说明不放大线性噪声并不等于没有噪声或反馈代价。 |
| `deserializer-and-alignment.md` | 把多个采样结果组织成字；串行位序、字边界和跨时钟域；位对齐不等于多 lane 对齐。 | 以固定 32 bit 字宽展示两种边界产生的不同字；将完整多 lane deskew 放到第六章。 |
| `rx-cooperation-example.md` | 一条受损链路上，CTLE、CDR、采样和 DFE 如何协同；不同架构可以缺少某些模块。 | 将第 5 节案例从通道样本推进到判决和解串；列出这个教学模型没有模拟的噪声、时钟反馈和非线性。 |

## 5. 贯穿第一阶段的教学案例

采用同一组教学参数，贯穿链路、通道、TX 和 RX。它是**人为构造的例子**，不是某项标准、芯片规格或测量结果。

### 5.1 输入与速率

- 一条**单向**差分 NRZ lane；信号电平用归一化的 `−1` 和 `+1` 表示。
- 假设串行化器输入端每个时钟周期提供一个 32 bit 字，时钟为 `312.5 MHz`。所有 32 bit 都进入串行流，无空周期和额外编码开销。
- 所以串行线速率为 `32 × 312.5 MHz = 10 Gb/s`；NRZ 每符号 1 bit，因此符号率为 `10 GBd`，一个 UI 为 `100 ps`。这些数字不代表应用有效载荷速率。
- 约定 MSB-first。真实接口应以其具体位序与采样规则为准。
- 以 `5 GHz` 作为此例符号率一半的参考频点；它不是链路自动存在的硬截止频率。

### 5.2 离散通道与判决

先只看接收采样时刻的一个教学模型：

```text
a[k] ∈ {−1, +1}
r[k] = 0.7 × a[k] + 0.2 × a[k−1]
```

其中 `a[k]` 是当前发送符号，`a[k−1]` 是前一个符号，`r[k]` 是**归一化**的接收采样值。假设通道线性且当前只保留一个历史抽头；暂不加入噪声、反射的多次往返、时钟误差或非线性。

| 当前符号 | 前一符号 | 采样值 `r[k]` | 门限为 0 时的判决 |
| ---: | ---: | ---: | --- |
| `+1` | `+1` | `+0.9` | `+1` |
| `+1` | `−1` | `+0.5` | `+1` |
| `−1` | `+1` | `−0.5` | `−1` |
| `−1` | `−1` | `−0.9` | `−1` |

历史符号会改变采样值，但此例在无噪声、采样时刻正确时仍能正确判决，不能说出现 ISI 就必然误码。理想 DFE 若已知正确的上一符号和 `0.2` 系数，可从 `r[k]` 扣除历史项，得到 `0.7a[k]`。若历史判决错误，扣除项也可能错误。这个抽样等式不模拟 CTLE 的连续频响、CDR 闭环或电路带宽。

### 5.3 图解计划

优先制作四类图；每张都要有文字说明、替代文本和适用条件。

1. **链路总图**：显示数据、时钟和控制，不暗示所有芯片采用同一模块排列。
2. **差分与通道图**：分别显示 P/N 电压、差模和假设的共模扰动；另示阻抗不连续与反射。
3. **TX 时间图**：显示并行字、串行位序、时钟相位和 FFE 抽头；标记位序与速率假设。
4. **RX 反馈图**：显示 CTLE、采样、DFE 历史判决和 CDR 相位调整；标明方向及观察点。

这些是教学图解。即使后续加入交互，也不能把演示结果称为电路仿真、实测眼图或产品性能。实现交互时需检查键盘、窄屏和减少动态效果。

## 6. 第五至十章的内容与边界

| 章节 | 主要问题 | 与第一阶段的衔接及限制 |
| --- | --- | --- |
| 05 信号与指标 | 相同比特率下 NRZ/PAM4 的符号率、眼图、噪声余量和带宽怎样比较？怎样报告 BER、FEC 前后、置信度及 pJ/bit？ | 扩展第一阶段的基础概念；`UI` 定义和参考频点须绑定符号率与标准。零错误测试要报告观察比特数、模型和置信度，不等于 BER 为零。[S4](#s4)、[S12](#s12) |
| 06 链路运行 | 检测对端、锁定、训练、均衡、自适应、lane 对齐、降速和重训怎样配合？ | 明确本地调整与双端消息；训练顺序、超时和动作以**指定协议版本**为准。每 lane 恢复时钟不消除跨 lane 对齐约束。[S6](#s6)、[S13](#s13) |
| 07 设计与验证 | 从需求到实现和测试，哪些输入需要冻结？哪些结果支持“能运行”“达标”“可互通”“可量产”？ | 规格要包含调制、速率、通道参考面、PVT、目标错误指标、供电、面积、测试与对端。分别记录行为仿真、晶体管 / 提取后仿真、样片与系统验证；电气合规不自动证明互通或量产可靠性。[S13](#s13) |
| 08 系统应用 | PCIe、以太网、CPO、D2D、HBM 的连接目的、协议、物理路径和代价怎样不同？ | 区分封装内部的短距串行和宽并行实现、HBM 堆栈内互连与对外接口；TSV、微凸点和混合键合是物理连接手段，不自动定义协议。参数和产业动态必须带版本、日期及来源。[S14](#s14) |
| 09 建模 | 哪些问题需要模拟波形，哪些可以只保留速率、延迟、状态、错误和功耗？ | 输入需包含数据来源、工作条件和状态转移契约。事件模型不会自行证明眼图、BER、互通或真实硬件性能；没有恢复机制时不能凭空添加固定重训罚时。 |
| 10 参考 | 如何统一术语、公式、参考面、常见误解和资料入口？ | 按阶段维护，给术语和公式链接到已实现正文；来源区分标准、厂商实例、推导和未核验资料。 |

## 7. 与现有内容的衔接

| 现有内容 | SerDes 专题如何使用 | 分工边界 |
| --- | --- | --- |
| [从电荷到芯片时序](../../microarchitecture/foundations/electrical-timing-foundations.md) | 作为电容、电压、边沿、setup / hold 的先修入口。 | 共用基础解释同步数字路径；SerDes 专题继续解释跨通道波形、时钟恢复和判决。 |
| [PCIe 分层架构](../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md) | 从协议物理层链接到 SerDes 机制，再从训练案例返回 PCIe。 | PCIe 专题保留协议、事务、链路层及系统语义；本专题不复制整套 PCIe 规范。 |
| [封装信号完整性](../../../FAB/wiki/06-cross-cutting-engineering/signal-integrity-in-package.md) | 复用反射算例及封装、回流和 SI/PI 联系。 | FAB 关注制造与封装约束；本专题聚焦 TX—通道—RX 的链路行为。 |
| [CPO 光链路基础](../CPO/wiki/04-optical-engine/optical-link-basics.md) | 从电 SerDes 边界连接驱动、调制器、光通道和接收侧。 | 光功率预算与光器件留在 CPO；不能把光损耗预算直接套成电通道预算。 |
| [DDR：双倍数据率](../../storage/RAM/wiki/05-dram-protocol-families/why-double-data-rate.md) | 对比并行、随路选通与嵌入时钟串行链路，说明采样与训练共性。 | 不把 DDR / HBM 的 PHY 简化为“没有串并转换”，也不把其整个接口称为常见长距 SerDes。 |

专题已按现有配置接入网站；每阶段继续检查正文链接、导航、面包屑和搜索。`wiki-plan.md` 和原始聊天记录留在正文目录之外；公开发布按仓库既有流程另行处理。

## 8. 对话问题与待纠正观点

| 对话中的问题 / 观点 | 覆盖位置或处理方式 |
| --- | --- |
| PHY、SerDes 是什么？ | 01：端到端路径和概念边界；不能用某个协议的 PCS/PMA 划分代替所有实现。 |
| 差分、skew、PLL、FFE、CTLE、DFE、CDR、采样与解串是什么？ | 02—04：每项都有位置、输入输出、机制、例子和限制。 |
| 为什么普通数字逻辑不一定能跟上线速率？翻转是什么意思？ | 01、02、03：区分线速率、器件速度、路径时序、摆幅和多相结构；不把某个频率断言为数字电路的通用上限。 |
| 自研需要哪些设计点？怎样才算实际可用？ | 07：需求与证据链；样片、互通、生产测试和可靠性分开。 |
| 224G 是什么？协议、调制、速率和插入损耗有何关系？ | 01、02、05、08：先定义比特率、符号率和参考频点；厂商具体产品和“最高速率”必须按查询日期与来源重核。 |
| 为什么不一直增加 lane？ | 01、06、08：比较岸线、功耗、封装、通道、对齐和协议开销；不能说多 lane 没有 skew。 |
| chiplet 间是否需要 SerDes？3D 堆叠怎样通信？ | 08：以具体接口和物理路径作比较，不用距离单独决定答案；明确 HBM 栈内与对外接口。 |
| 链路训练是什么？ | 01 提供基本作用，06 分协议解释协商、训练与自适应，不承诺统一步骤。 |

原对话另有几处不能直接搬入正文：

1. `32 bit × 156 MHz` 在每周期一个字的假设下是 `4.992 Gb/s`，不是 `10 Gb/s`；除非另有数据边沿或位宽条件。
2. 加扰、线路编码与调制是不同概念。加扰对负载序列的统计改善，不能直接等同于确定的最长无跳变保证。具体 64b/66b 格式还可能包含不经加扰且自身有跳变的同步头；必须分别检查完整线码、所处位置和规范条件。[S15](#s15)、[S16](#s16)
3. PAM4 的符号包含两个比特；与编码开销、应用有效数据率是不同层次。不能把符号率、比特率和时钟频率当成同一个量。[S4](#s4)
4. 低误码率不是“链路已跑通一次”就能证明；测量、统计假设、置信度及误码位置都需要记录。[S12](#s12)

## 9. 内容质量与验收

### 9.1 第一阶段完成条件

1. 专题首页和四章首页存在；22 篇正文按依赖顺序可达，文章的上级、相邻入口、导航名称一致。
2. 每篇都有明确问题和适用条件；解释关键模块时给出输入、输出、职责及过程，不只列术语。
3. 第 5 节同一案例的位序、数据率、单位、抽头和初始条件在各篇一致。例子、图解和正文不互相矛盾。
4. 至少覆盖第 5 节四类图解；图解有文字替代，标明简化假设，不伪装成仿真或测量。
5. 第一阶段的术语、符号和资料有维护入口；每个重要事实、外部数据和特定实现都有可追溯依据。
6. 保留下面的自测及反例。正文必须足以独立回答，不以“见其他文章”代替必要解释。
7. 本地页面接入时检查站点构建、导航、面包屑、链接和窄屏显示；构建通过只证明所检查的文档 / 网站行为。

### 9.2 自测与反例

1. 已知每周期输入 `32 bit`、时钟 `312.5 MHz`，串行接口在什么假设下为 `10 Gb/s`？如果每周期有空闲，结果怎么变？
2. 同一时刻 `VP = 0.65 V`、`VN = 0.45 V`，差模电压和共模电压各是多少？两线同时增加 `0.1 V` 会怎样？若只增加 P 端呢？
3. 已知一条链路的 UI 与 lane 间到达时间差，如何换算相差多少 UI？为什么还不能仅据此认定整个链路必然成功或失败？
4. 通道损耗写为 `−20 dB` 时，要问哪些参考条件，才能解释它表示什么？为什么不能只凭这一个数字得到 BER？
5. 用第 5 节抽样模型计算两次不同历史下的接收值，并说明当前模型是否必然误码。
6. TX FFE 与 RX CTLE / DFE 分别在何处处理什么？为什么系数越大不一定越好？
7. 连续没有跳变时，CDR 为什么可能失去新的相位信息？PLL 锁定、CDR 锁定和字边界对齐为何不是同一个状态？
8. 如果上一个符号判错，DFE 下一步会发生什么？这个结果是否意味着所有 DFE 实现都会永久出错？
9. 一条 lane 已恢复串行数据后，多 lane 链路为什么仍可能需要对齐？
10. 波形示意、行为仿真、样片测量和协议互通分别能支持什么结论？

通过自测或文档检查，只能说明检查覆盖的内容符合预期；不能据此宣称 RTL、版图、电路、硬件或产品性能已被验证。

## 10. 资料起点

以下资料在规划阶段用于确定主题和技术边界。厂商手册描述其指定产品或实现；正式正文要按章节、版本与条件引用，不能把其数值推广为通用规格。

<a id="s1"></a>
**S1. 收发器与协议接口**：[TI Processor SDK：SerDes](https://software-dl.ti.com/jacinto7/esd/processor-sdk-linux-am67/latest/exports/docs/linux/Foundational_Components/Kernel/Kernel_Drivers/SERDES/SERDES.html)。用于串并转换、协议复用与 IP 能力边界；适用 TI 指定 SoC。

<a id="s2"></a>
**S2. RX 模块实例**：[AMD Versal GTY Transceivers：Receiver](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/Receiver)。用于 RX 模块、数据和时钟路径的实例；不是所有 SerDes 的固定框图。

<a id="s3"></a>
**S3. 具体 PCS/PMA 划分**：[AMD 1000BASE-X PCS/PMA](https://docs.amd.com/r/en-US/pg138-axi-ethernet/PCS/PMA)。用于指定以太网实现的编码、串并转换和时钟恢复边界。

<a id="s4"></a>
**S4. 比特、符号和 UI**：[Keysight：Understanding Signal Parameters](https://helpfiles.keysight.com/scopes/FlexDCA-UG/Content/Topics/Quick-Start/FlexDCA-fact-6.htm)。用于 NRZ / PAM4 的 bit、symbol、baud 和 UI 定义；计算时仍需核对具体接口口径。

<a id="s5"></a>
**S5. 差分与传输线**：[TI：Suggestions for High-Speed Differential Connections](https://www.ti.com/lit/an/slla104a/slla104a.pdf)。用于差分连接、平衡、终端和反射的入门；需区分理想与实际扰动。

<a id="s6"></a>
**S6. 多 lane 对齐实例**：[Intel：Implementing the SERDES Framer](https://cdrdv2-public.intel.com/654332/an571.pdf)。用于指定 SFI-5.1 实现中的 lane 间 skew 和 deskew；其预算不是 PCIe 或其他协议的通用参数。

<a id="s7"></a>
**S7. 反射**：[TI：Reflections and How to Deal with Them](https://www.ti.com/document-viewer/lit/html/SSZTAX3/GUID-2D2CAEAA-D7FA-43E3-8CAD-78D810632034)。用于理解阻抗不连续与反射；计算例子需明确模型和观察点。

<a id="s8"></a>
**S8. 通道指标**：[Keysight：Measurement Parameters](https://helpfiles.keysight.com/csg/pxivna/S1_Settings/Measurement_Parameters.htm)。用于 S 参数及插入、回波损耗的概念；差分转换、参考阻抗和去嵌条件须另行定义。

<a id="s9"></a>
**S9. PLL**：[Analog Devices：Fundamentals of Phase Locked Loops](https://www.analog.com/media/en/training-seminars/tutorials/MT-086.pdf)。用于反馈、鉴相、滤波、VCO 和分频的基础模型；不代表全部 PLL 实现。

<a id="s10"></a>
**S10. 发送与接收均衡实例**：[Analog Devices：ADRV904x SerDes Tuning](https://www.analog.com/cn/resources/app-notes/an-2594.html)。用于特定器件的 TX 摆幅 / 预加重及 RX CTLE/DFE 调整，不把该器件调参流程当成通用标准。

<a id="s11"></a>
**S11. 时钟与数据恢复**：[Analog Devices：Precision Reference Clock Usage in CDR Circuits](https://www.analog.com/en/resources/technical-articles/hfta070-precision-reference-clock-usage-in-clock-and-data-recovery-circuits.html)。用于链路与 CDR 的参考时钟、反馈和误差；不同 CDR 架构需分别说明。

<a id="s12"></a>
**S12. BER 与测试时间实例**：[Keysight N5990A-101 PCIe Test Automation User Guide](https://www.keysight.com/ng/en/assets/9018-04428/user-manuals/9018-04428.pdf)。用于指定测试设置下的目标 BER、置信度与测试时间实例；统计假设及相关性须单独说明。

<a id="s13"></a>
**S13. PCIe 合规与互通**：[PCI-SIG：Seamless Transition to PCIe 5.0](https://pcisig.com/sites/default/files/files/PCI-SIG-Seamless_Transition_to_PCIe_5.0_in_System_Implementations_FINAL.pdf)。用于区分电气合规、LTSSM 压力测试和系统互通。

<a id="s14"></a>
**S14. UCIe 专题边界**：[UCIe Consortium：UCIe 3.0](https://www.uciexpress.org/specifications/ucie-3-0)。用于确认该版本涉及封装级物理层、协议和管理；详细时钟与信号实现应查对应规范正文。

<a id="s15"></a>
**S15. 数据转换与 CDR 测试**：[Tektronix：Clock Recovery Primer, Part 1](https://download.tek.com/document/65W_26023_0_Letter.pdf)。用于码型、转换密度及 CDR 测试的解释；不能把统计描述泛化成对所有协议与比特序列的绝对保证。

<a id="s16"></a>
**S16. 64b/66b 同步头实例**：[Altera：64B/66B Encoder and Transmitter State Machine](https://docs.altera.com/r/docs/683621/current/l-and-h-tile-transceiver-phy-user-guide/b/66b-encoder-and-transmitter-state-machine-tx-sm)。用于区分该 10GBASE-R 实现中未经加扰的 `01` / `10` 同步头与经加扰的负载；其他映射或后续处理应另查对应规范。

## 11. 第一阶段实施与自检记录

2026-11-11：已编写四章共 22 篇正文、专题与章节入口、术语和资料页、10 题自测，并加入 5 张静态教学图。当时第二、第三阶段尚未编写。

本次自检覆盖：

- 核对第一阶段目录、正文数量、相对链接、后续阅读名称和 SVG 结构；网站暂存不包含本规划稿和原始 Claude 对话记录。
- 复核贯穿案例的位序、速率、UI、FFE / ISI、反射、dB 和时钟漂移计算。
- 使用本地 `workload-wiki` 来源执行 `website/prepare.py` 和 `mkdocs build --strict`；执行 `python -m unittest discover -s website/tests`，8 项测试通过。
- 抽查桌面与 390 px 窄屏页面、导航、图解横向滚动、键盘操作和自测答案展开。图解可点击查看原图。

这是作者自检，不是独立专家验收。正文使用的数值例子和图解是教学模型；本次未进行电路仿真、RTL 验证、芯片测量或公开网站部署。

## 12. 第二阶段实施与自检记录

2026-11-11：已编写 05、06 两章共 10 篇正文及章节入口，增加第二阶段术语、资料和 9 题自测，并加入 3 张静态教学图。专题首页、现有 PCIe 案例、站点导航和搜索索引均有对应入口。当时第三阶段仍为规划。

本次作者自检包括：

- 参考器件手册、测量厂商资料和 PCI-SIG 资料，分别核对 PAM4、64b/66b、眼图、BER、FEC、10GBASE-KR、lane 对齐和 PCIe 案例的适用边界。
- 检查新文章及相关入口的本地链接、搜索索引、章节顺序、导航高亮、面包屑、SVG 结构，以及 BER、带宽、电平间距和能耗例子的算术。
- 使用本地 Workload Wiki 来源执行严格网站构建和网站测试；抽查桌面及 `390 px` 窄屏页面、搜索和图解键盘滚动。

这些检查属于作者自检，不是独立专家验收。本文中的训练、误码和眼图例子是教学模型；没有进行 RTL、电路仿真、芯片测量、协议合规测试或公开网站部署。

## 13. 第三阶段实施与自检记录

2026-11-11：已编写 07、08、09 三章共 16 篇正文及章节入口，补充符号与单位、第三阶段术语、资料和 12 题自测，并加入事件时间线图。专题首页、PCIe 建模、HBM 和 CPO 原有内容均增加对应入口。

本次作者自检覆盖：

- 核对 [IBIS 6.1](https://ibis.org/ver6.1/ver6_1.pdf)、[PCI-SIG 合规项目](https://pcisig.com/developers/compliance-program)、UCIe 联盟及指定厂商资料的适用范围；产品页按厂商声明与待验证条件分别记录。
- 复算 224G PAM4 速率、HBM 与多 lane 带宽、光功率预算及能耗；另以小型事件队列复算无恢复、`2 μs` 恢复、零时长恢复和容量背压案例。
- 检查 SerDes 全部正文及新增跨专题入口的相对链接、章节顺序、SVG 结构和新文章搜索索引；执行严格网站构建和 8 项网站测试。
- 抽查桌面与 `390 px` 页面、导航高亮、面包屑、搜索、自测展开和图解键盘滚动。

这些是作者自检，不是独立专家验收。事件模型与图解为教学假设；没有进行 RTL、电路仿真、实物测量、协议合规或互通测试，也没有公开部署。
