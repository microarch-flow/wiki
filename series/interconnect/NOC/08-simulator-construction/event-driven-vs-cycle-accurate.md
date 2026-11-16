# 事件推进与逐拍精度：怎样安全地跳过空拍？

<span id="event-driven-与-cycle-accurate"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[如何选择模型粒度](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)、[路由器逐拍推进](./router-pipeline-pseudocode.md)、[验证与校准](./verification-and-calibration.md)

<span id="这页在回答什么问题"></span>推进方式和模型精度是不同选择。tick-driven 逐拍检查；event-driven 根据计划事件推进。周期精确则是相对于**指定目标和观察边界**，要求相关事件与状态的每拍行为一致。

## 同一规则，两种执行

假设拍 0 发送一个 flit，正向延迟为 1。按本章契约，它在拍 1 末进入下游 FIFO，拍 2 才可参加仲裁。逐拍引擎可以依次执行拍 0、1、2；事件引擎可以在合适条件下跳到到期事件，但仍要按相同的拍末提交和下一拍可见规则处理。

若拍 1 还有其他待仲裁 flit、consumer 行动或 credit 到期，则不能跳过这些动作。对同拍 router，所有候选仍从同一份 S(t) 形成；按 `(cycle, phase, stable_id)` 排序可以保证处理顺序稳定，但不能把稳定 ID 当作真实的资源仲裁规则。

## 何时可快进

只有能证明跳过的区间不会改变所需观察结果，或能以等价方式补算变化时，才可以快进。例如，队列内容保持不变，但等待年龄和 occupancy 统计随时间累计；实现可以按间隔批量累加，而不是假装这些统计没有变化。到期输入、计时器、仲裁、consumer 和工作负载释放都必须纳入检查。

快进不自动降低精度，也不保证更快；事件维护和等价性验证本身有成本。[gem5 事件队列接口](https://doxygen.gem5.org/develop/group__api__eventq.html)展示了一种按时间调度事件的机制，并不规定本章的拍内顺序。

## 选择与验证

同一模型可以用 tick 或事件引擎实现。要比较它们，固定输入、时间契约、资源规则和需要观察的统计，再逐拍比较发送、队列、credit/free、grant 与消费。覆盖同拍多个事件、空闲快进、阻塞和恢复。

相同 seed 不保证两套实现消耗随机数的顺序相同。可以固定仲裁结果，或为资源使用可复现的独立随机流。通过有限场景只说明这些场景一致，不自动证明两种内核对所有输入等价，也不证明与 RTL 一致。
