# RAM 家族的分类与命名体系

<span id="这页在回答什么问题"></span>
<span id="区分单元组织接口角色和封装"></span>

上级：[系统视角](./README.md)

相关：[SRAM 与 DRAM 的分化](./sram-dram-divergence.md) · [DRAM 协议对比](../../03-dram/protocols/ddr-lpddr-gddr-hbm-tradeoff-map.md) · [存储层次与系统角色](memory-hierarchy-as-system.md)

<p class="ram-problem-lede">SRAM、cache、DDR 和 HBM 都与存储有关，但它们回答的问题不同：一个 bit 怎样保存、存储资源在系统里做什么、控制器怎样访问它，以及器件如何集成。先分清问题，才能正确描述一个系统。</p>

本文用五个观察角度整理常见名称，再用 DDR4 模块和 HBM2E 两个例子把它们连接起来。这些角度彼此有关，不代表每一项都可以任意组合。

## 1. 先看名称在回答什么问题

| 观察角度 | 要问的问题 | 例子 |
| --- | --- | --- |
| 存储单元与技术 | 数据靠什么物理状态保存？ | 6T SRAM cell、1T1C DRAM cell |
| 阵列与访问组织 | 单元怎样组成可访问的资源？ | SRAM bank、DRAM row 和 bank |
| 系统角色 | 这块存储在系统里负责什么？ | cache、scratchpad、register file、主存 |
| 接口与协议 | 请求、命令、数据和时序怎样在边界上传递？ | SRAM 宏接口、DDR4、LPDDR5、HBM2E 接口 |
| 封装与集成 | die、器件和计算芯片怎样连接到一起？ | BGA 器件封装、DIMM 模块、die 堆叠、interposer |

这些角度不是互斥的盒子。同一个对象可以同时具有多个属性；一个名称也可能横跨多个角度。例如，HBM 既涉及 DRAM、接口，也涉及堆叠和集成要求。

## 2. 存储单元与阵列：数据怎样保存和访问？

**RAM** 是 random-access memory，通常译为随机存取存储器。它允许根据地址选择存储位置，不需要从开头顺序经过更早的位置。这个名称不保证所有位置的访问时间相同，也不保证多个请求不会竞争同一资源。

本专题主要讨论易失性 SRAM 和 DRAM 中常见的两种单元：

- **6T SRAM cell**：用交叉耦合电路维持状态。满足供电和保持条件时，不需要 DRAM 式周期刷新。
- **1T1C DRAM cell**：用电容上的电荷表示状态。电荷会泄漏，需要按器件要求周期刷新；常见 DRAM 在 ACT 开行时感测并恢复该行，后续列读取可以访问已打开的行。

SRAM、DRAM 是存储技术名称；6T 和 1T1C 是常见单元结构，不是各自所有实现的完整清单。“随机存取”也不等于“断电后一定丢失数据”：例如，厂商提供非易失性的 [MRAM](https://www.everspin.com/products)。MRAM 不在本专题的主要范围内。

**SRAM 与 SDRAM 也不是同一个缩写。**SRAM 中的 S 表示 static；SDRAM 中的 S 表示 synchronous。SDRAM 是接口和命令与时钟同步的 DRAM，DDR4 和 DDR5 SDRAM 是其中的具体代际。[Micron 的 DDR5 说明](https://www.micron.com/content/micron/us/en/products/memory/dram-components/ddr5-sdram.html)介绍了 DDR5 与 DRAM、SDRAM 的关系。

另一个容易混淆的名称是 pSRAM（伪静态 RAM）。例如，[Infineon 的一种 pSRAM](https://www.infineon.com/products/memories/psram-pseudostatic-dram)使用 DRAM 存储阵列，并在器件内部处理刷新。主控不需要发出刷新命令，并不表示内部一定是 SRAM cell；具体行为仍以目标器件为准。

许多单元还要组织成阵列，并通过端口、译码和数据通路提供访问。一个 **bank** 通常表示某种可独立或相对独立管理的访问资源；它具体能否与其他 bank 并行，取决于共享的端口、控制和数据通道。SRAM bank 和 DRAM bank 的内部状态也不同，不能只因名字相同就假设行为相同。

## 3. 系统角色：谁管理数据？

同一类存储单元可以承担不同职责。角色描述的是系统怎样使用和管理数据，而不单是它由什么电路构成。

| 角色 | 在系统中的职责 |
| --- | --- |
| Cache | 在常见硬件管理的设计中，保存下一级数据的副本；硬件判断命中，并按策略填充或替换。 |
| Scratchpad | 提供显式管理的数据区域；软件、编译器或其他调度机制负责安排数据放置与使用。 |
| Register file | 为执行单元提供寄存器操作数，并接收结果写回。 |
| 主存或设备内存 | 为系统或设备提供较大范围的数据存放空间；具体可见性和用途由系统定义。 |

Cache 的数据阵列和 scratchpad **常用 SRAM 实现**，但角色名称本身不规定唯一的 cell 技术。角色怎样管理数据，以及它与实现技术如何对应，见[存储层次与系统角色](./memory-hierarchy-as-system.md)。

## 4. 接口与协议：两端如何交换数据？

接口定义边界上的信号或请求、响应及时序；协议进一步约束操作如何执行。片上 SRAM 宏也有接口，例如读写地址、使能、数据和对应的时钟边沿。它未必使用 DDR 或 AXI，但不能因此认为它“没有接口”。

在本专题中，讨论 DRAM 时经常遇到这些名称：

| 名称 | 需要先确认什么 |
| --- | --- |
| DDR4、DDR5 SDRAM | 所说的代际、器件或模块，以及对应的命令、时序与电气条件。 |
| LPDDR、GDDR | 具体代际与产品配置；它们是不同的 DRAM 接口与产品路线。 |
| HBM、HBM2E | 具体代际与配置；HBM 涉及堆叠 DRAM、接口和系统集成。 |

**DDR 的含义要看上下文。**“double data rate”可以描述在时钟或数据选通信号的两个边沿传输数据；“DDR4 SDRAM”“DDR5 SDRAM”则指具体的 DRAM 标准及产品家族。双倍数据率传输方式并非 DRAM 独有，[Infineon 也提供 DDR 同步 SRAM](https://www.infineon.com/products/memories/sram-static-ram)。因此，只看到“DDR”三个字，还不足以判断 cell 技术或接口的全部细节。

DDR4、DDR5、LPDDR、GDDR 和 HBM 的具体接口不能因为都涉及双倍数据率就视为兼容。比较时应查对应代际、器件和工作模式，而不是只按缩写推断。

## 5. 封装与集成：器件怎样进入系统？

下面几个名称处于不同的物理层级：

- **Die** 是制造在晶圆上、切割后的一块芯片。一个封装内可以包含一个或多个 die。
- **BGA** 等名称描述器件封装形式。日常所说的 DRAM“颗粒”通常指封装后的存储器件，不必然等于单个裸 die。
- **DIMM / SODIMM** 是内存模块形式。模块上可以装多个 DRAM 器件及其他所需组件；它不是单个 DRAM cell 或单个封装。
- **HBM stack** 描述堆叠的存储 die 及相关结构；**interposer** 则可用于在封装内连接 HBM 与计算 die。堆叠方式和系统集成方式应分别说明。

例如，同样是 DRAM，器件可以安装在 DIMM 上，也可以作为 HBM stack 的一部分集成到封装系统中。具体连接、可替换性和电气条件取决于实际产品，不由“DRAM”一词单独决定。

## 6. 例子一：一条 DDR4 DIMM 包含什么？

假设一个教学系统使用单 rank、非 ECC 的 DDR4 DIMM。这个 rank 包含 8 颗 x8 DRAM 器件，每颗容量为 8 Gibit；8 颗器件并行提供数据。这里的 `x8` 表示**单颗器件的数据位宽为 8 bit**，不是模块只有 8 bit 宽。

假设处理器的读取未在参与查找的 cache 中命中，简化的请求方向如下。图中省略互连和排队；数据沿返回路径送回处理器。

<ol class="ram-event-sequence" aria-label="简化的 DDR4 读取请求路径">
  <li>处理器</li>
  <li>cache</li>
  <li>内存控制器</li>
  <li>DDR4 channel</li>
  <li>DIMM 上的 rank</li>
</ol>

| 要描述的对象 | 本例中的含义 |
| --- | --- |
| 存储技术 | 每颗器件是 DRAM。 |
| 接口家族 | 控制器按 DDR4 接口与器件通信。 |
| Rank 与位宽 | 8 颗 x8 器件在本例中组成一个 rank，合计提供 64 bit 数据位宽。 |
| 模块形式 | 这些器件安装在 DIMM 上；DIMM 是模块，不是另一种 cell。 |
| 系统角色 | 在这个假设系统中，该模块承担主存角色。 |

按例子的容量口径，`1 Gibit = 2³⁰ bit`，`1 GiB = 2³⁰ B`：

<div class="ram-calculation">
  <span>模块数据位宽 = 8 颗 × 8 bit = <strong>64 bit</strong></span>
  <span>模块数据容量 = 8 颗 × 8 Gibit ÷ 8 = <strong>8 GiB</strong></span>
</div>

如果这个接口以 3,200 MT/s 传输，且每次传输的 64 bit 都是数据，则单方向理论数据率为 `3,200 × 10⁶ × 8 B/s = 25.6 GB/s`，这里 `1 GB = 10⁹ B`。这是数据引脚持续传输时的理论值，不计命令、刷新、读写切换或空闲造成的损失，也不是实测带宽。

这个组合是为了说明命名和计算边界，不是对实际系统的测量。[Micron 的一个 DDR4 UDIMM 产品资料](https://www.micron.com/products/memory/dram-modules/udimm/part-catalog/part-detail/mta8atf1g64az-3g2e1)列出了单 rank、x64、8 颗 x8 器件和 3,200 MT/s 等字段。不同模块可能有不同的 rank、器件位宽或 ECC 配置，不能把此例当作 DIMM 的统一组织。进一步的层级说明见 [Channel、rank 与 chip](../../03-dram/foundations/channel-rank-chip-hierarchy.md)。

## 7. 例子二：HBM 不只是一个封装名称

以 [Micron 的 HBM2E 技术说明](https://assets.micron.com/adobe/assets/urn%3Aaaid%3Aaem%3A275edf31-79e3-4b6c-8bbd-a233babe9281/original/as/micron-hbm2e-memory-wp.pdf)中的器件为例：

| 观察角度 | 该资料中的对象 |
| --- | --- |
| 存储技术 | 多层 DRAM die。 |
| 访问组织与接口 | 8 个独立 channel；每个 channel 有各自的命令、地址和数据接口。 |
| 堆叠方式 | DRAM die 通过 TSV 与底部接口 die 连接。 |
| 系统集成 | 资料展示了通过硅 interposer 连接 HBM2E 与计算 die 的封装系统。 |

这里的 8 个 channel 是该 HBM2E 资料的配置，不能套用到所有 HBM 代际。HBM 在某个系统中可以承担设备内存等角色，但“设备内存”描述用途，不等于“HBM”这个技术与接口名称。

因此，说“HBM 是 DRAM”是在说明存储技术；说“HBM 使用堆叠和封装集成”是在说明实现方式。这两句话可以同时成立，但都不能独自描述完整系统。

## 8. 怎样比较不同名称？

“HBM 比 SRAM 更先进吗？”没有给出比较目标、实现或约束，因此无法得到清楚的工程结论。但来自不同角度的对象并非不能比较：只要定义了实际系统和统一的指标边界，就可以比较它们的**具体实现**。

例如，在同一处理器上，可以测量同样大小的一笔读取，从发起到数据可用所需的时间：一次由指定的 L1 cache 命中满足；另一次在参与查找的 cache 均未命中后，由 HBM 返回。后一条路径包含互连、控制器、排队和数据返回等开销。结果反映的是这两条**系统路径**，不能直接当成 SRAM cell 与 DRAM cell 的电路延迟对比。

比较容量、带宽或能耗时也要说明观察位置、工作负载、器件配置和时间窗口。关于指标与约束，见[速度·容量·成本·功耗](./memory-hierarchy-tension.md)。

## 一句话理解

先问一个名称描述的是存储技术、资源组织、系统角色、接口协议，还是封装集成；再把同一系统中相关的属性连接起来。

## 建模启示

建模时，先确定对象边界。Cache 是有管理机制的系统资源；它的 tag 和 data 阵列可以进一步映射到具体存储实现。DRAM 器件、channel、控制器和连接它们的路径也不是同一个对象。

按需要记录角色、存储技术、组织、接口和集成方式，并明确它们之间的关系。例如，片上 SRAM 宏可以有自定义读写接口；如果接口信息未知，应标记为未知，而不是用“无接口”代替。若只做容量估算，可以暂时省略内部时序；若要研究 bank 冲突或 DRAM 调度，还需要地址映射、共享资源和相关状态。

这些分类有助于说明模型对象，但**名称本身不会给出延迟、带宽或正确的事件规则**。具体参数仍需来自目标规格、测量或明确的建模假设。

## 接下来怎么读？

- [速度·容量·成本·功耗](./memory-hierarchy-tension.md)：看不同实现如何在共同约束下取舍。
- [SRAM 与 DRAM 的分化](./sram-dram-divergence.md)：从存储方式继续看两条技术路线。
- [DRAM 协议对比](../../03-dram/protocols/ddr-lpddr-gddr-hbm-tradeoff-map.md)：比较不同 DRAM 路线的系统目标。
- [HBM 封装与 TSV](../../06-system-integration/packaging/hbm-2.5d-3d-tsv.md)：进一步看 die 堆叠和系统集成。
