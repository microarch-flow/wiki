# 模拟器设计规格：第一版要表示什么？

<span id="simulator-design-spec"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[如何选择模型粒度](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)、[核心数据结构](./core-data-structures.md)、[实现路线](./implementation-roadmap.md)

<span id="这页在回答什么问题"></span><span id="目标边界"></span>这份规格描述一个用于教学和架构探索的 NoC 模型。它要说明输入、资源、时间与输出，使实现能够逐项验证；它不是 RTL 等价证明，也不是物理签核模型。

## 第一版的目标能力

| 能力 | 目标契约 | 最小实作篇的范围 |
| --- | --- | --- |
| 网络 | 单播、固定拓扑与确定性路由；每次跨路发送一个 flit。 | 四个 router 的固定线形路径。 |
| 流控 | input VC 有有限 slot，逐跳 credit 控制发送；严格策略等待下游 tail free 后再分配。 | 每个输入一个 VC、一个 packet；记录 free，不实现下一包分配。 |
| 竞争 | 可配置多个 VC 和输入；仲裁必须满足输入、输出及 VC 许可约束。 | 单路径无竞争，不实现 allocator。 |
| 端点 | 注入队列、有限 ejection FIFO 和 consumer；本地交付按所选契约单独处理。 | 一个源和一个目的，可暂停 consumer。 |
| 输入与任务 | 可接入第八章 v1 事件；支持 compute 时需定义计算资源与调度。 | 在代码中直接构造一个 packet，不读取 v1 Trace。 |
| 时间 | 单时钟；拍初读 S(t)，拍末提交；基线 flit 与链路传输单位同宽。 | 正向、返回延迟均可配置为正整数。 |

traffic class 可以作为 packet 标签和统计维度；仅有标签不产生隔离或有界服务。多播共享树、多时钟 CDC、复杂自适应路由、位精确编码、重试与完整一致性协议均不在这个基线内。支持某项扩展前，要补资源状态、时间规则及对应验证。

<span id="第一版必须回答的问题"></span>在已表示工作负载和端点的范围内，模型可以比较指定输入下的链路负载、等待和完成事件。计算利用率或系统级因果只有在计算与端点资源已建模时才有意义。

## 输入、状态和输出

<span id="核心对象"></span>输入包括拓扑、端点位置、路由、packet 或 workload 事件、slot 容量、链路延迟、仲裁和消费规则。核心状态包括 Packet、Flit、Input VC、Output VC、Link 和 Endpoint；统计模块记录成功动作、等待及完成边界。[核心数据结构](./core-data-structures.md)定义各自的写入者和不变量。

<span id="输出接口"></span>输出应包括配置及版本、packet 注入／网络到达／消费时间、链路流量、指定口径的 stall 与未完成对象。若支持 workload 事件，再报告事件完成及其依赖；不要用网络到达时间代替 consumer 或事务完成。

## 时间、资源与停止条件

<span id="必须固定的时序语义"></span><span id="推荐的主循环语义"></span>跨路发送时扣除发送端 credit，预留下游 slot；下游实际移出该 flit 后生成返还 credit。到期消息在拍末提交，不能参与当拍决策。tail 离开本地 input 时释放本地上下文；严格策略下，下游 VC 许可等待 tail free 返回。[快照与逐拍推进](./router-pipeline-pseudocode.md#时间与快照契约)给出完整规则。

<span id="traffic-class-的最低要求"></span>示例沿用 `CONTROL`、`MEMORY_REQUEST`、`MEMORY_RESPONSE`、`STREAM`、`BULK_DMA` 标签。类别如何映射 VC 和仲裁由配置决定；不必强制每类独占 VC。

停止时要分别检查网络协议状态是否排空，以及所有目标 workload 事件是否完成。网络暂时空闲时，可能还有未来释放的任务；超时应输出未完成状态，不能仅凭超时证明死锁。

<span id="第一版明确不做什么"></span><span id="一句话理解"></span><span id="建模启示"></span>先固定契约，再以[验证场景](./verification-and-calibration.md)检查实现。最小程序只覆盖其中的场景 1 和 2；测试通过只说明指定条件下的模型行为得到检查。
