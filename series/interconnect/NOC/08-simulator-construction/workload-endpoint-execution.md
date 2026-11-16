# 工作负载与端点执行：依赖何时释放？

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)

相关：[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)、[流量注入、分包与完成](./traffic-injection-and-tracing.md)、[从 Flow 到完成](./workload-to-completion-worked-example.md)、[网络接口 NI](../05-system-integration/ni-network-interface-design.md)

Trace 的事件需要由某个资源执行。一个 consumer 是否能接收、一个 compute 是否能占用计算资源，都会改变后继事件的释放时间。本页定义一种可实现的教学调度规则，不规定真实硬件必须如此执行。

## 事件状态和可见时间

对 v1 的 `flow`、`compute` 和 `barrier`，可记录 `WAITING → READY → RUNNING → COMPLETE`。前驱按 all-of 判断；释放时间已到且全部前驱完成，事件才可就绪。失败、超时和取消需要单独定义，不能伪装成完成。

在本章快照口径下，拍 t 的动作在拍末提交。若一个 consumer 在拍 t 消费 tail，或一个事件在拍 t 完成，依赖它的后继最早在 S(t+1) 看见完成。实现可以给完成事件和可见时刻分别记字段，避免把拍号与经过的周期数混用。

## 计算资源和零时长

构造例：节点 0 有一个不可抢占计算资源，两个 4-cycle compute 在 S(0) 都已就绪，按确定的 FIFO 顺序选择，且没有其他等待。第一项运行于区间 [0,4)，在拍 3 末完成；第二项运行于 [4,8)，在拍 7 末完成。两项完成时，资源共执行 8 个 compute-cycle，观察窗口为 8 cycle。若有两个独立资源且允许并行，它们可以都在 [0,4) 执行；资源数和统计分母必须随结果报告。

第八章示例的校验器接受 `duration_cycles=0`。本章可将零时长 compute 作为不占计算资源的事件：若在 S(t) 已就绪，在拍 t 末提交完成，其后继最早在 S(t+1) 可见。它的计算时长为零；拍末提交的可见规则仍然存在。barrier 可采用同样的提交边界。其他零时长处理规则也可行，但改变 v1 输入限制或依赖语义时，要同步说明兼容范围。

## Flow、本地交付与 consumer

flow 就绪后，endpoint 按目的集合创建交付。本文基线对源和目的相同的分支选择本地交付，不经过网络注入或 router 间链路；它仍需要按定义占用本地 consumer 服务，并产生目的完成事件。远端分支按 packetize、注入、网络到达、ejection 和 consumer 接收推进。

每个目的所需的全部 packet 都被 consumer 接收，才标记该目的完成；所有目的包括本地目的都完成，才标记父 flow 完成。packet ID 和目的 ID 应去重，避免重放或重复通知使计数提前归零。第八章的 v1 定义是整个 flow 的 all-consumer 完成；若要让某个目的独立释放计算，需要扩展事件表达，不能直接更改 v1 的含义。

## 网络空闲与任务完成

网络队列和返回 credit 都为空，可以表明所检查的网络协议状态已排空；未来释放的 compute、flow 或 barrier 仍可能存在。报告时分开 packet 完成、已释放网络工作的静止和目标 workload 全部完成。有限时间内未完成需要记录对象、依赖和资源状态；超时本身不是死锁证明。

实现者应固定本地／远端 consumer 容量、计算资源数、调度顺序、时间可见点及统计分母，再使用[验证场景](./verification-and-calibration.md)和任务依赖测试。真实 NI、DMA 与存储系统的机制见第五章；这里仅规定模型接口。
