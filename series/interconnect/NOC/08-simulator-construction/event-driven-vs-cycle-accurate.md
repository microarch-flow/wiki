# Event Driven 与 Cycle Accurate

上级：[08 Simulator Construction](./README.md)

相关：[Modeling Layers](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)、[Verification And Calibration](./verification-and-calibration.md)、[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)

## 这页在回答什么问题

仿真推进方式和模型保真度是两条独立轴。event-driven 指按事件时间跳转；tick-driven 指逐拍执行。cycle-accurate 则要求所选接口和内部状态的每拍行为符合目标时间契约，不能由引擎名称推断。

| 执行引擎 | 粗 flow 状态 | flit/credit 与逐拍仲裁状态 |
| --- | --- | --- |
| tick-driven | 每拍检查 flow 的粗模型，可能做很多无效工作 | 可按每拍快照实现 cycle-accurate |
| event-driven | 按 flow 到达和完成时间推进 | 也可在每个有变化的周期处理候选、grant、flit 和 credit，达到同一逐拍语义 |

例如事件按 `(cycle, phase, stable_id)` 确定次序；对同拍 router，仍要从统一 `S(t)` 快照计算候选，在拍末统一提交，不能因事件遍历顺序让 flit 同拍走多跳。模型应遵守 [时间与快照契约](./router-pipeline-pseudocode.md#时间与快照契约)。

## 何时可快进

仅在下一事件之前没有会改变结果的外部输入、时钟边沿、计时器、仲裁指针、队列、credit 或消费状态时，才能跳过空闲时间。若一个等待候选每拍都可能获 grant，就不能只跳到下个 packet 到达而漏掉仲裁。事件队列节省的是无状态变化的空拍，不自动降低模型精度，也不保证更快。

## 选择与验证

先决定需要观察 flow、packet、flit、credit 或信号级状态，再选 tick 或事件实现。粗 flow 模型适合快速筛选，但不能解释未建模的 VC 和逐拍回压；细粒度模型有更高状态和验证成本。

用同一 trace、seed 和快照规则运行 tick 与 event 两个内核，逐拍比较发送、credit/free、队列、grant、消费和统计。测试同拍多事件、空闲快进、下游阻塞及恢复；只有在目标场景对齐后，才可声称两实现等价。两者都不自动等同 RTL 签核。
