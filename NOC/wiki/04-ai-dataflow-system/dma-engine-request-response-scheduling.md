# DMA Engine / Request-Response Scheduling

上级：[AI Dataflow 系统视角](./README.md)

相关：[Memory-Centric NoC](./memory-centric-noc.md)、[KV Cache / Decode Memory Path 深化](./kv-cache-decode-memory-path.md)

## 读这页前先统一几个词

- `request generation`：DMA 何时、以多快节奏发出新请求
- `burst`：一次连续搬运的一段数据
- `outstanding window`：允许同时在外飞行的未完成请求数量
- `response reassembly`：多个响应片段回到 DMA 后，如何重新拼成软件想要的数据块
- `overlap`：计算和数据搬运同时进行，用并行执行来隐藏延迟

## 为什么 DMA 不能只当“搬运器”

在很多 AI accelerator 里，DMA 不只是被动搬数据，它还决定：

- request 发起节奏
- burst（突发传输）粒度
- outstanding（未完成）请求数量
- response 回流压力
- 与 compute / NoC 的 overlap（重叠执行）质量

所以 DMA engine 的行为会直接塑造 NoC traffic。

## DMA 的关键行为对象

至少要关注：

- request generation
- burst scheduling
- outstanding request window
- response reassembly
- writeback / refill sequencing

这些机制共同决定 NoC 上看见的是平滑流量还是突发流量。

## Request-Response Scheduling 为什么重要

如果只看 request，不看 response，你很容易高估系统性能。  
真正影响 forward progress（前进保证）的往往是：

- request 发得太猛，response 回来时挤爆目的端
- request 和 response 混跑，共同堵塞
- DMA 窗口过大，导致 memory node 周期性热点

## Outstanding Window 的 tradeoff

outstanding request 太小：

- memory latency 难隐藏
- overlap 不足

outstanding request 太大：

- response 回流更集中
- memory port 和 NoC 更容易突发拥塞

所以它不是“越大越好”，而是调度参数。

## Burst Size 的 tradeoff

burst 大：

- 吞吐效率高
- header 开销低

但也可能：

- 压住关键小消息
- 拉长占路时间
- 增加 response 回流峰值

burst 小：

- 更灵活
- 更利于混合 traffic

但效率会下降。

## DMA 与 QoS 的关系

常见错误是让 bulk DMA 直接和：

- control
- response
- stream

完全同权混跑。  
这很容易导致：

- barrier（同步屏障）被延迟
- response 被拖慢
- tile（计算单元）等待依赖完成

所以 DMA 行为和 QoS（服务质量）设计必须联动看。

## DMA 与 local memory 的关系

DMA 不只向 NoC 发流量，也会对目的端 local memory system 施压。  
例如：

- refill（回填）写入 cluster SRAM（簇级静态存储）
- writeback 与 compute 读写竞争同一 bank

这说明 DMA 调度不只是 NoC 问题，也是 local memory arbitration 问题。

## 在 simulator 里最少怎么建

第一版建议至少有：

- DMA request queue
- DMA response queue
- outstanding count limit
- burst size parameter
- response completion path

更进一步可以加：

- per-stream DMA channel
- priority / throttle 机制

## 你至少要比较的实验

### 1. Outstanding Window 扫描

观察：

- throughput
- response latency
- hotspot 程度

### 2. Burst Size 扫描

观察：

- bulk efficiency
- tail latency（尾部延迟）
- control / response 是否被放大阻塞

### 3. DMA Throttle on/off

观察：

- 网络更平稳还是更容易堆积
- decode-like 流量是否明显受益

## 最值得看的指标

- request injection rate
- response latency
- outstanding occupancy
- memory port utilization
- ejection blocked（弹出阻塞）
- workload completion time

## 一个实用判断

如果你发现网络周期性出现热点波峰，而不是持续饱和，优先怀疑 DMA burst / scheduling 行为，而不是先怀疑 topology。

## 本页结论

DMA engine / request-response scheduling 的核心，不在于把数据搬得更快，而在于把 memory traffic 组织成不会破坏系统 forward progress 的形状。  
这对 decode、memory-centric 路径和多流并发场景尤其重要。
