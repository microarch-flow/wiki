# 如何选择模型粒度：需要保留哪些状态？

<span id="modeling-layers-analytical-event-cycle"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[07 Evaluation Methodology](./README.md)

相关：[性能界与瓶颈分析](./performance-bounds-and-bottlenecks.md)、[模拟器设计规格](../08-simulator-construction/simulator-design-spec.md)

<span id="这页在回答什么问题"></span><span id="不要从最复杂模型开始"></span>模型应保留回答问题所需的状态和规则。例如，只想排除容量明显不足的方案，不一定需要模拟每个 flit；要区分 credit 等待与仲裁失败，就需要描述对应资源。

## 状态、时间和推进方式分开选择

| 选择 | 要回答的问题 | 例子 |
| --- | --- | --- |
| 对象与状态 | 把什么视为独立对象，保留哪些资源？ | flow 和链路服务量；或 packet、flit、VC、credit 和队列。 |
| 时间精度 | 哪些事件的先后和时间需要准确？ | 阶段级完成时间；或指定模型边界的逐拍状态。 |
| 推进方式 | 怎样执行时间？ | 每拍推进，或跳到下一离散事件。 |
| 参考与验证 | 结果与什么契约或系统比较？ | 手算、独立模型、RTL 或实际计数器。 |

这几个选择可以组合。离散事件引擎如果按约定处理每拍相关事件，也可以复现指定模型的逐拍状态；逐拍循环如果没有表示 credit 和仲裁，也不能自动回答 credit 问题。[事件推进与逐拍精度](../08-simulator-construction/event-driven-vs-cycle-accurate.md)讨论实现。

## 同一个共享资源，不同问题

<span id="layer-0-analytical-estimate-bound"></span>对于[两源共享链路](./performance-bounds-and-bottlenecks.md#一个共享链路例子)，知道必要字节和资源容量，就可以得到完成时间下界。这个下界不需要规定仲裁顺序，但也不会给出每个 packet 的等待分布。

<span id="layer-1-bandwidth-aware-topology-aware"></span>加入端点位置、路由和每条链路容量后，可以估算不同映射的资源需求。若再定义服务和排队规则，解析或流级模型也可以分析某些 QoS 问题；结论仍受这些规则和假设限制。未经证明的估算称为 estimate 或 proxy，不能仅因为简化了模型就称为严格界。

<span id="layer-2-flow-状态粒度"></span>用 flow 表示释放、源目的、依赖和完成，可以研究阶段何时重叠。但如果模型没有表示逐拍仲裁或 credit，就不能从结果中报告真实的 `NO_CREDIT` 周期。flow 是否排队、如何共享带宽，仍需由模型定义。

<span id="layer-3-flit-level-credit-level"></span>显式加入 flit、VC、buffer、credit 和仲裁后，可以观察该模型中的细粒度等待。只有端点、路由及相关协议也被正确表示时，这些观察才能支持对应范围内的解释；更细的网络状态不自动修复错误的 workload 或端点假设。

## 周期精确相对于什么

<span id="cycle-accurate-是时间保真度不是引擎类别"></span>所谓周期精确，应说明与哪个目标相比，以及要求哪些边界的状态和事件逐拍一致。相对于教学模型一致，不等于已经与 RTL 或芯片一致。验证检查实现是否遵守模型；校准比较模型与参考系统。两者都需要记录输入、观测点和未覆盖的条件。

## 何时调整模型

<span id="什么时候该升级"></span>先列出目标指标、可用输入和不需要回答的问题。若结果对未表示的仲裁、端点反压或依赖敏感，就需要增加相应状态或使用更合适的参考；如果主要不确定性来自 workload，则只细化 router 并不能解决问题。

<span id="常见误区"></span><span id="一句话理解"></span><span id="建模启示"></span>每次增加复杂度，都要写清楚它新增了什么能力、成本和验证要求。模型记录模板见[实验与案例记录](./case-card-template.md)。
