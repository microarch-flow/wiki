# QoS（服务质量）、公平性与 Stall Taxonomy（停顿分类体系）

上级：[建模与评估](./README.md)

相关：[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)、[Credit / Backpressure](../02-router-microarchitecture/credit-backpressure.md)

## 读这页前先统一几个词

- `QoS`：通过隔离、优先级或配额，让关键流量不被其他流量压死
- `fairness`：不同流量长期来看都能拿到合理服务，而不是有人一直抢不到
- `traffic class`：按业务重要性或行为相似性分组后的流量类别
- `latency-sensitive`：对延迟极敏感，小幅排队都会伤系统性能
- `taxonomy`：把复杂现象按稳定标准分门别类，便于定位根因

## 为什么这页必须单独存在

很多 NoC（片上网络）分析在看到”吞吐下降”时就停了。  
但架构探索真正要回答的是：

- 谁被谁压住了
- 为什么压住
- 这是带宽问题、调度问题还是端点问题

没有 QoS、公平性和 stall taxonomy，这些问题就说不清。

## QoS 在 AI NoC 里的真正意义

QoS 不是为了做很花哨的服务等级，而是为了避免错误的阻塞耦合。

最典型的风险是：

- bulk DMA（大块直接内存访问）长时间占路
- control / barrier（屏障同步）被延迟
- memory response 回不来
- producer 或 consumer 因等待关键小消息而整体停住

所以 QoS 的本质，是保证关键流量不被不关键的大流量淹没。

## 一套实用的 traffic class 优先级思路

对 AI dataflow NoC，一个常见且合理的顺序是：

- control / barrier / descriptor（描述符）
- latency-sensitive memory response（延迟敏感的存储响应）
- tile-to-tile stream
- bulk DMA / background traffic

这不是唯一答案，但它表达了一个原则：

影响 pipeline（流水线）forward progress（前向推进）的小消息，通常比吞吐型 bulk data 更值得先保。

## 公平性为什么不能被忽略

只讲优先级，不讲公平性，会带来另一个问题：

- 高优先级流量长期占优
- 低优先级流量被持续饥饿
- 某些 stream 永远得不到足够服务

所以实际设计里常见折中是：

- fixed priority（固定优先级）处理最紧急流量
- round-robin（轮询）/ weighted round-robin（加权轮询）保留长期公平性
- age-based（基于等待时长）避免请求无限期等待

## 你至少要会区分的 stall 类型

### 1. NO_CREDIT

下游没有可用 buffer slot。  
优化方向通常是：

- 加深 buffer
- 降低 destination 阻塞
- 缩短 credit round-trip

### 2. SWITCH_CONFLICT

多个输入争同一个输出，仲裁没赢。  
优化方向通常是：

- 改 arbitration
- 改 traffic class 隔离
- 改 topology 或 placement

### 3. LINK_BUSY

链路本身长期被占用，说明局部带宽不足或路径过于集中。

### 4. EJECTION_BLOCKED

packet（数据包）已经到目的 router（路由器），但本地 NI（网络接口）、FIFO（先入先出队列）、SRAM（静态随机存储）接口不能及时接收。  
这类 stall 很关键，因为它常常伪装成“网络堵了”，实际根因在端点。

### 5. INJECTION_BLOCKED

源端本地队列或注入条件不满足，packet 还没真正进入 NoC。

### 6. ROUTE_BLOCKED

由于 route restriction、VC（虚通道）不可用或下游路径资源限制，当前 packet 无法进入目标通路。

### 7. WAITING_FOR_OTHER_STREAM

这类 stall（停顿）更偏系统级：某个 tile（计算单元）不是被 NoC 单独卡住，而是在等待其他 stream（数据流）、其他 tile 或其他阶段到齐。  
它提醒你：不是所有“算力没打满”都能靠改 NoC 解决。

## 为什么 stall taxonomy 比平均 latency 更重要

因为不同 stall 的根因完全不同：

- `NO_CREDIT` 更像流控/端点问题
- `SWITCH_CONFLICT` 更像局部资源竞争问题
- `EJECTION_BLOCKED` 更像端点消费问题
- `WAITING_FOR_OTHER_STREAM` 更像上层 pipeline 协同问题

如果把这些都混成一个“stall”，优化动作很容易南辕北辙。

## 第一版 simulator 的推荐统计方式

- 每个 flit（流控单元）/ packet 在每周期只归因到一个主 stall reason
- 统计总 stall cycle，也统计 packet 数量
- 分 traffic class（流量类别）统计 stall
- 分 router / link / endpoint 统计 stall

这样你才能回答：

- 哪类消息最容易被压住
- 哪个位置最先出问题
- 是网络竞争还是端点阻塞

## QoS 是否一定要在第一版实现

不一定要做复杂 QoS，但至少应做到：

- control 与 bulk data 的基本隔离
- response 与 request 不互相堵死
- 统计 starvation（饥饿）/ 长尾等待现象

否则很多结果会带明显偏差。

## 一个实用实验

对同一 workload，比较下面两种策略：

- 所有流量同优先级
- control / response 高优先级，bulk DMA 低优先级

如果 end-to-end tokens/s（端到端每秒令牌数）、barrier latency 或 tail latency（尾部延迟）明显改善，就说明 QoS 不是“锦上添花”，而是主约束之一。

## 本页结论

QoS、公平性和 stall taxonomy 的价值，不在于把模型做得更复杂，而在于把性能下降的因果链拆清楚。  
只有把 stall 类型分开，你才能判断应该改 buffer（缓冲）、改仲裁、改端点，还是改 workload mapping（工作负载映射）。
