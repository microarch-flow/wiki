# NI / DMA / 存储接口

上级：[AI Dataflow 系统视角](./README.md)

相关：[Credit / Backpressure](../02-router-microarchitecture/credit-backpressure.md)

## 读这页前先统一几个词

- `NI`：Network Interface，端点和 NoC 之间的协议转换层
- `injection`：把 packet 从端点送进 NoC
- `ejection`：把 packet 从 NoC 弹出到目的端点
- `reassembly`：把收到的一串 flit 重组成完整 packet 或完整数据块
- `outstanding request`：已经发出但还没收到响应的请求；数量过大时会放大 response 回流压力

## 为什么这一层必须单独拿出来

很多人把 NoC 建成“router + link”就停了，但真正决定系统堵不堵的，常常是端点。

尤其在 AI accelerator 里，下面这些对象都不是被动终点：

- Network Interface（网络接口）
- DMA engine（直接内存访问引擎）
- tile（计算单元）local SRAM（片上静态存储）interface
- HBM（高带宽存储器）/ memory controller port
- destination stream FIFO

## NI 的职责

Network Interface 是 tile 世界（语义层）和 NoC 世界（传输层）之间的翻译层：

```
tile 侧（语义层）            NI                     NoC 侧（传输层）

"读地址 0x1000"  ───────→  打包成 read request     ──→ header + body flit
                           packet：填入源地址、          注入到 router
                           目的地址、消息类型、
                           长度等字段

                           ←── 收到 response             ←── flit 到达
"收到 64B 数据"  ←───────  packet，解包还原为            header + body + tail
                           tile 可消费的数据块            flit 重组为完整 packet
```

具体职责：

- **发送侧打包**：将 tile 的读写请求 / DMA 事务打包成 packet（添加 header、切分为 flit），注入 NoC
- **接收侧解包**：将到达的 flit 重组为完整 packet，还原为 tile 可消费的数据
- **协议转换**：tile 侧可能是 AXI / TileLink 等总线协议，NI 转换为 NoC 的 flit 格式
- **缓冲**：injection FIFO 和 ejection FIFO，吸收 tile 和 NoC 之间的速率差异
- 本地流量分类
- 与 tile FIFO / SRAM / DMA descriptor（描述符）接口对接

### Packet 间的依赖关系不由 NoC 管

NoC 只负责把每个 packet 从源送到目的地，不理解 packet 之间的语义依赖。依赖和顺序由上层保证：

| 层 | 职责 |
|---|---|
| 编译器 / runtime | 规划发送顺序和时序，确保依赖正确 |
| NI / DMA 控制器 | 按编译器指定的顺序发起传输，用 barrier / descriptor 做同步 |
| NoC | 只管转发，不重排、不理解依赖 |
| 目的端 NI | 按 packet 到达顺序交付 tile，或用 tag 让 tile 重组 |

有一个保证：**同一个源、同一个目的、同一个 VC 上的 packet，NoC 保证 FIFO 顺序（先发的先到）。** 因为 wormhole 下同一 VC 的 packet 是串行通过的。但不同源、不同 VC、不同路径的 packet 之间没有顺序保证。

### 片上 NoC 不丢数据

这是和片外网络（以太网、互联网）最本质的区别。以太网交换机 buffer 满了会主动丢包（drop），所以需要 TCP 做重传。片上 NoC 不存在这种场景：

- **credit 机制**保证发送方不会发超过下游 buffer 容量的 flit → 不会因溢出丢包
- 信号在芯片内部走短距离金属线，物理上极可靠
- wormhole 下 flit 一旦进入 router buffer 就被安全存储

所以 NI 的协议层主要处理的是**打包 / 解包 / 重组 / 顺序**，不需要像 TCP 那样做丢失检测和重传。数据完整性在 NoC 层面通过 credit 就已经保证了。

高可靠性场景（如车规级芯片）可能在 link 上加 ECC（纠错码）或 parity（奇偶校验）来应对极罕见的软错误（如宇宙射线位翻转），但消费电子级设计通常不加。

## DMA 的职责

DMA 一般负责：

- 把大块数据在 HBM、SRAM、tile 之间搬运
- 生成 read request / write packet
- 接收 response 并组织回写
- 与编译器或 runtime 计划配合

架构探索里，DMA 的 burst（突发传输）行为经常决定：

- packet 粒度
- memory traffic 峰值
- 是否压住 control 小消息

## 存储接口为什么会反向决定 NoC 行为

NoC 看上去在“搬数据”，但最终数据必须被端点消费。

所以必须显式考虑：

- tile local SRAM bank 冲突
- HBM controller port 带宽
- response reordering 能力
- destination ejection FIFO 深度

只要目的端消费速度下降，NoC backpressure（反压）就会被拉起来。

## 第一版模型里最低限度需要的端点建模

- source injection FIFO
- destination ejection FIFO
- DMA request / response 队列
- tile 消费速率
- memory port 带宽限制

## 一个很实用的工程判断

NoC 的瓶颈不一定在 NoC 内部。  
很多“link 利用率不高但系统还是慢”的情况，本质是：

- destination 消费不动
- response 回不来
- SRAM/HBM 接口节奏不匹配

## NI 注入带宽的量化限制

NI 的注入带宽受限于 local port 与 router 的连接宽度：

```text
NI 最大注入带宽 = link_width × freq

例如:
  link_width = 256 bit, freq = 1 GHz
  NI 最大注入带宽 = 256 bit / cycle = 32 GB/s

如果 tile 产生数据的速率 > 32 GB/s → NI 注入成为瓶颈
如果 tile 产生数据的速率 < 32 GB/s → NI 不是瓶颈
```

但实际有效注入率还要低：

```text
有效注入率 = link_width × freq × (1 - header_overhead) × (1 - credit_stall_ratio)

header_overhead: 每个 packet 的 header flit 不携带有效数据
  假设 5 flit packet: overhead = 1/5 = 20%

credit_stall_ratio: 等待下游 credit 的时间占比
  取决于 buffer depth 和下游拥塞程度

实际有效注入率:
  理想: 32 GB/s × 0.8 = 25.6 GB/s
  中等拥塞: 32 GB/s × 0.8 × 0.7 = 17.9 GB/s
  严重拥塞: 32 GB/s × 0.8 × 0.3 = 7.7 GB/s
```

## DMA Outstanding Window 对有效带宽的影响

DMA 不是发一个请求等回复再发下一个，而是可以同时发出多个请求（outstanding window）。

```text
BW_effective = outstanding_requests × packet_size / RTT

其中:
  outstanding_requests: 同时在途的请求数
  packet_size: 每个请求的数据大小
  RTT: 一个请求从发出到收到 response 的往返时间
```

### 具体数值示例

```text
参数:
  HBM RTT = 200 ns (HBM access latency + NoC round-trip)
  packet_size = 256 B (一个 cache line)
  目标带宽 = 32 GB/s (充分利用一个 NI port)

需要的 outstanding requests:
  outstanding = BW_target × RTT / packet_size
             = 32 GB/s × 200 ns / 256 B
             = 32 × 10⁹ × 200 × 10⁻⁹ / 256
             = 25 个

→ DMA 需要至少 25 个 outstanding read request 才能填满一个 NI port
```

### Outstanding Window 对比

| Outstanding | Effective BW (256B pkt, 200ns RTT) | NI 利用率 |
|---|---|---|
| 1 | 1.28 GB/s | 4% |
| 4 | 5.12 GB/s | 16% |
| 8 | 10.24 GB/s | 32% |
| 16 | 20.48 GB/s | 64% |
| 25 | 32.0 GB/s | 100% |
| 32 | 32.0 GB/s (饱和) | 100% |

关键结论：

- Outstanding window 太小 → NI 空转等 response → 有效带宽远低于链路带宽
- 这是”link utilization 不高但系统很慢”的最常见原因之一
- 建模时必须显式设置 DMA outstanding depth，否则会严重高估实际带宽

### Packet Size 的影响

```text
更大的 packet size 可以减少需要的 outstanding 数:

outstanding = BW_target × RTT / packet_size

packet_size = 256B  → outstanding = 25
packet_size = 1KB   → outstanding = 6.25 ≈ 7
packet_size = 4KB   → outstanding = 1.56 ≈ 2

但大 packet 的代价:
  - 占用链路时间更长（serialization latency）
  - HOL blocking 更严重（大 packet 阻塞后面的小 packet）
  - 对 control 消息的干扰更大
```

## 本页结论

如果不把 NI、DMA 和存储接口纳入模型，你得到的 NoC 结论往往只是”网络空转视角”的结论，而不是系统视角的结论。量化分析表明，NI 注入带宽、DMA outstanding window 和 packet size 这三个端点参数对有效带宽的影响可能比 NoC 内部参数更大——一个 outstanding=4 的 DMA 只能用到链路带宽的 16%，无论 NoC 做得多好。
