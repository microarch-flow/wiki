# Common Misconceptions：软件背景人的常见误区

## 前置知识

- 建议先读 [完整生命周期](../00_overview/01_full_lifecycle.md)。
- 建议先读 [软件背景人在前端容易踩的坑](../02_frontend_design_and_verification/09_software_engineer_pitfalls.md)。
- 建议理解 [C Model](../00_overview/05_glossary.md#c-model)、[RTL](../00_overview/05_glossary.md#rtl)、[Signoff](../00_overview/05_glossary.md#signoff)、[Tapeout](../00_overview/05_glossary.md#流片-tapeout)、[Respin](../00_overview/05_glossary.md#respin)。

## 误区一：C model 正确，RTL 就只是翻译

C model 是功能和架构探索工具，不完整表达并行时序、资源冲突、背压、复位、CDC、低功耗、物理时序和测试结构。RTL 不是“把 C 语句翻译成 Verilog”，而是定义时钟边界上的硬件状态和组合逻辑。

用 agent 从 C model 生成 RTL 是有价值的，但必须把 agent 当成代码生成器，不是硬件工程师。生成结果要经过 lint、CDC/RDC、synthesis、formal/仿真、coverage、DFT、STA 和 code review。否则你只是把软件层面的未定义假设快速固化成硬件 bug。

错误后果：仿真在理想 testbench 下通过，但综合后出现 latch、combinational loop、multi-driver、timing failure 或 reset bug。更糟的是，bug 在硅上表现为随机 hang，无法通过日志快速定位。

## 误区二：仿真通过就能流片

软件测试通过通常意味着可以进入发布候选；芯片仿真通过只是验证证据的一部分。还要看 coverage 是否覆盖关键状态，assertion 是否定义协议不变量，formal 是否覆盖难枚举状态，CDC/RDC 是否 clean，DFT 是否可测，STA 是否收敛，DRC/LVS 是否 clean。

芯片 signoff 是多维证据集合，不是一个 test suite 的绿色勾。尤其是 AI SoC，很多 bug 出现在长时间运行、低概率 arbitration、backpressure、功耗状态切换、复位释放、host interface 和 firmware 交互中。

错误后果：tapeout 前发现物理时序或 DFT 不可接受，项目延迟；或者带着 waiver 流片，硅后无法判断是设计 bug、测试问题还是物理问题。

## 误区三：硬件也可以像软件一样快速修

软件发布可以回滚、热修复、灰度和日志定位。芯片 tapeout 后，修复路径可能是 firmware workaround、driver 限制、compiler 避免、熔丝配置、test 筛选、metal ECO 或 full respin。越靠近物理制造，成本和周期越高。

这不意味着硬件不能迭代，而是迭代粒度和反馈周期不同。正确做法是把可变性放在软件、firmware、microcode、配置寄存器、debug hooks、可编程数据路径和编译器策略中，把不可变硬件做到足够稳。

错误后果：团队为了赶首版把 debug、DFT、safe mode、error register 删掉。硅后发现问题时，没有观测和绕过手段，只能猜或 respin。

## 误区四：开源和自动化可以绕过商业生态

开源 RTL、开源编译器、OpenROAD、OpenLane、开放 PDK 都很重要，但先进节点量产仍受商业 PDK、EDA signoff、IP、foundry、封装、测试和客户质量要求约束。开源降低门槛，不消除制造现实。

全栈开源也不等于所有文件公开。PDK、商业 IP、SRAM compiler、PHY hard macro、timing library、rule deck、GDS signoff collateral 通常受 NDA 限制。你需要设计公开 repo 和私有 signoff repo 的边界。

错误后果：对外承诺“全部开源”后，发现关键制造文件不能公开；或者公开代码无法对应实际硅片，客户对透明度产生质疑。

## 误区五：外包可以解决自己不懂的问题

外包能补执行能力，不能补判断力。你可以外包后端、DFT、封装、测试、FA 和部分 turnkey，但你必须知道验收标准、风险边界、waiver 含义和客户承诺。否则供应商交付了合同项，产品仍可能失败。

软件外包失败通常还能重构；芯片外包失败可能意味着 tapeout 延误、硅后不可调、良率低、责任边界模糊。尤其是把不成熟 RTL 交给 turnkey，希望供应商“帮忙做成芯片”，这是高风险反模式。

错误后果：GDS 按时交付，但 bring-up 失败；供应商说输入 RTL/constraint 有问题，内部说供应商 signoff 不严格，责任无法界定。

## 误区六：第一颗芯片要证明所有愿景

创业者容易把第一颗芯片做成融资叙事的全集：先进节点、全栈开源、高性能 AI、复杂软件栈、量产收入、生态平台。问题是目标过多会让失败不可归因。失败时你不知道是架构、RTL、验证、节点、IP、封装、软件、客户还是供应链的问题。

第一颗芯片更应该验证最关键假设：目标 workload 是否有价值，架构是否有效，生成/验证 flow 是否可控，软件栈能否跑通，团队能否走完整 flow，客户是否愿意试用。

错误后果：V1 过大过复杂，资金和时间被消耗在非核心风险上；最终既没有稳定产品，也没有清晰学习。

## 典型流程场景

一个软件背景团队从 C model 生成 NPU RTL，用仿真证明几个算子输出正确，然后认为可以推进 tapeout。评审后发现没有 CDC 策略、没有 reset plan、没有 DFT 架构、没有真实 SDC、没有后端 trial、没有 software bring-up plan。正确纠偏是把项目退回工程化阶段：定义 clock/reset/power domain，建立 lint/CDC/synthesis smoke test，写 block verification plan，设计 debug/DFT，做小规模后端试跑，再决定 tapeout scope。

## 成本视角

这些误区的共同成本不是“多写点代码”，而是把便宜阶段的问题拖到昂贵阶段。需求阶段纠正可能是几天讨论；RTL 阶段纠正可能是数周；后端阶段纠正可能是月级；tapeout 后纠正可能是百万美元级 NRE 和数月机会成本；客户现场纠正还会损害信誉。

## 后续阅读

- [关键思维转换](./02_critical_mindset_shifts.md)
- [第一颗芯片务实建议](./04_first_chip_pragmatics.md)
- [快速迭代真实约束](./05_fast_iteration_realities.md)

## 参考公开来源

- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [CHIPS Alliance about page](https://www.chipsalliance.org/about/who-we-are/)

## 内容可信度说明

- **公开信息（高可信）**：C model、RTL、signoff、tapeout、respin、EDA/PDK/开源工具的基本边界。
- **行业惯例（中可信）**：仿真只是验证证据之一、外包不能替代验收标准、第一颗芯片应控制 scope。
- **经验性观察（中低可信）**：软件背景团队容易把“代码可生成”和“芯片可交付”混同，容易低估 debug/DFT/signoff/硅后成本。
- **不确定/需向资深工程师确认（低可信）**：具体团队能力、外包供应商能力、客户对 V1 的接受边界、不同节点下错误后移的真实成本。
