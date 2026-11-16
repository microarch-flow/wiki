# 实现路线与阶段验收：先做哪一部分？

<span id="implementation-roadmap"></span>

上级：[09 模拟器构建与验证](../SUMMARY.md#08-simulator-construction)；原章节：[08 Simulator Construction](./README.md)

相关：[模拟器设计规格](./simulator-design-spec.md)、[最小逐拍仿真实作](./minimal-cycle-simulator.md)、[验证与校准](./verification-and-calibration.md)

<span id="这页在回答什么问题"></span><span id="核心原则"></span>实现可以逐步扩展，但每个阶段只能验收已经定义和实现的状态。保留前一阶段的回归，避免后续功能改变时间口径。

## Phase 0: 固定边界

确定单时钟、拓扑、路由、传输粒度、slot、链路延迟、端点和输出口径。写清可靠有序单播及不支持的功能，并保存初始配置与版本。

## Phase 1: 最小传输骨架

实现 packet／flit、固定路径和拍初读／拍末提交。用无阻塞例子检查 hop、顺序及各跳时间；若还没有 buffer、credit 和 ejection，不要求匹配包含这些状态的完整回归表。

## Phase 2: Buffer 与 Credit

加入有限 input FIFO、注入与 ejection、逐跳 credit 和反馈事件。在单 packet、无竞争条件下检查三跳表中的队列、credit 和完成时间；停止 consumer，检查反压在持续供数时如何传播。每拍检查容量及 credit 守恒。[最小逐拍仿真实作](./minimal-cycle-simulator.md)覆盖这个有限范围。

## Phase 3: Wormhole Path State

加入 input 上下文和逐包固定 VC。tail 成功离开本地 input 才清本地上下文；严格策略下，下游 VC 许可等 tail free 返回后释放。验收连续两个 packet，区分本地释放与许可可用，不让后包提前复用。

## Phase 4: Allocation And Contention

增加多输入、多 VC 和仲裁。检查不同输入竞争同一输出，也检查同一物理输入的不同 VC 请求不同输出时不能超出输入能力。分别记录 VC 许可失败、credit 不足和实际输掉 switch 仲裁。

## Phase 5: Traffic Class

给 packet 保留 class，明确 class 到队列、VC 与仲裁策略的映射，并能按类统计。只有进一步约定竞争流量、服务、反馈及端点条件，才能验证该构造配置下的等待界；标签本身不提供保证。

## Phase 6: Workload Trace

接入 v1 `flow / compute / barrier`、依赖和分包，区分本地交付及远端 consumer 完成。实现计算资源及调度后再输出计算利用率；先用小事件图检查依赖和零时长，再运行 GEMM 等较大输入。

## Phase 7: Stats And Experiment Harness

明确释放、注入、网络到达和消费时间，以及链路流量、stall 对象与分母。区分网络静止、workload 完成和超时。实验输出配置、seed、未完成对象和结构化结果。

## Phase 8: 对比实验

固定工作负载、预算和完成边界，选择一个问题逐项比较，例如 buffer 深度或端点服务。检查资源负载、等待、任务时间及成本；需要时增加组合实验。保留输入、结果和未验证假设，不把一次 sweep 写成全局最优。

<span id="一句话理解"></span><span id="建模启示"></span>每个阶段都应有最小测试、可复现输入和明确的通过条件。回归通过只证明覆盖场景符合该阶段契约；与参考系统的差异还需独立校准。
