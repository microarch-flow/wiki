# 晶圆筛测与 CP

<span class="micro-legacy-anchor" id="中测cp-阶段"></span>

上级：[FAB 制造与封测](../README.md)

<span class="micro-legacy-anchor" id="本章文件关系"></span><span class="micro-legacy-anchor" id="测试前移的核心逻辑"></span><span class="micro-legacy-anchor" id="一句话理解"></span><span class="micro-legacy-anchor" id="架构师启示"></span>

## 这页在回答什么问题

芯片还在晶圆上时，可以用探针和测试设备测量及筛选每颗裸片。CP 按产品规定输出分档和晶圆图，供后续切割、组装、筛选和分析使用。工艺参数监控、中间组件测试与成品终测涉及其他对象或条件。

## CP 在整条链路中的位置

设计提供测试访问、时钟、模式、向量或自测功能。晶圆测试根据探针、设备、时间和温度限制执行。已达到规定筛选条件的裸片可作为后续组装候选。组装仍可能引入缺陷，需要适用的中间检查和终测。 [可测性设计与制造测试](../../../process/02_frontend_design_and_verification/05_dft_introduction.md) · [OCP 多芯粒测试流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

<span class="micro-legacy-anchor" id="本章正文"></span>

## 阅读顺序

1. [晶圆筛测为什么前移](why-wafer-sort-exists.md)说明组装前先筛的价值与限制。
2. [CP 测试流程](cp-test-methodology.md)核对访问、测试项目、分档和晶圆图。
3. [KGD 的筛选判据与残余风险](kgd-known-good-die.md)定义已筛裸片的接收范围。
4. [测试覆盖与成本](test-cost-vs-coverage-tradeoff.md)区分故障模型、漏检和过杀。

接着可读[成品终测](../05-final-test-and-reliability/final-test-methodology.md)和[良率、缺陷密度与面积](yield-and-defect-density.md)。前者讲组装后的判据。后者讲如何解释分母和随机缺陷。
