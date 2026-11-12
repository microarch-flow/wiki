# NOC Meets Memory System

上级：[05 System Integration](./README.md)

相关：[RAM: NPU memory hierarchy](../../../../../RAM/wiki/09-ai-chip-memory-architecture/npu-memory-hierarchy.md)、[RAM: memory controller](../../../../../RAM/wiki/06-memory-controller/why-mc-is-the-real-bottleneck.md)

## 这页在回答什么问题

NoC 把请求和数据送到 NI，SRAM bank、memory controller 和 consumer 决定何时能接收和服务。任何一处服务不足都可能形成队列，并通过 ejection、逐跳 credit 反压到源端。

## 同一单位比较容量

对一个确定方向、路径和采样窗口，用有效字节/秒比较：

```text
payload_throughput ≤ min(path_payload_capacity, NI_payload_capacity,
                         bank_service_bytes_per_s, MC_service_bytes_per_s)
```

各项需在同一流量和计量边界测量。链路物理位宽为 `w_bits`，时钟为 `f_Hz` 时，单端口原始容量为 `w_bits × f_Hz / 8` B/s；header、空拍和重试使 payload 容量更低。多路径共享链路、读写共享总线、多个请求相互依赖时，简单取 min 仅是必要上限，不能证明可达。

## SRAM bank 冲突和 ejection

假设 B 个相同单端口 bank，每拍 Q 个请求独立、均匀映射，且每个非空 bank 当拍可服务一个请求，不考虑历史排队：

```text
E[可服务请求数] = B × (1 − (1 − 1/B)^Q)
```

例如 B=4、Q=3，期望为 `4×(1−(3/4)^3)=37/16=2.3125` 请求/拍。其余请求需要按队列与仲裁规则重试；这不是 `Q²/B` 的冲突因子。若每次服务 32 B、频率 1 GHz，期望服务量为 74 GB/s；还必须确认每请求恰为 32 B、无其他竞争且样本满足上述独立分布。顺序 stripe、热点及 compute/DMA 共享 bank 时需用实际映射和队列测量，不能套用固定百分比。

把测得或假设的有效服务速率 `S` B/s 转为 flit/cycle：`S / flit_bytes / router_frequency_Hz`。例如 `64 GB/s / 32 B / 1 GHz = 2 flit/cycle`。若局部时钟不同，需另建 CDC 和时钟换算；GB/s 除以 B/flit 先得到 flit/s。

## HBM 与 controller 的服务窗口

每 pin 的数据率乘总数据位宽，再除以 8，才是该接口的理论 B/s；burst 组织决定一次请求传多少数据，不应再把数据率乘以 burst 长度。有效吞吐受通道映射、读写方向、时序、调度与流量约束。

例如假设某系统实际测得可用数据服务能力 600 GB/s，平均响应 256 B，单窗口完整 RTT 为 100 ns，可用请求槽 64：

```text
服务容量 = 600e9 / 256 = 2.344e9 request/s
窗口容量 = 64 / 100e-9 = 640e6 request/s
由此得必要上限 min(...) = 640e6 request/s = 163.84 GB/s
```

这是构造假设，不是 HBM 型号规格。RTT 会随负载变化；请求供给、返回链路及 controller 也可能限制性能。若比较 NoC 的 bytes/s，先将 request/s 乘以同口径的平均有效响应字节。

## 返回突发与有限缓冲

一个响应可由多个 beat 或 packet 返回。抵达节奏由 controller、桥、链路宽度、时钟和仲裁共同决定，不能假设 256 B 总在 1–2 cycle 到达。要评估 ejection 深度，记录每拍入队/出队、credit 反馈和消费 stall；在已知突发到达曲线、最小服务曲线与初始占用时求最大积压。缓冲可以反压并平滑流量，不存在通用的 `max(R,burst+2)` 深度公式。

## 建模启示

保留地址到 channel/bank 的映射、NI injection/ejection 队列、bank 端口和仲裁、MC 请求槽及服务分布、response 分片与 consumer ready。统计每一方向的 payload 和 wire 字节、queue occupancy、实际服务率与未完成请求；用同窗口测量区分网络、bank、MC 和端点供给造成的等待。固定 latency 可用于粗略筛选，但不能解释 burst、局部热点或信用反压。
