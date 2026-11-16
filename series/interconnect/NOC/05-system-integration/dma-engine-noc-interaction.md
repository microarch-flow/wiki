# DMA 与 NoC：请求窗口怎样影响流量？

上级：[05 端点与系统集成](./README.md)

相关：[网络接口 NI](./ni-network-interface-design.md)、[NoC 与存储系统](./noc-meets-memory-system.md)、[DMA：调度、Outstanding 与回包](../../../microarchitecture/DMA/wiki/03-dma-microarchitecture/scheduling-outstanding.md)

<span id="dma-engine-noc-interaction"></span><span id="这页在回答什么问题"></span>DMA 将搬运需求组织成请求、数据和响应。它的窗口、粒度和发起节奏会影响网络流量；网络和目的端的反压也会反过来限制 DMA。

## 一次搬运包含什么

<span id="dma-真正在决定什么"></span>一种读回填流程是：DMA 接收命令、发起存储读请求，等待返回数据，再交付给目的缓冲。写出流程可能有不同的数据和响应路径。描述符读取、地址翻译、完成上报和错误处理是否存在，取决于设备接口。

<span id="request-和-response-必须一起看"></span>请求已发出不表示返回资源可用；数据到达 NI 也不自动表示本地 SRAM 已接纳。分析时分别记录请求被接纳、返回数据交付、窗口槽释放和设备 completion 的事件。

## Outstanding 窗口与吞吐上限

<span id="outstanding-window-不是越大越好"></span>构造一个稳定读流：每笔完成请求返回 256 B 有效数据；从占用槽到释放槽的平均时间为 200 ns；最多有 W 笔请求同时占槽。令其他资源的有效容量为 C，则长期平均吞吐满足：

> 有效吞吐 ≤ min(C，W × 256 B ÷ 200 ns)。

| 在途槽 W | 窗口给出的上限 |
| --- | --- |
| 4 | 5.12 GB/s |
| 25 | 32 GB/s |

因此，在这些假设下，要达到 32 GB/s 至少需要 25 个槽。它不是达到目标的充分条件：请求生成、重排缓冲、memory、返回链路和接收端仍要提供足够服务。平均在途时间可能随负载变化；本例不是某款 DMA 或 HBM 的实测值。[AMD：吞吐、延迟与在途事务](https://docs.amd.com/r/en-US/pg313-network-on-chip/Throughput-Latency-and-Outstanding-Transactions)

<span id="burst-size-也不是越大越好"></span>更大的 burst 可能摊薄固定开销，也可能增加非抢占占用或返回突发。burst、网络 packet 和 flit 是不同层的单位；拆分规则取决于地址边界和接口限制。改变大小后应同时比较吞吐、关键事务等待和缓冲压力。

## 同样的总量，不同的峰值

<span id="dma-为什么会制造假网络问题"></span>假设两个 DMA stream 都要发送 8 个 flit，目标路径共用一条每拍可服务 1 flit 的链路。若两者同时在最初 8 拍各提出 1 flit，而链路持续可用，合计提出 16 flit、最多服务 8 flit，至少 8 flit 需要在后续等待或被反压。若将两个 stream 分别安排在拍 0–7 和 8–15，且没有其他流量，则此链路不因两者同拍到达而积压。

这是指定流量和理想链路下的比较；错峰可能延迟其中一个 stream，也不能消除其他路径或端点的竞争。

<span id="它和-qos-的关系"></span><span id="它和-local-memory-的关系"></span>优先级、限速、独立队列或网络都是候选机制。是否值得采用，取决于描述符、响应和 bulk 流的依赖，以及 SRAM bank、接收队列与共享链路的实际服务条件；高优先级本身不构成完成时间保证。

<span id="一个工程上更实用的判断方式"></span><span id="建模启示"></span>比较方案时固定数据量和观察边界，记录每条流的发起与接纳节奏、在途槽占用、响应延迟、目的端阻塞和任务完成时间。链路不满可能是供给不足，也可能是返回或端点阻塞；需结合队列与事件区分。

<span id="一句话理解"></span>DMA 窗口影响可隐藏的延迟，发起节奏影响峰值；两者都要与网络和端点资源一起分析。
