# NoC 设计决策路径：怎样生成并检验候选？

<span id="noc-design-decision-tree"></span>

上级：[10 查阅与练习](../SUMMARY.md#09-reference)；原章节：[09 Reference](./README.md)

相关：[拓扑选型](../03-topology/topology-selection-framework.md)、[架构探索与实验设计](../07-evaluation-methodology/architecture-exploration-loop.md)、[检查清单](./checklists.md)

<span id="这页在回答什么问题"></span>本页帮助把一个设计问题变成可比较的候选、证据和下一步实验。各步可以反复执行；它们不是按一次判断给出唯一拓扑的规则。

## <span id="决策树主线"></span>从问题到候选

先记录目标及其边界，例如“在给定工作负载和面积预算下，缩短到所有 consumer 完成的时间”。同时记录端点、物理约束、可改变的参数，以及已经有证据和仍未知的项。

### Step 1: 先判断主流量是什么

列出参与者、源目的、数据量、时间分布和依赖。区分单播、多个目的的复制与归约；同一个系统也可以同时出现 request、response 和 bulk 流量。只有算子名字时，先生成或收集候选通信模式，不预设它的热点。[从工作负载到 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)

### Step 2: 再判断主要瓶颈层级

分别检查链路／router、注入与 ejection、memory 端口、计算及依赖。没有结果时，只能列**候选瓶颈**；使用容量必要条件、逐资源计数或受控实验补证据。某资源负载高也未必证明它决定端到端完成时间。[性能界与瓶颈](../07-evaluation-methodology/performance-bounds-and-bottlenecks.md)

### Step 3: 判断 path diversity 是否真的有价值

画出合法替代路径及其共享资源，比较固定映射、修改 placement 和动态选路。多路径可能分散特定竞争，也可能增加距离和硬件成本；混合路由要重新检查依赖与前进条件。[自适应路由](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)

### Step 4: 判断是否需要 traffic isolation

若有受干扰的目标流，先定义它的带宽、等待或完成目标，再比较共享仲裁、预留服务、VC 映射和物理网络。不同方案的面积、利用率与证明条件不同；class 标签或独立 VC 本身不保证端到端服务。[QoS 与优先级](../04-routing-and-flow-control/qos-and-priority-classes.md) · [端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

### Step 5: 判断是否要上 collective 支持

对实际参与组和数据位置，比较多份单播、逻辑树与网络内复制或归约。计算链路与端点需求，并计入复制状态、缓冲和硬件代价。存在 collective 不自动意味着专用网络更优。[集体通信基础](../06-ai-noc-specifics/collective-communication-basics.md)

### Step 6: 判断 compiler/runtime 是否应参与

可比较预先映射、静态调度、运行时选择或混合方案。需要记录可预测的信息、允许的偏差、冲突处理及端点行为；动态工作负载也可能有可静态利用的部分。[编译器与 NoC 协同](../06-ai-noc-specifics/compiler-noc-co-design.md)

## 用一个观察设计下一步

假设某次实验显示“全网平均链路利用率为 30%，任务完成较慢”。这不能单独排除网络瓶颈：少数方向可能繁忙，端点或依赖也可能限制供数。

先检查测量窗口和未完成任务，再看每条有向链路、ejection、memory 与依赖等待。若证据仍不足，可以分别提高候选链路容量或目的端服务能力，保持输入与其他参数相同，观察完成时间及等待如何改变。这是用于区分原因的**实验设计**，不是对任何实际系统的诊断。

## 一个更具体的速查版本

以下仅给出优先检查项，不由工作负载名称直接选拓扑。

### 如果是 GEMM-like

检查输入复用、广播或转发、partial sum 归约，以及数据放置。[GEMM 案例](../06-ai-noc-specifics/workload-gemm-on-noc.md)

### 如果是 decode-like

检查请求／响应、KV 位置、端点服务和依赖边界；不同长度与 batch 可能改变瓶颈。[Decode 案例](../06-ai-noc-specifics/workload-attention-decode-kv-cache.md)

### 如果是 MoE-like

检查 dispatch/gather 通信矩阵、专家位置、负载分布及可用路径。[MoE 案例](../06-ai-noc-specifics/workload-moe-routing.md)

### 如果是 chiplet / cross-die

检查网关、跨 die 带宽与时钟、协议和位置，比较分层方案的实际资源成本。[层次化与混合互连](../03-topology/hierarchical-and-hybrid-topology.md)

## 什么时候该回头重判

当工作负载、端点或 memory 位置、预算、服务目标、模型口径或观察到的等待改变时，重新检查候选。报告每个方案的输入、可行性、结果和代价；若证据不足或没有可行方案，应明确记录。

<span id="一句话理解"></span><span id="建模启示"></span>决策路径的输出是“在这些条件下，候选经过哪些检查”，不是脱离条件的方案排名。记录格式可复用[实验与案例记录](../07-evaluation-methodology/case-card-template.md)。
