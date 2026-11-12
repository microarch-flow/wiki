# 指标、瓶颈与实验设计

上级：[06 性能建模与调优](./README.md)

相关：[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

看 DMA 性能时，哪些指标值得盯，哪些实验最能快速暴露真正瓶颈；以及为什么只看平均带宽几乎总会把你带偏。

## 平均带宽几乎从来不够

平均带宽之所以诱人，是因为它看起来最像一个“总成绩”。但 DMA 真正把系统拖垮的，经常不是平均值，而是阶段错配和长尾。你可能看到带宽已经不低，系统仍然 stall；也可能看到总字节数搬得很多，但 completion 尾延迟让 queue 深度收益完全出不来。

所以 DMA 的性能评估至少要把“搬了多少”和“什么时候能继续”分开。前者更像 transport throughput，后者更像 system progress。两者只在极少数理想 steady-state 里才接近同一件事。

## 先把延迟边界定义清楚

这页最重要的不是列更多指标，而是先把几个容易混的延迟定义清楚：

- `submit latency`：descriptor 或 command 提交后，到 DMA 真正开始受理或 issue 的时间
- `transfer service time`：首个有效传输发出，到最后一笔数据搬运结束的时间
- `completion visibility latency`：若设备保证指定域的 `transfer_done` 先于通知可见，则量两者时间差；否则分别记录时间点，不假定顺序
- `consumer-ready total latency`：从同一任务 submit 到软件或下游真正可继续的时间；若设备契约提供有序 completion，则 `consumer-ready after completion` 是 completion 可见到 consumer ready 的增量，两者不能同名混算

这些时间边界不能从 AXI B 或 PCIe posted write 自动推断。先固定传输完成的观察域与设备契约，再判断哪些差值可作为延迟。DMA 性能分析如果不先把它们拆开，后面所有“慢”都只会混成一个黑箱。

## 最值得同时看的几类指标

一组足够有判断力的指标，通常至少包括：

- effective bandwidth
- completion latency 分布，而不只是平均值
- tail latency，例如 P95/P99
- outstanding occupancy
- queue depth / completion backlog
- overlap 成功率
- memory / NoC / SRAM 端口利用率

有效带宽统一为测量窗口内在指定观察点完成的有效 payload bytes 除以 wall time（B/s）；offered、accepted、completed 任务/bytes 分别计数。记录 warmup、measurement、drain、时间戳时钟域、超时数及窗口末未完成请求数/年龄。P95/P99 只对已完成样本计算时必须同时报告未完成项，否则最慢任务被排除会虚假改善尾延迟。FIFO full 占比的分母是全部观测周期；有请求因满被拒的 demand-stall 占比要另用请求有效周期或明确定义的对象周期作分母。

这些指标搭配起来看，才能回答“DMA 是没发出去、没回得来、没写得下，还是完成路径没闭环”。单独盯任何一个，基本都会遗漏关键信息。

## 常见瓶颈位置其实很固定

虽然 DMA 系统长得很复杂，但常见瓶颈位置很少是完全随机的，通常落在下面几类：

- software submit 太慢，任务还没把 DMA 喂饱
- descriptor / queue 太浅，latency hiding 不足
- DMA issue 不够激进，outstanding 上不去
- NoC 注入或 return path 堵住
- DDR/HBM return latency 尾部很差
- destination ejection 或 local SRAM port 冲突
- completion 可见性或回收路径拖慢下一轮

真正的价值不在于记住这张表，而在于实验设计时能用最少轮次排掉大类。

## 三组最值得先做的实验

第一组是 `size sweep`。扫任务大小、tile 大小或 packet 大小，观察效率何时从 header/控制开销主导，切到带宽主导。它最适合暴露小事务碎片化和 burst 不足。

第二组是 `outstanding / queue depth sweep`。这组实验用来寻找延迟隐藏与资源饱和的拐点。单槽也可以进入稳定但吞吐较低的状态，只是可能无法覆盖往返时间、无法达到目标带宽。增大窗口可能提高吞吐，也可能在共享资源饱和后增加排队、尾延迟或 completion backlog；结果取决于请求供给、服务速率、负载分布和回收能力。应同时记录吞吐、窗口占用、RTT 分布与 backlog，而不是预设窗口越大一定变差。

第三组是 `concurrency sweep`。单流、双流、多流分别跑，观察 fairness、completion 尾部和局部热点。很多“单流看着没问题，多流突然坏掉”的现象，只有这组实验能暴露。

## 实验设计最容易犯的错

最常见的错误是一次改太多旋钮。比如同时改 tile、burst、queue depth 和 polling 策略，最后根本不知道收益来自哪里。另一个常见错误是只量 steady-state 平均值，不量 warm-up、tail 和 drain，于是双缓冲、moderation、completion 回收一类问题都会被藏掉。

所以 DMA 实验和通用 benchmark 不太一样。你需要的不是“跑一个大分”，而是建立一组最小可解释因果关系。

## 常见误解

常见误解：`平均带宽高就代表 DMA 高效`。实际上 queue 堆积、completion 长尾和 consumer stall 可能已经把系统拖垮。

常见误解：`性能问题主要发生在数据传输阶段`。实际上 submit、completion visibility 和 buffer 回收同样可能是主瓶颈。

常见误解：`实验越综合越接近真实越好`。实际上过于综合的实验常常最难定位因果，先做分解实验更有效。

## 一句话理解

DMA 性能分析要同时量 `搬了多少、多久能搬完、多久软件能继续、多久消费者能继续`，否则很容易把局部高效误判成系统高效。

## 建模启示

这一页最适合定义指标采样点。event-driven 仿真中，至少要为 `submit_ts`、`issue_ts`、`transfer_done_ts`、`completion_visible_ts`、`consumer_ready_ts` 这些时间戳留钩子。

可直接使用的统计结构是：

```text
DMAMetrics {
  bytes_moved
  submit_latency
  service_time
  completion_visibility_latency
  consumer_ready_latency
  tail_percentiles
}
```

在 `06-performance-modeling`、`07-workloads-case-studies` 里，这类指标最适合映射到 `Interaction` 和 `Capability` 的观测层。若只关心粗粒度吞吐，可以省 `consumer_ready_latency`；若关心真实 forward progress，它必须保留。
