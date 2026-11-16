# MoE 通信案例：专家选择怎样形成片上流量？

<span id="workload-moe-routing"></span>

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)；原章节：[06 AI NOC Specifics](./README.md)

相关：[All-to-All 与通信矩阵](./all-to-all-and-traffic-matrix.md)、[自适应路由](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)、[编译器与 NoC 协同](./compiler-noc-co-design.md)

<span id="这页在回答什么问题"></span><span id="moe-最狠的地方不在总量"></span>MoE 的 gating 为 token 选择需要执行的 expert。选择结果、expert 放置和执行能力共同决定通信。相同逻辑数据量也可能产生不同的本地交付比例、链路负载和端点等待。

## 从选择到完成

<span id="从-gating-到网络流量"></span>一个简化步骤是：选择 expert → dispatch token 数据 → expert 接收并计算 → 返回结果 → combine。gating 选择的是**模型中的目的 expert**；NoC routing 选择数据经过的网络路径。二者处于不同层次。

例如 100 个 token、hidden=1024、FP16 输入为 2 B/元素、每个 token 选择两个 expert，且所有选择都被接受、不压缩、不填充，则 dispatch 的逻辑交付量为：

> 100 × 1024 × 2 B × 2 = **409,600 B，即 400 KiB**。

若每个选择都分别返回同尺寸结果，逻辑回传量也为 400 KiB。结果维度、精度、合并位置或接纳规则变化时，回传不一定相等。本地 expert 的数据不必经过 NoC；多份逻辑交付也不一定对应相同数量的物理包。

## 相同逻辑量，不同 expert 分布

构造另一个更小的例子：4 个 tile 各持一个 token，expert 0–3 分别位于 tile 0–3；每个 token 选择两个不同 expert。假设每份 token 是 8 B，所有选择均被接受，本地直接交付，远端各发一份单播，不计包头、填充、重试或其他流量。

| 选择情况 | 各 expert 收到的份数 | 逻辑交付量 | 本地交付 | NoC 注入 payload |
| --- | --- | ---: | ---: | ---: |
| token 0、1 选 0/1；token 2、3 选 2/3 | 2、2、2、2 | 64 B | 32 B | 32 B |
| 四个 token 均选 0/1 | 4、4、0、0 | 64 B | 16 B | 48 B |

两个场景都产生 4×2=8 次逻辑交付，但 expert 负载和远端份数不同。若输出各自返回对应 token 所在 tile，且每份结果也是 8 B，上述两组的回传 payload 分别为 32 B 和 48 B；实际合并、分片或不同输出尺寸会改变结果。

这个例子不指定拓扑和时刻，不能据此推断最忙链路或完成时间。要进一步分析，需要把源、目的和发送时机映射到物理路径。通信矩阵与切面容量见 [All-to-All 与通信矩阵](./all-to-all-and-traffic-matrix.md)。

## 网络热点与 expert 热点

<span id="为什么它会挑战-deterministic-方案"></span>输入相关的 expert 选择可能使预先假设的负载分布失效，也可能让同一静态路径在某些输入下集中竞争。应区分至少两种情况：

- **网络资源紧张**：不同流竞争共享链路、交换端口或下游缓冲。可检查是否存在合法替代路径，以及绕行对其他流的影响。
- **expert 服务紧张**：选中同一 expert 的任务超过其接收或计算服务能力。仅改变 NoC 路径不能增加这个 expert 的计算能力。

<span id="但它不等于-fully-adaptive-就一定赢"></span>动态路由、不同 placement 或任务重排都可能是候选方案；其收益取决于可用路径、端点能力、负载与成本。静态计划也可以对允许的流量和偏离处理作明确约束，不应仅凭“MoE”名称断言哪种方案更好。

## 交付方式与隔离

<span id="qos-和-traffic-isolation-同样重要"></span>不同实现可能采取不同的通信组织方式。NVIDIA Megatron Core 文档列出 AllGather、All-to-All 和其他 dispatcher；这是跨 GPU 软件实现的例子，不规定片上 NoC 必须提供相同原语。[Megatron Core MoE 文档](https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html)

当 dispatch、结果返回和 memory response 共享资源时，可比较队列、服务机会或物理路径的不同隔离方式。记录各资源实际共享的范围，验证低优流量是否仍有服务机会；类别标签或增加优先级本身不证明公平或有限延迟。

<span id="建模启示"></span>对每个 token 或聚合块记录 expert 选择、接纳或丢弃、源目的位置、发送与接收、expert 入队及完成、回传和 combine。比较不同路由或 placement 时固定相同输入、端点容量与网络预算，并分别统计链路等待、expert 排队、未完成任务及工作负载完成时间。

<span id="一句话理解"></span>MoE 的关键不是给流量贴上“随机”标签，而是把输入相关选择转成可检查的数据交付和资源需求。
