# NoC 的 QoS：怎样为不同流量分配服务？

上级：[04 路由、仲裁与服务保证](../SUMMARY.md#04-routing-and-flow-control)；原章节：[04 路由、仲裁与服务保证](./README.md)

相关：[仲裁策略](./arbitration-policies.md)、[虚通道基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)、[端到端服务保证](./service-guarantees-and-latency-bounds.md)、[多网络与资源隔离](../05-system-integration/multiple-physical-networks.md)

<span id="qos-and-priority-classes"></span><span id="这页在回答什么问题"></span>服务质量（QoS）描述不同流量需要怎样的服务，以及网络如何分配或隔离资源。优先级只是实现手段之一；是否有带宽或延迟保证，还要定义流量和服务条件。

## 先说目标，再选机制

<span id="qos-不是让所有流量都更快"></span>一个系统可能希望控制消息尽快完成，同时让数据流获得足够吞吐。应先确定测量边界、每类流量的需求、允许的输入与可接受的结果，再选择实现方式。目标可以是某类请求的统计延迟，也可以是在明确前提下的最坏情况界；两者不是同一承诺。

<span id="qos-最常见的实现抓手"></span>下面是可以组合的机制，不是按强弱排列的替代品：

| 机制 | 能控制什么 | 仍需检查什么 |
| --- | --- | --- |
| 优先级 | 同一仲裁点上的选择次序 | 高优负载、可服务条件和低优饥饿。 |
| 独立 VC 或队列 | 部分排队和上下文 | 是否仍共享输出、链路、缓冲池及端点。 |
| 加权或预留服务 | 指定机会或带宽份额 | 服务单位、时隙位置、输入 burst 和下游反馈。 |
| 多物理网络 | 分离部分物理资源 | 网络接口、目的端或存储系统是否仍共享。 |

<span id="1-priority-class"></span>优先级可以让符合条件的关键流量先被选择，但不能突破目的端容量。<span id="2-vc-separation"></span>VC 能给不同流量独立的队列或资源类别，却不增加共享物理链路的峰值容量；消息依赖和安全性仍需单独证明。

<span id="3-multiple-physical-networks-planes"></span><span id="4-reserved-share-weighted-arbitration"></span>物理分离可以减少某些共享点，也会引入额外资源与可能闲置的容量。共享链路上的预留或加权机制是另一类选择；实际隔离和等待需要依照服务规则与流量共同评估。[多网络与资源隔离](../05-system-integration/multiple-physical-networks.md)比较共享和分离在相同容量下的一种取舍。

## 一条路径上怎样形成服务

<span id="noc-里的-qos-比-bus-更难"></span>端到端请求可能依次经过源端、多个仲裁点、目的网络接口和存储系统。如果某一段持续不可服务，即使其他各段都有较高优先级，整体也不能按时完成。一个 class 标签需要由各相关资源实际识别并执行，才有可观察的效果。

<span id="一个-deterministic-npu-的常见-class-划分"></span>例如系统可以将 control、response 和 bulk data 分成不同类别。但类别名称、优先级和映射应由依赖与服务目标决定；不能仅凭“小包”或“响应”判断它一定需要最高优先级。

## 成本与验证

<span id="qos-的代价"></span><span id="什么时候比较多网络与带宽预留"></span>更强的隔离可能需要更多队列、状态、布线或控制逻辑；保留资源也可能在对应流量空闲时闲置。比较方案时同时观察关键类等待、其他类吞吐、端点能力及资源成本。

<span id="常见误区"></span><span id="建模启示"></span>按 class 记录输入、路径、队列映射、仲裁与共享资源，并区分生成、注入和交付的计量边界。统计延迟分布时，也记录尚未完成的请求；P99 不能自动充当最坏情况保证。[性能指标](../07-evaluation-methodology/metrics-latency-throughput-saturation.md)

<span id="一句话理解"></span>QoS 先定义需要的服务，再组合资源分配和隔离；标签本身不是保证。
