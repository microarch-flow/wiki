# Credit / Backpressure

上级：[Router 微架构](./README.md)

相关：[Packet / Flit / Wormhole](./packet-flit-wormhole.md)、[指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)

## 核心问题

上游什么时候可以安全地把 flit 发给下游？  
如果下游堵住了，这个压力如何一路传回 producer tile？

## 为什么需要 flow control

router 的 input buffer 是有限的。  
如果发送方不关心接收方是否还有空位，最终一定会发生 buffer overflow。

所以 flow control 的本质是：

保证 sender 不会发送 receiver 无法接收的 flit。

## Ready/Valid vs Credit

### Ready/Valid

适合：

- 短距离 pipeline stage
- 本地模块握手

问题：

- 如果跨多级 router 或长链路，`ready` 反压路径容易过长
- 不适合大规模 NoC 的时序实现

### Credit-based

发送方维护一个 credit counter，表示下游尚可接收的 buffer slot 数量。

规则很简单：

- 发送 1 个 flit，credit 减 1
- 下游释放 1 个 slot，返回 1 个 credit
- 只有 credit > 0 时，发送方才能继续发

## 一条容易搞错的原则

credit 返回的时机，不是“下游收到这个 flit”，而是“下游释放了这个 buffer slot”。

这意味着：

- credit 防的是 overflow
- credit 不等价于成功送达终点

## Credit round-trip latency

credit 是要飞回来的，所以 credit 本身也有往返延迟。  
这会带来两个直接影响：

- buffer 太浅时，链路吞吐起不来
- 即使逻辑上没有完全堵死，也会因为 credit 回来太慢出现 bubble

工程上常见的直觉是：

buffer 深度至少要覆盖 credit round-trip 的量级，否则链路利用率会被 credit 往返时间吃掉。

## Backpressure 是什么

当下游没有空间或不能继续消费时，上游被迫停止发送；这种停止如果继续沿路径反向传播，就是 backpressure。

## 为什么 AI NoC 特别怕 backpressure

因为它最终不只是通信 stall，而会演化成 compute stall。

典型链条：

1. destination stream FIFO 满
2. 本地 ejection 停住
3. 上游 router 收不到 credit
4. 上游链路被迫停发
5. producer tile 无法继续输出
6. tile pipeline 利用率下降

## 常见 backpressure 来源

- destination stream FIFO 太浅
- HBM / DMA response 被堵
- reduce fan-in 过大
- bulk DMA 流量压住小控制消息
- 下游 compute stage 消费节奏慢

## 建模时必须区分的两类 stall

### Credit stall

没有下游 buffer 配额，不能发。

### Switch stall

有 credit，但多个输入在争同一个输出，仲裁没赢。

这两类 stall 的优化方向完全不同。

## 第一版 simulator 至少要统计什么

- per-link utilization
- per-router input occupancy
- credit stall cycles
- switch stall cycles
- packet latency 分布
- source injection stall
- destination ejection stall
- tile busy / idle / blocked 比例

## 本页结论

credit-based flow control 的本质，是用“下游空位计数”代替长距离实时 ready 信号。  
它能安全防止 overflow，但不能自动保证高吞吐，更不能自动避免死锁。AI NoC 中很多看似“算力没打满”的问题，最后会在 credit/backpressure 链条上找到根源。
