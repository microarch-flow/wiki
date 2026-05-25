# 写缓冲与 write drain：为什么读优先

上级：[Memory Controller](./README.md)
相关：[命令调度：FR-FCFS 及其变体](./command-scheduling-fr-fcfs.md), [多 master 场景下的 QoS 与公平性](./qos-multi-master-arbitration.md)

## 这页在回答什么问题

为什么很多 DRAM 控制器几乎都会默认“读优先”，并把写请求先积累进 write buffer，等到合适时机再集中排空。更准确地说，这不是经验偏好，而是由读请求的系统敏感度和总线方向切换代价共同推出来的策略。

## 正文

如果只从功能语义上看，读和写似乎都是普通内存请求：一个要把数据取回来，一个要把数据送出去，排队公平一点似乎最合理。真实 DRAM 系统很少这样做。大多数控制器会明显偏向读请求，把写请求先缓存在 write buffer 中，只在写积累到一定程度、或者满足某些时机条件时，才进入所谓 `write drain` 阶段集中服务。这种设计并不是“写不重要”，而是在承认读写在系统影响和总线代价上并不对称。

第一层原因来自 `可见性敏感度`。读请求几乎总是阻塞前台执行——就像外卖骑手等你出餐：你不出菜他就站在那里等，后面的单全堆着；而写请求更像往仓库码货，货先堆在门口也不影响前面做生意。读请求几乎总是直接阻塞前台执行：CPU load miss 读不到数据就卡住流水，GPU wavefront/NPU tile 等不到关键输入就会 stall，DMA 若在为消费侧供数，读不出来也会直接影响下游。写请求则常常有更强的缓冲弹性。很多 store 在进入写队列后，发起核心就可以继续前进；不少 DMA 或外设写也只要缓冲区没满，就不一定立刻要求外存完成。因此，从系统感知角度，读更像“前台阻塞操作”，写更像“后台可延后工作”。这就是“读优先”的第一层根源。

第二层原因来自 `总线方向切换代价`。DRAM 数据总线不是理想双向管道，读数据从 DRAM 送向 controller，写数据则从 controller 送向 DRAM。每次在读和写之间切换，通常都要付出 bus turnaround 的等待窗口，相关 timing 约束会让总线短时间内不能立刻满效率工作。若 controller 完全按请求到达顺序交错服务读写，例如 `R-W-R-W-R-W`，看起来公平，实际上会把大量时间浪费在反复切换方向上。于是更高效的办法往往是：先尽量把一批读做完，再在某个时刻切到写方向，把积累的写一口气排掉。也就是说，write drain 的存在，本质上是在把”频繁的小损失”换成”更少次的大切换”。这和洗碗的道理一样——你可以做一道菜洗一次碗（频繁切换），也可以先把脏碗攒一盆，做完所有菜后一口气洗完（集中排空）。后者每次从做菜切换到洗碗确实要花一小段准备时间，但你只切换一次，而不是十次。

一个极简例子就能看出差别：

```text
Naive interleave:
  R -> turn -> W -> turn -> R -> turn -> W

Write drain style:
  R -> R -> R -> turn -> W -> W -> W
```

后者未必让每一笔写更早完成，但它明显减少了方向切换次数，因此总线有效利用率通常更高。常见误解是认为 write drain 只是“懒得立即写回”；实际上，它是在显式优化共享数据总线的方向开销。

第三层原因来自写请求自身更适合被局部性优化。写请求进入 buffer 后，controller 往往有更多机会观察到它们在 row/bank 上的聚集关系。若多笔写刚好落到相同或相邻 row，集中写出时可以像读一样利用 row locality，把 activate 成本摊薄。因此，write buffer 不只是一个临时停车场，它还给 controller 提供了重排和聚合写事务的窗口。读请求当然也会受益于重排，但它们通常更急，更不适合长时间等待“凑局部性”。

但既然写可以缓，为什么不一直缓下去？因为 write buffer 不是无限的，写请求也不是永远不重要。若长期只偏爱读请求，写队列会逐渐堆满，一旦 buffer 空间逼近阈值，新的写可能无法继续吸收，甚至反过来阻塞前端；某些一致性或同步语义也可能要求写在有限时间内真正落到内存。因此 controller 通常会设定几个触发条件：比如写队列深度超过高水位、当前读请求较少、刷新窗口刚好不敏感、或者需要为后续请求腾出空间。到了这些时刻，就进入 write drain，把一批写尽量连续处理完。

一个简单的状态机可以这样理解：

```text
if read queue busy and write buffer below high watermark:
    prefer reads

if write buffer above high watermark:
    switch to write-drain mode

if write buffer falls below low watermark:
    switch back to read-preferred mode
```

这里最关键的是 `high watermark / low watermark` 这种滞回式设计。没有滞回，controller 可能会在读优先和写排空之间来回抖动，方向切换优势反而被削弱。滞回让“读模式”和“写排空模式”各自能维持一个足够长的片段，从而真的减少 turnaround 次数。

这也解释了为什么 write drain 和 FR-FCFS 常常要一起看。FR-FCFS 在一个模式内部喜欢追 row-hit；write drain 则决定当前整个控制器是偏向服务读还是偏向服务写。两者叠加起来，控制器才会呈现真实行为：平时以读优先、在读模式里尽量吃 row-hit；当写堆太多时，切到写模式、在写模式里也继续利用 row locality。也就是说，write drain 不是替代命令调度，而是在更高层决定“现在该优化哪一类事务”。

写优先策略为什么通常不成立，也就很清楚了。写请求虽然也会影响吞吐，但它们对前台 stall 的直接伤害往往比读低；同时，过于积极地提前排空写会让高敏感读请求在本不必要的时候等待，总体系统体验更差。只有在非常特定的系统目标下，例如某些流式输出设备或写密集后端任务，controller 才可能显著提高写优先级。但对大多数通用处理器和加速器，读优先几乎是默认合理起点。

当然，读优先也不是没有代价。它可能让某些写请求尾延迟很长，也可能在多 master 场景下让写密集流长期处于从属地位。如果系统里有显式的写时限、持久性语义、DMA backpressure 或下游 buffer 满溢风险，controller 就不能简单地把写永远当后台任务。这也是为什么 write drain 最终会和 QoS、仲裁和流量隔离问题连起来：有些写虽然“不是读”，但也未必真的不急。

从建模角度压缩一下，write drain 的本质可以概括成一句话：controller 正在把一个双向共享总线上的混合请求流，重塑成更少方向切换、更多同类聚合的服务序列。它优化的是总线效率和前台感知延迟，但代价是写完成时间分布更不均匀。因此，只要你的模型里还有读写共用的数据总线，就不应该把二者简单视为对称负载。

## 一句话理解

读优先和 write drain 的本质，是利用“读更像前台阻塞、写更像可缓后台任务”这一系统不对称性，再加上减少总线方向切换的硬收益，把请求流重塑成更高效的服务序列。

## 建模启示

在模型里，读写请求不应共享完全相同的调度优先级和代价函数。最少应显式保留 `bus direction state`、`write_buffer_occupancy` 和 `drain threshold`，否则模型无法表达为什么读写交错时有效带宽会明显下降，也无法表达为什么写可以先缓后排。

一个够用的状态草图可以写成：

```text
WriteDrainModel {
  mode: enum { READ_PREF, WRITE_DRAIN }
  write_buffer_occupancy: int
  high_watermark: int
  low_watermark: int
  bus_direction: enum { READ, WRITE, TURNAROUND }
}
```

对应切换逻辑可以写成：

```text
if mode == READ_PREF and write_buffer_occupancy >= high_watermark:
    mode = WRITE_DRAIN

if mode == WRITE_DRAIN and write_buffer_occupancy <= low_watermark:
    mode = READ_PREF
```

如果只关心粗粒度平均性能，可以把 turnaround 折成一个读写切换惩罚；但只要你要分析 tail latency、DMA backpressure 或混合读写 workload，就最好显式保留 `WRITE_DRAIN` 这一模式。因为很多系统不是“写更慢”，而是“写被故意延后到某些时间片集中完成”。
