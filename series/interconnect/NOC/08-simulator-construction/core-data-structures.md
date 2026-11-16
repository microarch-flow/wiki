# 核心数据结构：状态由谁持有，何时改变？

<span id="core-data-structures"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[路由器逐拍推进](./router-pipeline-pseudocode.md)、[工作负载与端点执行](./workload-endpoint-execution.md)、[验证与校准](./verification-and-calibration.md)

## 对象与模型边界

以下面向单播、flit 级、wormhole 和逐跳 credit 的教学模型。其他实现可以组织不同的数据结构，但必须给出等价的状态和时间规则。

| 对象 | 持有的状态 | 更新者与职责 |
| --- | --- | --- |
| Packet / Flit | ID、源和目的、类别、flit 序号及类型 | packetizer 创建；单 flit 使用 `HEAD_TAIL`，跨 router 发送才增加 hop。 |
| Input VC | FIFO、当前包及其 route / out VC 上下文 | 到期 flit 入队；成功移出 tail 后清本地上下文。 |
| Output VC | 下游 slot credit、许可及其 owner | 发送扣 credit；返还 credit 到期加回；分配与 free 更新许可。 |
| Link | 正向 flit 和反向 credit/free 的定时事件 | 按配置时间在拍末交付，保留每条边和 VC 的身份。 |
| Endpoint | 已就绪待发包、注入许可、ejection FIFO 和 consumer | 按容量注入与消费，并记录各完成事件。 |
| Workload / Stats | 事件依赖、任务状态；时间、流量与 stall | 调度器更新任务状态；统计模块按提交事件计数。 |

<span id="最小字段和写入者"></span>每个对象应有稳定 ID。未发生的时间用 `None`，不要用 0 冒充；同一 packet 的 flit 固定使用已分配的 VC 并保持顺序。状态只能由约定的模块在提交阶段写入；本地未获得服务时不能先 pop、扣 credit 或释放上下文。

## 三种独立状态

1. **本地上下文**保存当前 input VC 的 packet、输出端口与分配结果。tail 成功离开后，本地上下文可清除。
2. **slot credit**表示发送端可预留的下游空槽。发送消耗 credit，下游实际移出 flit 后才生成返还。
3. **VC 分配许可**表示下游 VC 能否分配给新包。严格策略下，即使 credit 大于 0，也要等下游 tail 的 free 信号返回并提交。

这三种状态不等价。另一种实现可以提前复用 VC，但必须保证 FIFO 顺序、包边界和上下文切换；不能仅凭清除本地 holder 就宣布下游许可空闲。[BookSim 手册](https://github.com/booksim/booksim2/blob/master/doc/manual.tex)将等待 tail credit 作为可配置策略。

## 时间字段和统计边界

| 字段 | 本章采用的写入时刻 |
| --- | --- |
| `injection_cycle` | 首 flit 成功注入源 router input 的拍末。 |
| `network_arrival_cycle` | tail 成功进入目的 ejection FIFO 的拍末。 |
| `consumer_complete_cycle` | consumer 成功接收 tail 的拍末。 |
| `protocol_quiescent_cycle` | 本次已释放的待发包、网络／端点队列、正反向消息和 VC 占用均清空的首次拍末。 |

时间戳是拍号；是否把首尾拍都计入离散周期数要另外说明。协议静止不表示未来计划释放的 workload 事件已完成；任务完成还要检查所有目标事件及依赖。本地源与目的相同时，本章 v1 案例选择端点本地交付，不计网络注入和 router 间 hop；consumer 的容量与完成规则仍需定义。

## 断言与守恒

对固定深度 B 的一个下游 VC，若每次发送预留一个 slot、每次出队返还一个 credit，且消息不丢失或重复，则同一拍末快照满足：

> B = 发送端可用 credit + 正向在途 flit + 下游 FIFO 占用 + 返回在途 credit。

四项必须属于同一有向连接和同一个下游 VC。源端注入接口也要有自己的容量和守恒规则；LOCAL ejection 不扣不存在的跨路 credit。

其他断言包括：每个 output VC 至多一个 owner；每个输入和输出不超过其每拍服务能力；失败动作不产生提交副作用；不同阶段中的 flit 总数守恒且按包有序。允许额外 staging、共享池、批量返回或重试时，需要扩展上述等式，而不是直接套用。

这些断言检查所定义的模型；它们不单独证明无死锁或与硬件数值一致。[验证与校准](./verification-and-calibration.md)给出手算场景。
