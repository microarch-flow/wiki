# 芯片项目成本结构总览

## 前置知识

- 建议先读 [01_full_lifecycle.md](./01_full_lifecycle.md)。
- 关键术语见 [05_glossary.md](./05_glossary.md)。

## 成本结构的核心观点

芯片成本分为一次性成本和单颗成本。一次性成本通常称为 [NRE](./05_glossary.md#nre)，包括人力、EDA、IP、验证、后端服务、mask、测试开发和认证。单颗成本包括晶圆、封装、测试、良率损失、物流、保修和库存。先进节点项目的危险在于：NRE 很高，且很多支出发生在收入之前。

软件创业常见的现金流模型是“先做 MVP、上线、迭代、增长”。芯片创业更像“先投入大量工程和供应链成本，数月到数年后才知道产品是否能规模销售”。因此成本结构必须在架构阶段就进入决策，而不是 tapeout 前才算账。

## 人力成本

人力通常是最大且最早发生的成本之一。一个完整 ASIC 项目需要架构、RTL、验证、DFT、后端、模拟/IP 集成、软件、硅后、测试、项目管理和供应链。先进 AI SoC 如果自研范围大，几十到数百名工程师并不罕见。创业公司可以缩小第一颗芯片范围，但不能把验证、DFT、后端判断和硅后准备完全省掉。

省钱方式是缩小功能、复用 IP、购买成熟接口、减少工艺冒险、使用 MPW 或 shuttle 做风险验证。不能省的是关键规格评审、验证计划、DFT、时序和物理 signoff。

人力成本还有一个容易被低估的部分：等待成本。后端等待 RTL freeze，验证等待 spec 澄清，软件等待可运行模拟器，硅后等待 board 或测试程序，这些都在消耗 runway。创业公司要把依赖关系管理当作成本控制手段。

## EDA 工具成本

[EDA](./05_glossary.md#eda) 成本包括仿真、综合、形式验证、lint/CDC、功耗分析、DFT、后端实现、STA、物理验证和版图相关工具。常见供应商包括 Synopsys、Cadence、Siemens EDA 和 Ansys。公开文档中，Synopsys Design Compiler 用于 RTL synthesis，Cadence Innovus 用于物理实现，Siemens Calibre 用于 DRC/LVS 等物理验证。

先进节点工具授权可能非常昂贵，且经常按 feature、token、时间、并发数、节点和支持服务收费。创业公司常见策略是通过云 EDA、孵化器计划、设计服务公司、foundry reference flow 或高校/开源路径降低早期成本。但商业 tapeout 不能假设开源工具能覆盖先进节点 signoff。

EDA 成本不仅是 license 报价，还包括工程师是否会用、flow 是否稳定、工具版本是否与 PDK 匹配、vendor support 是否及时、回归计算资源是否足够。便宜但无人会用的工具链，可能比昂贵但成熟的 flow 更贵。

量级上，商业 EDA 通常按年度授权、seat、token、feature、节点和并发量计价。单项工具可能从数万美元到更高量级，完整先进节点 flow 的年度成本对初创公司可能达到显著现金压力。具体价格高度依赖商务谈判、startup program、云服务、foundry package 和是否通过设计服务公司使用工具，因此不应把公开传闻当报价。

## IP 成本

[IP](./05_glossary.md#ip) 成本包括 CPU core、DDR/HBM controller/PHY、PCIe/CXL/Ethernet、NoC、安全模块、PLL、SerDes、eFuse、SRAM compiler、标准单元库、IO library、验证 IP 和软件驱动。授权模式可能包括 upfront license、per-project fee、royalty、maintenance、source access fee 和 foundry/node 限制。

创业公司常犯错误是只看 IP license，不看集成成本。一个高速接口 IP 的真实成本还包括验证环境、仿真模型、DFT 支持、后端约束、封装/板级 SI、firmware、bring-up 支持和供应商响应速度。

如果第一颗芯片的核心差异化不在 PCIe、DDR、SerDes 或 PLL，上来就自研这些 IP 通常风险很高。自研可以降低长期 royalty 或形成壁垒，但需要人才、验证、后端、硅后和客户兼容性成本。购买 IP 则要警惕黑盒限制、版本锁定、node 限制、开源发布限制和 vendor support 质量。

量级上，复杂商业 IP 常见计价方式包括一次性授权费、项目授权、按节点收费、royalty、维护费和支持费。简单软 IP 可能是较低成本或开源授权，高速 PHY、HBM/DDR、PCIe/CXL 等先进接口 IP 可能达到数十万到数百万美元量级，并且集成和验证人力可能接近或超过授权费。

## Mask cost 与流片成本

[Mask Cost](./05_glossary.md#mask-cost) 是把版图制造成光罩/掩模版的成本。先进节点需要更多 mask、更复杂的 OPC、EUV 相关步骤和严格工艺控制，因此成本显著高于成熟节点。公开行业报道和研究中，7nm 级别 full mask 常被描述为百万美元量级，5nm/3nm 可能更高；不同 foundry、节点、层数、商务关系和是否 full mask 会造成巨大差异。

[MPW](./05_glossary.md#mpw-multi-project-wafer) 可以摊薄 mask 成本，适合验证小面积原型或 IP，但不适合所有大芯片，尤其是大 die、HBM、高级封装或需要完整量产评估的项目。

Mask 成本的管理方式不是简单选择便宜节点，而是控制“每次硅反馈要验证什么”。如果一次 full mask 同时验证新架构、新编译器、新接口、新封装和新工艺，任何一个环节失败都会让整次投入价值下降。

## Wafer、封装与测试成本

晶圆成本取决于节点、wafer size、die size、良率、产能和客户关系。CSET 2020 年 AI 芯片成本模型曾估算 7nm 和 5nm 晶圆价格分别在约 9k 和 17k 美元量级；这些数字是公开历史模型，不应当当作当前报价。2026 年实际商务价格可能因 foundry、地区、产能和客户承诺差异很大。

封装成本取决于封装形式。普通 organic substrate BGA 与 2.5D interposer、CoWoS、HBM 堆叠完全不是一个成本层级。AI 芯片若绑定 HBM，HBM、interposer、基板、封装良率和供应优先级可能成为商业成败关键。

测试成本包括 wafer sort、final test、ATE 时间、probe card、load board、handler、温度测试和测试程序开发。测试时间越长，单颗成本越高。DFT 做得差会导致测试覆盖率低或测试时间过长，最终影响良率和毛利。

量级上，普通封装与先进封装不是同一成本层级。成熟 BGA 类封装可能主要由基板、封装厂加工和测试流程决定；2.5D、interposer、CoWoS、HBM 堆叠会引入更高封装 NRE、材料、良率和产能风险。测试也有 NRE 和单颗测试时间两部分：probe card、load board、test program 开发是前期投入，ATE 按秒或按测试时间消耗形成单颗成本压力。

## 良率与单颗成本

单颗硅成本不是 wafer price 除以理论 die 数那么简单。必须考虑缺陷密度、die size、边缘损失、封装良率、测试良率和 binning。大 die AI 芯片对良率非常敏感，因为 die 面积越大，单颗包含缺陷的概率越高。Chiplet 可以改善部分良率问题，但引入封装、互连、测试和供应链复杂度。

简单公式是：可销售单颗成本约等于晶圆成本除以良品 die 数，再加封装、测试、物流和库存成本。更完整模型还要加入报废、RMA、现场支持和价格折扣。

良率学习也是时间成本。首批硅片低良率不一定意味着设计失败，但如果没有足够 DFT、测试 bin、失效分析和工艺数据，团队就不知道问题来自设计、制造、封装还是测试程序。

## 软件和实验室成本

AI 芯片的商业化成本还包括软件栈。编译器、runtime、driver、firmware、kernel library、profiler、debugger、SDK、文档和 CI 都需要持续投入。硬件 tapeout 后才开始补软件，通常会导致客户 demo 延迟。

实验室成本包括 bring-up board、电源、示波器、逻辑分析仪、协议分析仪、热箱、ATE 开发支持、样片管理和安全库存。它们单项可能不如 mask 显眼，但如果准备不足，会让首硅回来后无法快速定位问题。

量级上，实验室设备和板卡可能从数万美元到更高量级，取决于高速接口、功耗、温控和协议分析需求。对 AI 芯片，开发板、电源完整性、散热和高速链路调试设备不能等首硅回来后再临时采购。

## 典型成本决策场景

创业团队想做 5nm AI 芯片，因为性能更好。财务测算发现，5nm 的 EDA、IP、mask、晶圆、封装和工程经验要求都高于 12/16/28nm。若目标客户愿意为能效付高价，且软件栈能释放性能，先进节点可能合理。若第一颗芯片主要用于验证架构和开发者生态，成熟节点或 MPW 原型可能更务实。

错误决策的后果是：现金消耗在首颗芯片上过大，还没完成客户验证就耗尽 runway。另一种错误是为了省 IP 授权自研 PCIe/DDR，结果外围接口拖垮项目，核心 NPU 反而没有机会被客户验证。

## 创业公司成本取舍

可以省钱的地方：缩小第一颗芯片范围，减少高速接口数量，购买成熟 IP，避免不必要的先进封装，使用 MPW 验证关键 IP，外包部分后端执行，采用云资源做峰值仿真回归。

不能省钱的地方：关键验证、DFT、CDC/RDC、STA、DRC/LVS、IR drop、硅后 debug 能力、IP 法务审查、foundry/OSAT 交付管理。这里省掉的钱往往会以 respin、客户失败或量产良率问题的形式回来。

## 后续阅读

- [04_startup_vs_bigcompany.md](./04_startup_vs_bigcompany.md)
- [../01_product_definition_and_architecture/04_ip_strategy.md](../01_product_definition_and_architecture/04_ip_strategy.md)
- [../06_cross_cutting_topics/04_mpw_shuttle_strategy.md](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)
- [../06_cross_cutting_topics/05_turnkey_services.md](../06_cross_cutting_topics/05_turnkey_services.md)

## 参考公开来源

- [CSET: Why AI Chips Matter](https://cset.georgetown.edu/publication/why-ai-chips-matter/)
- [CSET 相关 5nm wafer cost 摘要报道](https://www.techspot.com/news/86813-analysts-believe-single-tsmc-5nm-wafer-costs-17000.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/content/cadence-www/global/en_US/home/tools/digital-design-and-signoff/hierarchical-design-and-floorplanning/innovus-implementation-system.html)
- [Synopsys Design Compiler](https://www.synopsys.com/Tools/Implementation/RTLSynthesis/DesignCompiler/Pages/default.aspx)
- [Siemens Calibre Physical Verification](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/)

## 内容可信度说明

- **公开信息（高可信）**：NRE/wafer/package/test/IP/EDA 的成本分类，CSET 公开 AI chip cost model 中的历史晶圆成本估算，Synopsys/Cadence/Siemens 工具用途。
- **行业惯例（中可信）**：先进节点 mask 百万到千万美元量级、EDA/IP 商务复杂度、封装和测试成本构成。
- **经验性观察（中低可信）**：创业公司省钱策略、第一颗芯片节点选择思路、DFT 与测试成本的连锁影响。
- **不确定/需向资深工程师确认（低可信）**：当前 foundry 实际报价、具体 IP 授权条款、先进封装产能价格、特定节点良率模型。
