# 推测解码：候选验证、分布保证与执行成本

<div class="inference-legacy-anchors" aria-hidden="true"><span id="09-投机解码-speculative-decoding"></span></div>

上级：[本专题导读](README.md)

推测解码先生成多个候选，再由目标模型验证，希望用一次较大的目标模型执行替代多次小执行。它能否加速取决于接受长度和额外成本；能否保持结果性质取决于接受算法。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="draftverify-流程"></span></div>

## Draft、verify 与提交

给定已提交前缀，草稿模型顺序提议 $\gamma$ 个候选。目标模型在正确的因果掩码下批量计算对应条件分布。验证器从第一个候选开始判断，遇到首个拒绝后停止接受该链的后续候选。

已接受 token 才能进入正式输出。候选的 KV、随机数消耗和语法状态需要区分暂存与提交；拒绝后必须回滚或丢弃无效后缀。全部候选接受时，算法还可以从额外的目标分布采样一个 token。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="rejection-sampling-的无损性为什么不掉质量"></span></div>

## 拒绝采样为什么可以保持分布

令目标分布为 $p$，草稿分布为 $q$。对从 $q$ 采得的候选 $x$，接受概率为：

$$a(x)=\min(1,p(x)/q(x))$$

若拒绝，则从归一化后的正残差采样：

$$r(x)=\frac{\max(0,p(x)-q(x))}
{\sum_v\max(0,p(v)-q(v))}$$

候选来自 $q$，所以被实际提议的 token 不会要求对零概率提议作除法。若 $p=q$，拒绝事件概率为零，残差分支无需执行。

例：$p=(0.6,0.4)$、$q=(0.8,0.2)$。第一类候选以 0.75 接受，第二类全部接受；拒绝后的残差只支持第二类。最终第一类概率为 $0.8\times0.75=0.6$，第二类为 $0.2+0.2=0.4$。

序列上的保证要求每个位置使用对应已接受历史下的条件分布，并正确实现拒绝与残差步骤。温度、截断和其他 logits 处理也必须与被比较的目标采样管线一致；数值实现仍需验证。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="变体都保持无损差别在怎么造更准的-draft"></span></div>

## 不同方案的保证不能混写

贪心验证可要求每个接受 token 与目标模型的 argmax 一致。上述拒绝采样保持目标采样分布。这两种性质又不同于“任务评测质量接近”。

Medusa 论文讨论的 typical acceptance 并不要求匹配原始目标分布；部分训练方案还会改变目标模型参数。因此不能把 Medusa、EAGLE、树候选和 lookahead 等名称统一标为“都无损”。应逐项说明候选来源、验证方式、目标模型是否变化和保证范围。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-期望产出与加速比leviathan-公式"></span></div>

## 接受率怎样进入成本模型

在每个位置的条件接受概率均近似为常数 $\alpha$ 的简化假设下，一轮期望提交 token 数为：

$$E[N]=1+\alpha+\cdots+\alpha^\gamma
=\frac{1-\alpha^{\gamma+1}}{1-\alpha}$$

$\alpha=1$ 时取极限 $\gamma+1$。真实接受率随位置和上下文变化时，应使用各位置条件接受概率的乘积累加，不能直接套单一均值。

若普通单步时间为 $T_t$，草稿单步为 $T_d$，验证为 $T_v$，其他成本为 $T_o$，则模型中的加速比为：

$$S\approx\frac{E[N]T_t}{\gamma T_d+T_v+T_o}$$

构造 $\gamma=4,\alpha=0.8,T_t=10$ ms、$T_d=2$ ms、$T_v=12$ ms、$T_o=1$ ms，得到 $E[N]=3.3616$、$S\approx1.60$。验证不是固定“一次普通 Decode”的成本，草稿也并非免费。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-与-batch-的张力核心架构结论"></span><span id="与架构建模的接口-modeling-interface"></span><span id="延伸阅读-references"></span></div>

## 批量与流式输出的影响

大批量可能已经充分摊薄目标权重，额外候选又增加 KV、工作区和验证计算。策略应在目标负载下测量，而不是无条件开启。

一轮提交多个 token 还可能产生突发输出。平均 token 产出改善不等于客户端 p99 ITL 同比例改善。需联合检查接受长度、请求延迟、输出分块和内存峰值。

来源：[Leviathan 等人的原始算法](https://proceedings.mlr.press/v202/leviathan23a.html)、[Medusa 论文](https://arxiv.org/html/2401.10774v3)。本页数值为构造模型，非论文实测。基础生成管线见[采样与停止](sampling-and-stopping.md)。
