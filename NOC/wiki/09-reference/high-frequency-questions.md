# High Frequency Questions

上级：[09 Reference](./README.md)

相关：[Bus Vs Noc Vs Crossbar](../01-overview/bus-vs-noc-vs-crossbar.md)、[Deadlock Livelock Starvation](../04-routing-and-flow-control/deadlock-livelock-starvation.md)

## 这页在回答什么问题

这页回答：如果只想快速找某个高频问题的短答案，而不想立刻重读整章，最先应该记住什么。

## 高频问答

### 1. NoC 是不是“更高级的总线”？

不是。BUS、crossbar、NoC 是三种不同的系统组织方式。NoC 的关键新增维度是路径空间和分布式资源竞争，而不只是“带宽更大”。

### 2. credit 能不能解决 deadlock？

不能。credit 防 overflow，不防循环等待。

### 3. VC 的价值是不是只是提高吞吐？

不是。VC 同时也是：

- HOL blocking 缓解工具
- message class 隔离工具
- deadlock avoidance 工具
- QoS 抓手

### 4. XY routing 为什么这么常见？

因为它简单、可预测、易验证，并且能用固定资源顺序避免一类 routing deadlock。它牺牲的是 path diversity。

### 5. source routing 是不是就不用仲裁了？

不是。source routing 决定路径，资源交汇处仍然需要仲裁。

### 6. adaptive routing 一定更好吗？

不一定。只有在存在真实可用多路径、流量足够动态、验证预算也能承受时，它的收益才明显。

### 7. 为什么 link 利用率不高，系统还是慢？

常见原因是：

- endpoint 吃不动
- ejection blocked
- memory response 在关键路径上
- DMA outstanding 太小

也就是说，瓶颈可能在网络边界，而不是主干链路。

### 8. decode 和 prefill 为什么必须分开讨论？

因为它们对 NoC 提的问题不同：

- prefill 更偏 bulk throughput
- decode 更偏 response-sensitive / memory-centric

### 9. MoE 为什么比 GEMM 更“折磨” NoC？

因为 MoE 更容易出现动态热点、负载偏斜、all-to-all-like dispatch/gather，以及 fairness / adaptive routing 问题。

### 10. AI 芯片为什么经常既要 BUS 又要 NoC？

因为它们分工不同：

- BUS 负责控制语义、状态可见性、boot/debug/fault 闭环
- NoC 负责大规模数据交换

### 11. NoC 模型是不是一上来就该做 cycle-accurate？

不一定。先看问题是否真的需要 flit / credit / arbitration 级解释力。很多一阶结构问题停在 analytical 或 event 层就够。

### 12. 第一版 simulator 最该先验证什么？

先验证最小规则：

- 单包延迟
- credit 返回
- tail 释放
- 输出冲突
- ejection blocked 回压

### 13. QoS 是不是 fixed priority 就够了？

不够。fixed priority 只是 QoS 的一种实现。真正的问题是：

- class 怎么分
- 是否会 starvation
- 是否需要 VC 或物理网络隔离

### 14. 为什么地址映射也会成为 NoC 问题？

因为地址映射最终决定请求落到哪个 tile / SRAM / HBM port，也就决定了热点落点。

### 15. 为什么很多 AI NoC 倾向 deterministic / static scheduling？

因为很多主流量可预知，系统更看重稳定性、可验证性和可复现性，而不是极限灵活性。

## 一句话理解

高频问答的作用是先把方向拨正，再回到对应章节深挖，不是替代正文。

## 建模启示

如果你在做 review、设计讨论或 simulator 评审，这一页很适合当“快速对齐口径”的入口：先看这里，确认没在问错问题，再继续展开。
