# Verification And Calibration

上级：[08 Simulator Construction](./README.md)

相关：[Core Data Structures](./core-data-structures.md)、[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)、[Stall Taxonomy And Attribution](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)

## 验证范围与计时口径

Verification 检查实现是否遵守已定义的模型；calibration 检查参数及输出与参考系统的差异。前者通过不代表模型已校准，也不证明硬件性能。以下是手算的回归预期，不是已经运行的仿真结果。

所有表使用 [快照契约](./router-pipeline-pseudocode.md#时间与快照契约)：读拍初 `S(t)`，在拍末提交；当拍到期的 flit、credit 和注入不可在本拍参与路由。每条 link 正反向延迟均为 1，即拍 `t` 发送，拍 `t+1` 末到达、拍 `t+2` 可使用。本模型 RC/VA/SA/ST 可在一个有效拍完成。consumer 每拍读取拍初 ejection FIFO，拍末提交。输出 VC 使用下游 tail free 信号的严格复用策略。

## 场景 1：三跳、三 flit、无阻塞

输入：`R0—R1—R2—R3`，每个 input VC 深度 4，单 VC。源 endpoint 自拍 0 起每拍注入 1 flit，目的 ejection FIFO 深度 4，consumer 每拍最多取 1 flit。packet 依次为 `H, B, T`。初始 FIFO 和 link 为空，每个 credit 为 4。下表所有队列和 credit 均是**拍末快照**；`-` 是空，`E` 是 ejection FIFO。

| 拍 | 本拍动作；箭头后的 flit 在下一拍末到达 | R0 input | R1 input | R2 input | R3 input | E | C01 / C12 / C23 |
|---:|---|---|---|---|---|---|---:|
| 0 | 注入 H | H | - | - | - | - | 4 / 4 / 4 |
| 1 | R0→R1 H；注入 B | B | - | - | - | - | 3 / 4 / 4 |
| 2 | R0→R1 B；H 到 R1；注入 T | T | H | - | - | - | 2 / 4 / 4 |
| 3 | R0→R1 T；R1→R2 H；B 到 R1 | - | B | - | - | - | 1 / 3 / 4 |
| 4 | R1→R2 B；T 到 R1、H 到 R2；C01 收 H 的 credit | - | T | H | - | - | 2 / 2 / 4 |
| 5 | R1→R2 T；R2→R3 H；B 到 R2；C01 收 B 的 credit | - | - | B | - | - | 3 / 1 / 3 |
| 6 | R2→R3 B；T 到 R2、H 到 R3；C01 收 T、C12 收 H 的 credit | - | - | T | H | - | 4 / 2 / 2 |
| 7 | R2→R3 T；H 弹出；B 到 R3；C12 收 B 的 credit | - | - | - | B | H | 4 / 3 / 1 |
| 8 | consumer 取 H；B 弹出；T 到 R3；C12 收 T、C23 收 H 的 credit | - | - | - | T | B | 4 / 4 / 2 |
| 9 | consumer 取 B；T 弹出；C23 收 B 的 credit | - | - | - | - | T | 4 / 4 / 3 |
| 10 | consumer 取 T；C23 收 T 的 credit/free | - | - | - | - | - | 4 / 4 / 4 |

`Cij` 是 Ri 指向 Rj 的 output credit；源 endpoint 的注入 credit 在拍末 0–4 分别是 `3, 2, 2, 3, 4`，此后为 4。每个 flit 经三条 router 间 link，`hop_count=3`；LOCAL 弹出不加 hop。`injection_cycle=0`，`network_arrival_cycle=9`，`consumer_complete_cycle=10`。在本例其他队列、管线和许可也于拍 10 末清空，故 `protocol_quiescent_cycle=10`。这三个边界可以在其他配置下相隔更多拍。

首 flit 每一跳在本口径占 `1` 拍发送及 `1` 拍到达提交，下一拍才可发送；三个 link 后第 7 拍弹出。包的 tail 晚两拍注入，因此第 9 拍才弹出。旧的“第 8 拍全部弹出、耗时 6 拍”同时忽略了 tail 的序列化和快照边界。一个不同的旁路实现可以更快，但不能沿用这张表。

## 场景 2：持续流量填满反压链

输入：同一拓扑和 buffer，ejection 深度 2、consumer 不消费；注入足够长的单包，例如 30 flit。有限的 10 flit 不足以保证填满本拓扑全部 FIFO，不能把它用作该通过条件。

预期：ejection 满后，R3 的 LOCAL 队首报 `EJECTION_BLOCKED`。持续供数且链路可靠时，R3 input 堵满，R2 的 credit 耗尽；依次传播到 R1、R0 和源注入端。最终 R0–R3 各 input FIFO 满，C01/C12/C23 均为 0，源 injection credit 为 0，仍有 flit 待注入。R3 没有用于 LOCAL 的 C34。每条 link 分别满足 credit 守恒。恢复 consumer 后，先逐个释放目的端 slot，再由正反向链路与仲裁逐级恢复前进。

首次阻塞拍取决于现有 credit、在途 flit、buffer、link 延迟和仲裁；不得断言统一等于某个 buffer 深度。记录各级首次事件，用有限时间上限检测意外停滞。

## 场景 3：尾部释放与下一包

使用场景 1 的拓扑和严格策略。在拍 0 排队 A 和 B，各 3 flit，单 VC。A 在拍 0、1、2 注入。A 的 T 在拍 3 离开 R0，本地 input 上下文可于拍末清除；源接口的尾部 free 在拍 4 末到达，因此 B 最早在拍 5 注入。A 的 T 在拍 5 离开 R1，R0→R1 的尾部 free 在拍 6 末到达。因此 B 的 H 在 R0 最早于拍 7 获得该输出 VC；拍 6 不能抢先分配。

这个例子分开了源 router 本地上下文释放、源注入 VC 的许可、跨路输出 VC 的许可。若选择提前复用策略，必须另写 FIFO/包边界证明和预期表；不得沿用上述严格时序。

## 场景 4：VC 竞争与 switch 竞争分开

两输入的完整 A、B 各 3 flit 已在拍 `k` 前排入不同 input VC，都要从同一东向输出发送。下游有两个可用 output VC，各有至少 3 credit；VA 可同时分配两个 VC；switch 每拍仅传 1 flit，按每 flit round-robin，初始指针选 A。假设输入及正向链路均不额外阻塞。

| 拍 | 获胜 flit | 另一队首的主 stall |
|---:|---|---|
| k | A.H | B: SWITCH_CONFLICT |
| k+1 | B.H | A: SWITCH_CONFLICT |
| k+2 | A.BODY | B: SWITCH_CONFLICT |
| k+3 | B.BODY | A: SWITCH_CONFLICT |
| k+4 | A.T | B: SWITCH_CONFLICT |
| k+5 | B.T | 无 |

两包分别持有不同的下游 VC，因此可以在物理输出上交错。若只有一个下游 VC，B 在 A 的许可尚未释放时应报 `VC_ALLOC_FAIL`，不是持续报 `SWITCH_CONFLICT`；严格策略下还需等待下游尾部 free 返回。若实现按包保持 switch，则又是另一套显式仲裁策略。

## 场景 5：LOCAL 失败不可产生提交副作用

在目的 router 放一个 `HEAD_TAIL` 于 input 队首，使 ejection FIFO 满，并让 consumer 停止。连续执行两拍，检查每拍 `EJECTION_BLOCKED` 恰计一次。flit 仍在原 input FIFO，输入上下文不变，上游不收到新的 slot credit/free，hop 不增加。空 input VC 的 stall 计数保持 0。consumer 恢复后，在本模型中腾出的 slot 要到下一快照才可见；随后成功弹出，才释放输入 slot 并返回 credit/free。

再测首 flit 因 injection credit 为 0 或 VC 许可不可用而等待：`injection_cycle` 必须保持未定义；首次实际注入成功时才设置。多 VC 测试还要断言同一包从头到尾使用同一注入 VC。

## 校准和回归的边界

先把每拍队列、credit、free 与动作事件保存为 trace，对照上述手算和 [核心不变量](./core-data-structures.md#断言与守恒)。之后用独立参考模型、实际计数器或更高保真模型校准。对比必须冻结拓扑、链路与 router 延迟、buffer、VC 释放、仲裁及测量边界；不同假设下无需强行匹配数字。

平均延迟、饱和吞吐和网络直径可作为 sanity check，但负载增加时平均延迟并非对所有有限样本和流量模式都严格单调。校准容忍度应由目标和参考误差确定，不能把统一百分比当成正确性证明。

## 回归记录与独立验证

每个场景应保存拓扑、容量、时序与仲裁版本，逐拍期望值、观测值以及首个不一致项。例如：

```text
scenario: three-hop-3-flit
config: depth=4, forward=1, return=1, snapshot=v1
cycle: 9
field: R3.ejection_fifo
expected: [T]
observed: [T]       # 示例记录，不代表此 wiki 执行了测试
result: pass
```

校准时先固定参考和模型的时钟、采样点、traffic、容量及完成定义，用一组样本拟合延迟或有效带宽。再用未参与调参的独立负载和参数组合检查数值与趋势；记录样本、误差及不适用范围。若参考和模型的 VC 释放或流水线时序不同，先对齐契约，再解释残差。通过少数回归只说明这些条件下的模型行为得到验证。
