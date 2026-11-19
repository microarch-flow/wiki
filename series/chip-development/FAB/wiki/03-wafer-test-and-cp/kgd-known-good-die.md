# KGD 的筛选判据与残余风险

<span class="micro-legacy-anchor" id="kgdhbm3dic-时代的必要前提"></span>

上级：[晶圆筛测与 CP](README.md)
相关：[CP 测试流程](cp-test-methodology.md) · [W2W 与 D2W](../04-back-end-packaging/3d-routes/w2w-vs-d2w.md) · [HBM 堆栈制造](../04-back-end-packaging/hbm-as-case-study/hbm-stack-manufacturing.md)

<span class="micro-legacy-anchor" id="kgd-的真实含义"></span><span class="micro-legacy-anchor" id="为什么多-die-封装放大-kgd-价值"></span><span class="micro-legacy-anchor" id="d2w-为什么依赖-kgd"></span><span class="micro-legacy-anchor" id="kgd-的难点"></span>

## 这页在回答什么问题

多裸片组装为什么需要约定裸片的接收判据？组装前筛到的缺陷和只能在组装后测到的问题应怎样承接？

## 什么是 KGD

KGD（known-good die）指按规定的测试和分档结果，可接收进入后续工序的裸片。报告应注明对象、测试条件、通过项目、未检查范围和批次标识。通过品仍有残余缺陷风险。组装还可能产生新的连接或机械问题。 [OCP 芯粒测试流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 为什么 KGD 对 2.5D/3D 重要

组装时可能一次投入多颗裸片、堆栈和载体。若一颗坏片直到组装后才检出，可能损失已投入的其他良品及工序费用。用各对象在规定筛选条件下的真良比例估算，核对批次相关性和后续缺陷。详细分母与算例见[跨阶段良率与单位交付成本](../06-cross-cutting-engineering/yield-economics-across-stages.md)。

## W2W 和 D2W 对 KGD 的不同

D2W 能挑选和贴装单颗已筛裸片。W2W 整片对准键合，需考虑可用的晶圆图、位置配对与坏点相关性。用实际制造路线评估测试、选择与报废范围。 [W2W 与 D2W](../04-back-end-packaging/3d-routes/w2w-vs-d2w.md)

## HBM 场景里的 KGD

裸片、已筛 HBM 堆栈和子装配体是不同的接收对象。每件对象有独立的识别、测试条件和残余风险。后段使用已筛堆栈的条件概率，避免再次计入内部裸片的同一次筛选。供应商举例列出了不同生产阶段的探针和访问方式，具体能力与器件和设备匹配。 [FormFactor 的 HBM 与 KGD 测试](https://www.formfactor.com/blog/2024/known-good-die-test-enables-advanced-packaging-high-bandwidth-memory/)

## KGD 需要哪些条件

在设计阶段明确需要的电性、逻辑、存储和接口测试。探针接触、电压、温度和设备速度限制可测范围。若晶圆阶段不能完整测试某条高速连接，可以通过片上 loopback 或 BIST 补一部分。用中间测试或终测覆盖组装后的实际互连，并记录剩余风险。

<span class="micro-legacy-anchor" id="常见误解"></span><span class="micro-legacy-anchor" id="架构师启示"></span>

## 一句话理解

KGD 记录裸片在指定条件下通过了什么，支持后续组装选择。封装后的成品仍需按规定判据检查。
