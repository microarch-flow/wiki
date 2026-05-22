# 位宽、时钟、Burst 与延迟

上级：[02 基础对象与事务语义](./README.md)

相关：[仲裁、顺序性与 Backpressure](./arbitration-ordering-backpressure.md)、[AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)、[AXI Narrow Transfer 与 WSTRB](../03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

为什么 BUS 设计里改动位宽、时钟频率或 burst 参数，看起来只是改了“传输规格”，却会显著改变有效吞吐、尾延迟和实现复杂度。

## 原始带宽只是上限

位宽和时钟频率给出的是原始带宽上限：

`raw_bandwidth = data_width_bytes * clock_frequency`

例如 64-bit data path 在 500 MHz 下，每个 cycle 最多传 8 byte，原始带宽是 4 GB/s；128-bit data path 在 1 GHz 下，每个 cycle 最多传 16 byte，原始带宽是 16 GB/s。这个数字只说明“数据通路在每个 cycle 都传满有效 payload”时的上限，不说明系统能持续达到这个上限。

有效带宽还要扣掉事务固定开销和空窗：地址 phase、response phase、仲裁等待、backpressure、CDC 同步、width adapter 拆分或合并、burst 边界拆分、slave service gap。更准确的口径是：

`effective_bandwidth = payload_bytes / total_elapsed_time`

这里的 `total_elapsed_time` 不是 data beat 数，而是从请求获得服务机会到 completion 被消费之间的完整时间窗口。上一页讨论的仲裁、顺序性和 backpressure，都会把这个窗口拉长。

这个公式描述的是单笔或单组事务的有效速率，适合解释“这次访问为什么慢”。长期吞吐要换成观测窗口口径：`sustained_bandwidth = sum(payload_bytes) / observation_wall_time`。两者会给出不同答案：单笔速率会被排队延迟显著拉低，长期吞吐则更能反映系统在稳定流量下的持续服务能力。

容易误解：位宽乘频率就是系统带宽。实际上，位宽乘频率只是数据相位的物理上限；BUS 的有效吞吐由 payload 时间占总时间的比例决定。

## Burst 在摊薄固定开销

Burst 的价值不是让每个 beat 更快，而是把一次地址和调度开销分摊到多个连续 data beat 上。一次 1-beat 访问要付出一次 address、一次 arbitration、一次 response；一次 8-beat burst 仍然只需要一次 request header 和一次事务级 completion，数据阶段却有 8 个 beat。对读路径来说，状态可以随 data beat 返回，但整笔 burst 的闭环要等最后一个 beat 和对应状态都被消费后才成立。

下面用一个简化模型说明固定开销如何被摊薄。假设一次访问有 2 cycle 地址/仲裁开销、1 cycle response 开销，数据通路每 cycle 接收 1 beat，且没有额外 backpressure：

| 访问形态 | Payload | 固定开销 | 数据阶段 | 总 cycle | Payload 利用率 |
|---|---:|---:|---:|---:|---:|
| 单 beat | 1 beat | 3 cycle | 1 cycle | 4 cycle | 25% |
| 4-beat burst | 4 beat | 3 cycle | 4 cycle | 7 cycle | 57% |
| 8-beat burst | 8 beat | 3 cycle | 8 cycle | 11 cycle | 73% |

这张表展示的是 burst 的收益来源：固定开销没有消失，只是被更多 payload 平摊。系统里存在长 memory latency 时，对连续、对齐、可合并的访问，burst 还可以改善 memory controller 调度和 cache-line 访问效率；但它同时增加单笔 transaction 的占路时间、buffer 占用和错误定位复杂度。

Burst 长度存在明确权衡。短 burst 对控制访问、小包流量、低延迟请求更友好；长 burst 对 DMA、frame buffer、NPU tensor 搬运和连续 memory copy 更高效。把所有流量都拉成长 burst，会让短请求排队更久，也会让 backpressure 一次影响更多 beat。AXI 的对齐、4KB 边界和拆分规则会在 [AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md) 中展开。

容易误解：burst 越长越高效。实际上，长 burst 只是在特定连续流量下提高 payload 占比；在共享端口和混合负载下，它会把吞吐收益换成更高尾延迟和更长资源占用。

## 位宽是在换取并行数据量

更宽的数据通路能让同样大小的 payload 用更少 beat 完成。64 byte cache line 在 64-bit 通路上需要 8 个 data beat，在 128-bit 通路上需要 4 个 data beat，在 256-bit 通路上需要 2 个 data beat。对大块连续搬运来说，增加位宽可以直接减少占用窗口。

位宽的代价也很直接：布线更多，mux 更大，跨层级穿越更困难，时序收敛更难，功耗更高。更宽的通路还会放大窄传输的浪费。如果一个 32-bit 寄存器读走 128-bit data path，payload 只使用 4 byte，剩下 byte lane 在这次访问里没有承载有效数据；写路径还需要 byte enable 或 strobe 指出哪些 lane 真正被更新。

宽窄适配会把位宽问题变成事务重组问题。宽 master 访问窄 slave 时，一个 beat 可能被拆成多个下游 beat；窄 master 访问宽 slave 时，bridge 可能选择单次窄写、合并 buffer，或直接用 byte strobe 写入。只有当目标不能直接支持 byte-lane 写入、或者必须保持更宽粒度的原子更新时，read-modify-write 才会进入路径。每一种选择都会改变 latency、response 组织和 backpressure 位置。

容易误解：位宽变宽只会提升性能。实际上，位宽提升的是单个 data beat 的承载量；如果负载以窄 MMIO、小随机访问或跨 width adapter 的访问为主，更宽通路可能只增加面积和时序压力。

## 时钟频率不是免费提升

提高 BUS 时钟可以增加每秒 beat 数，但它会压缩每个 cycle 的组合逻辑预算。更高频率可能迫使互连加入 pipeline stage、register slice、skid buffer 或更深 FIFO；这些结构可以帮助时序收敛，却会增加请求到响应的固定延迟。

跨时钟域时，吞吐和延迟都要重新计算。fast-to-slow 路径会受到慢时钟接收速率限制，持续流量最终由慢域消化能力决定；slow-to-fast 路径峰值看起来更宽裕，但异步 FIFO、同步器和 credit/ready 往返仍会带来固定 cycle 开销。频率比还会让 backpressure 呈现成突发：快域可以短时间填满 FIFO，随后被慢域长期消化能力限制。

一个设计从 500 MHz 提到 1 GHz，如果为了收敛多插入 3 级 pipeline，原始带宽可能翻倍，但单笔寄存器读的固定往返延迟也会增加。对大块 DMA，这个延迟可以被 burst 和 outstanding 隐藏；对同步 MMIO poll loop，这个延迟会直接暴露给软件。

容易误解：升频只影响吞吐。实际上，升频会改变 pipeline 深度、CDC 结构和 ready/credit 往返时间；它既可能提高 sustained bandwidth，也可能提高单笔访问延迟。

## 延迟由固定时间和排队时间共同组成

延迟不是一个单独参数。对一笔 transaction，更有用的拆分是：

`latency = request_wait + header_time + data_service_time + queueing_time + response_time`

`request_wait` 来自仲裁和上游 backpressure；`header_time` 来自地址/control 被接受；`data_service_time` 与 beat 数、位宽和 slave 服务速率有关；`queueing_time` 来自共享资源争用和顺序约束；`response_time` 决定 completion 何时被 master 看见。

Burst 会降低每 byte 固定开销，但增加单笔 transaction 的服务时间。位宽会减少 beat 数，但可能引入 width adapter 拆分、byte lane 浪费或更深 pipeline。升频会增加每秒服务窗口，但可能增加跨域和时序 pipeline 固定延迟。这些参数对“平均吞吐”和“单笔尾延迟”的影响方向并不总是一致。

因此，比较两种 BUS 配置时，不能只问“峰值带宽是多少”。更可靠的问题是：目标流量的请求大小分布是什么，连续访问比例有多高，短控制请求能否绕过长 burst，CDC/adapter 在哪里，response 是否会被保序规则挡住，backpressure 到达 master 前有多少 buffer。

## 一句话理解

位宽和时钟决定每个时间窗口最多能搬多少数据，burst 决定固定开销如何被 payload 平摊，而真实延迟取决于这些参数在仲裁、适配、CDC、顺序性和 backpressure 约束下被消耗成多少有效服务时间。

## 建模启示

性能模型不能只保存 `width`、`frequency` 和 `burst_length` 三个标量。至少还要记录 data beat 数、header/response 固定 cycle、仲裁等待、FIFO depth、width adapter 拆分或合并规则、CDC 方向和频率比、burst 边界拆分、payload byte enable 或 strobe 对有效负载的影响。

对吞吐模型，可以把一次访问拆成固定开销和按 beat 计费的服务时间：`total_cycles = fixed_cycles + beat_count / service_rate + wait_cycles`。其中 `beat_count = ceil(payload_bytes / data_width_bytes)` 只是起点；窄传输、未对齐、跨边界和宽窄适配都会改变实际 beat 数。

对延迟模型，需要把平均值和尾部行为分开。长 burst 可以提高 payload 利用率，但在按 burst 保持 grant、下游要求连续服务、或协议边界不允许中途切换的路径上，会形成更长服务窗口；深 FIFO 可以吸收短时抖动，却会增加最坏排队时间；更高频率可以增加服务窗口，却可能用 pipeline 固定延迟交换时序裕量。

对功能模型，位宽和 burst 还影响正确性：byte enable/strobe 是否正确，未对齐访问是否被拆分，burst 是否越过协议或 decode 边界，width adapter 是否保持 response 和 ordering 语义。这些规则如果被性能模型完全省略，吞吐数字可能好看，但解释不了真实系统里的短包抖动、MMIO poll 变慢、DMA 长 burst 压制控制流量等现象。
