# 位宽、时钟、Burst 与延迟

上级：[02 基础对象与事务语义](./README.md)

相关：[仲裁、顺序性与 Backpressure](./arbitration-ordering-backpressure.md)、[AXI Burst、对齐与边界](../03-on-chip-protocol-families/axi-burst-alignment-boundary.md)、[AXI Narrow Transfer 与 WSTRB](../03-on-chip-protocol-families/axi-narrow-transfer-wstrb.md)、[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

为什么 BUS 设计里改动位宽、时钟频率或 burst 参数，看起来只是改了“传输规格”，却会显著改变有效吞吐、尾延迟和实现复杂度。

## 原始带宽只是上限

位宽和时钟频率给出的是**理论最大速度**——就像高速公路的设计通行能力：

`raw_bandwidth = data_width_bytes * clock_frequency`

一条 4 车道高速（64-bit），限速 100km/h（500 MHz），理论上每小时能通过 X 辆车（4 GB/s）。8 车道（128-bit）限速 200km/h（1 GHz），理论通行能力翻四倍（16 GB/s）。但这个数字只说明”每辆车都跑满速、车道永远不空”时的上限——现实中不可能。

有效带宽还要扣掉**各种”不跑车”的时间**：进站检票（地址 phase）、回程确认（response phase）、等红灯（仲裁等待）、前车刹车（backpressure）、过收费站（CDC 同步）、车道变窄（width adapter）、分流合流（burst 边界拆分）。更准确的口径是：

`effective_bandwidth = payload_bytes / total_elapsed_time`

这里的 `total_elapsed_time` 不是”车在路上跑”的时间，而是从”车想上高速”到”车到达目的地并停好”的完整时间。上一页讨论的仲裁、顺序性和 backpressure，都会把这个窗口拉长。

这个公式描述的是单程旅行效率，适合解释”这趟为什么慢”。长期吞吐要看整条高速一天能通过多少车：`sustained_bandwidth = sum(payload_bytes) / observation_wall_time`。两者会给出不同答案：单程可能因为堵车很慢，但一天下来高速总通行量可能还不错。

容易误解：车道数乘限速就是实际通行能力。实际上，位宽乘频率只是物理上限；有效吞吐由”车在跑”的时间占总时间的比例决定。

## Burst 在摊薄固定开销

Burst 的价值就像**拼车**——不是让车跑更快，而是把"叫车、上车、下车"这些固定开销分摊给更多乘客。一个人打车，固定开销（等车 + 上下车）可能比在路上的时间还长；8 个人拼一辆车，同样的固定开销被 8 个人分摊，人均效率大幅提升。

一次 1-beat 访问要付出一次 address（叫车）、一次 arbitration（等车）、一次 response（下车确认）；一次 8-beat burst 仍然只需要叫一次车和确认一次，但车上坐了 8 个人（8 个 data beat）。

下面用一个简化模型说明固定开销如何被摊薄。假设一次访问有 2 cycle 地址/仲裁开销、1 cycle response 开销，数据通路每 cycle 接收 1 beat，且没有额外 backpressure：

| 访问形态 | Payload | 固定开销 | 数据阶段 | 总 cycle | Payload 利用率 |
|---|---:|---:|---:|---:|---:|
| 单 beat | 1 beat | 3 cycle | 1 cycle | 4 cycle | 25% |
| 4-beat burst | 4 beat | 3 cycle | 4 cycle | 7 cycle | 57% |
| 8-beat burst | 8 beat | 3 cycle | 8 cycle | 11 cycle | 73% |

这张表展示的是 burst 的收益来源：固定开销没有消失，只是被更多 payload 平摊。系统里存在长 memory latency 时，对连续、对齐、可合并的访问，burst 还可以改善 memory controller 调度和 cache-line 访问效率；但它同时增加单笔 transaction 的占路时间、buffer 占用和错误定位复杂度。

Burst 长度存在明确权衡——就像拼车人数有个甜点。短 burst（2-3 人拼车）对短途、灵活需求更友好；长 burst（坐满一辆大巴）对长途大批量搬运（DMA、frame buffer、NPU tensor）更高效。但如果强制所有人都等大巴坐满才发车，只想跑两站路的人（MMIO 短请求）就要等很久，而且大巴一旦堵在路上（backpressure），影响的乘客也更多。

容易误解：大巴越大越好（burst 越长越高效）。实际上，长 burst 只是在大批量连续流量下提高载客率；在混合负载下，它会把吞吐收益换成更高尾延迟和更长资源占用——就像在早高峰混合通勤的城市里强制只开大巴，效率反而更差。

## 位宽是在换取并行数据量

位宽就像**车道数**。同样搬 64 箱货物（64 byte cache line），单车道（64-bit）要跑 8 趟，双车道（128-bit）跑 4 趟，四车道（256-bit）只要 2 趟。对大批量搬运来说，加车道就是减少占路时间。

但加车道的代价也很直接：道路面积更大（布线更多），路口更宽更难管理（mux 更大），跨立交穿越更困难（时序收敛更难），养护成本更高（功耗更高）。而且宽路会放大**小车浪费**：如果一辆摩托车（32-bit 寄存器读）独占四车道高速，三条车道空着跑，payload 只用了 4 byte，其余 byte lane 在这次访问里纯粹浪费；写路径还需要 byte enable 或 strobe 指出"这四条车道里哪条上有实际货物"。

宽窄适配会把位宽问题变成事务重组问题。宽 master 访问窄 slave 时，一个 beat 可能被拆成多个下游 beat；窄 master 访问宽 slave 时，bridge 可能选择单次窄写、合并 buffer，或直接用 byte strobe 写入。只有当目标不能直接支持 byte-lane 写入、或者必须保持更宽粒度的原子更新时，read-modify-write 才会进入路径。每一种选择都会改变 latency、response 组织和 backpressure 位置。

容易误解：位宽变宽只会提升性能。实际上，位宽提升的是单个 data beat 的承载量；如果负载以窄 MMIO、小随机访问或跨 width adapter 的访问为主，更宽通路可能只增加面积和时序压力。

## 时钟频率不是免费提升

提高频率就像**提高限速**——听起来车都跑更快了，但实际上要付出代价。限速从 100 提到 200km/h，路面要更平整（时序更紧），弯道要更缓（pipeline stage 更深），安全距离要更长（register slice、skid buffer），加油站要更大（更深 FIFO）。这些改造让车跑得更快了，但每辆车从进站到出站的**最低固定时间**反而增加了——因为安检、进出站流程变多了。

跨时钟域就像**从高速公路下到城市道路**。高速上跑 200km/h 的车流涌入限速 60km/h 的城区，持续通行量最终由城区消化能力决定（fast-to-slow）；反方向看，城区车流上高速时看起来宽裕，但上下匝道（异步 FIFO、同步器）仍有固定开销。而且频率比会造成"突发堵车"：高速上的车流可以短时间填满匝道入口，然后被城区慢慢消化。

一个设计从 500 MHz 提到 1 GHz，如果为了时序收敛多插入 3 级 pipeline，理论带宽翻倍，但每次"进出站"多了 3 个环节。对大货车车队（大块 DMA），这几个环节的开销可以被车队规模摊薄；对只是过站看一眼的摩托车（MMIO poll），每次都要多等 3 个环节，延迟直接暴露给软件。

容易误解：升频只影响吞吐。实际上，升频会改变 pipeline 深度、CDC 结构和 ready/credit 往返时间；它既可能提高 sustained bandwidth，也可能提高单笔访问延迟。

## 延迟由固定时间和排队时间共同组成

延迟不是一个数字，而是一张**旅行账单**：

`latency = request_wait + header_time + data_service_time + queueing_time + response_time`

翻译成人话就是：**等红灯**（仲裁和 backpressure）+ **进站检票**（地址被接受）+ **在路上跑**（数据传输，取决于距离和车速）+ **排队等位**（共享资源争用和顺序约束）+ **签收确认送回**（response 返回）。

这里面的微妙之处在于：**这些参数经常互相矛盾**。拼车（burst）降低人均成本，但一车人要等齐了才走，单程时间更长。加车道（位宽）减少趟数，但可能需要过收费站换小路（width adapter）。提限速（升频）增加通行量，但多加了几个安检站（pipeline），单程固定延迟反而增加。

因此，比较两种 BUS 配置时，不能只问”这条路理论上能跑多快”。更可靠的问题是：实际车流是什么样的（请求大小分布），大卡车多还是小轿车多（连续访问比例），小轿车能不能绕过大卡车（短请求能否绕过长 burst），哪里有收费站（CDC/adapter 在哪），回程会不会被排队规则堵住（response 是否被保序挡住），出口前有多少缓冲车道（buffer 深度）。

## 一句话理解

位宽和时钟决定每个时间窗口最多能搬多少数据，burst 决定固定开销如何被 payload 平摊，而真实延迟取决于这些参数在仲裁、适配、CDC、顺序性和 backpressure 约束下被消耗成多少有效服务时间。

## 建模启示

性能模型不能只保存 `width`、`frequency` 和 `burst_length` 三个标量。至少还要记录 data beat 数、header/response 固定 cycle、仲裁等待、FIFO depth、width adapter 拆分或合并规则、CDC 方向和频率比、burst 边界拆分、payload byte enable 或 strobe 对有效负载的影响。

对吞吐模型，可以把一次访问拆成固定开销和按 beat 计费的服务时间：`total_cycles = fixed_cycles + beat_count / service_rate + wait_cycles`。其中 `beat_count = ceil(payload_bytes / data_width_bytes)` 只是起点；窄传输、未对齐、跨边界和宽窄适配都会改变实际 beat 数。

对延迟模型，需要把平均值和尾部行为分开。长 burst 可以提高 payload 利用率，但在按 burst 保持 grant、下游要求连续服务、或协议边界不允许中途切换的路径上，会形成更长服务窗口；深 FIFO 可以吸收短时抖动，却会增加最坏排队时间；更高频率可以增加服务窗口，却可能用 pipeline 固定延迟交换时序裕量。

对功能模型，位宽和 burst 还影响正确性：byte enable/strobe 是否正确，未对齐访问是否被拆分，burst 是否越过协议或 decode 边界，width adapter 是否保持 response 和 ordering 语义。这些规则如果被性能模型完全省略，吞吐数字可能好看，但解释不了真实系统里的短包抖动、MMIO poll 变慢、DMA 长 burst 压制控制流量等现象。
