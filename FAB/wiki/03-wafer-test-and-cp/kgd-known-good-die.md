# KGD:HBM/3DIC 时代的必要前提

上级:[中测:CP 阶段](./README.md)
相关:[CP 测试的方法和典型流程](./cp-test-methodology.md), [Wafer-to-Wafer vs Die-to-Wafer:工艺与良率](../04-back-end-packaging/3d-routes/w2w-vs-d2w.md), [HBM stack 是怎么制造出来的](../04-back-end-packaging/hbm-as-case-study/hbm-stack-manufacturing.md)

## 这页在回答什么问题

KGD 为什么在 HBM、D2W、3DIC 和多 chiplet 封装中变成必要前提。它不是“测过的 die”这么简单，而是一个关于测试覆盖率、残余风险和后续封装价值的工程承诺。

## KGD 的真实含义

KGD，known-good die，指在进入后续高价值组装之前，已经通过足够测试并被认为适合继续投入的裸 die。这里的关键词是“足够”。不同产品的 KGD 标准不同：低成本单 die package 的封装前筛选可以较轻；高价值 HBM/3DIC package 的 KGD 需要更强的结构测试、存储测试、接口测试、binning 和风险管理。

KGD 不是绝对无缺陷。它的含义是：在当前测试覆盖率和风险模型下，残余 defect 低到值得进入后续 assembly。

## 为什么多 die 封装放大 KGD 价值

多 die package 的有效良率近似受到每个组成对象良率的乘法影响：

```text
package success
  ~= die_A_good
     x die_B_good
     x HBM_stack_good
     x interposer/substrate_good
     x assembly_success
```

这个公式不是精确模型，但能说明方向：对象越多、单个对象越贵、assembly 越不可逆，KGD 越重要。坏 die 漏进 package，不只是浪费自己，还会拖累其他 good die 和封装资源。

## D2W 为什么依赖 KGD

W2W 是 wafer-to-wafer，对规则、高良率、尺寸匹配结构有吞吐优势，但坏 die 可能在整片键合中被一起绑定。D2W 是 die-to-wafer，可以先切割和筛选 die，再把 KGD 贴到底层 wafer 上。D2W 的灵活性和良率优势来自 KGD；如果 KGD 不可靠，D2W 的经济性会明显下降。

这解释了为什么 3DIC 不只是 bonding 技术问题。bonding 再强，如果进入 bonding 的 die 残余 defect 过高，stack 后也会变成昂贵的报废品。

## HBM 场景里的 KGD

HBM stack 本身由多层 DRAM die、TSV、micro-bump 或其他连接、base die 和热机械结构组成。它进入 logic + HBM package 前，已经是一个高价值 3D memory component。HBM stack 的测试和筛选决定后续 2.5D package 的风险底线。

对 AI/HPC 系统，KGD 不只针对 compute die，也针对 HBM stack、I/O die、interposer module 或中间 assembly 阶段。每个对象都要尽量在进入下一层价值更高的组合前完成筛选。

## KGD 的难点

| 难点 | 为什么难 | 后果 |
| --- | --- | --- |
| 覆盖率有限 | wafer 环境无法完全模拟封装后电/热/接口条件 | residual defect 进入 assembly |
| 接口不可达 | D2D/HBM 接口封装前不完整 | 高速链路 defect 后移暴露 |
| 测试时间昂贵 | 高覆盖率需要更多 tester time | 成本与产能压力 |
| bin 匹配复杂 | 多 die package 需要速度/功耗/电压匹配 | SKU 和 assembly planning 复杂 |
| 失效隔离困难 | stack 后内部节点不可见 | debug 和 yield learning 变慢 |

## 常见误解

常见误解是“KGD 等于 CP pass”。实际 CP pass 只是 KGD 的输入之一。KGD 还包含覆盖率定义、binning、repair 状态、接口测试、残余风险和后续封装价值判断。

另一个误解是“用了 KGD 就解决多 die 良率”。KGD 降低坏 die 进入 assembly 的概率，但不能消除 bonding defect、interposer defect、substrate defect、warpage 和 package-level SI/PI 问题。

## 一句话理解

KGD 是把 die 带入高价值封装前的风险承诺；封装越复杂、对象越贵，KGD 的覆盖率和可信度越关键。

## 架构师启示

如果我把一个大 SoC 拆成 6 个 chiplet，理论上每个 chiplet 前道良率会提高，但 KGD 管理会变成新成本。每个 chiplet 必须可测、可 bin、可追踪，D2D 接口必须有 wafer-level 或 pre-assembly 覆盖，否则封装阶段会成为 defect 放大器。

一个具体决策例子：若两个 chiplet 之间需要极高带宽接口，架构师应优先选择支持 wafer-level loopback/BIST 的 D2D PHY，即使它有少量面积开销。这个开销可能比 package 后才发现坏 link 的报废成本低得多。
