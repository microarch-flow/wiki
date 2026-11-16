# 延迟、吞吐与饱和：数字从哪里开始，到哪里结束？

<span id="metrics-latency-throughput-saturation"></span>

上级：[08 性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)；原章节：[07 Evaluation Methodology](./README.md)

相关：[流量模式与表征](../05-system-integration/traffic-patterns-and-characterization.md)、[性能界与瓶颈分析](./performance-bounds-and-bottlenecks.md)、[Stall 分类与归因](./stall-taxonomy-and-attribution.md)

<span id="这页在回答什么问题"></span><span id="指标不是越多越好"></span>评估首先要固定对象和观察边界。相同网络可以同时有较高的链路吞吐、较长的尾延迟，以及较慢的工作负载完成时间；这些数字回答不同问题。

## 先定义事件和时间窗口

<span id="固定计量边界"></span>对一个 packet，可记录以下事件：

> 释放 → 首 flit 注入 → tail 网络到达 → 最后数据被 consumer 接收

释放前等待依赖、释放后等待注入、网络内传输、目的端等待消费是不同区间。这里把网络延迟定义为首 flit 注入到 tail 到达，端点等待定义为 tail 到达到最后数据被接收；其他定义也可以使用，但比较时必须给出各自起止事件。事务协议完成可能还需要其他响应，不能自动等同于 consumer 接收。

在窗口 [t₀, t₁) 内，可以分别统计释放速率（offered load）、成功注入速率和 consumer 交付速率。工具对 offered、accepted 等名称的定义可能不同，应先核对其边界。按**首 flit 注入事件**给整个 packet 的 payload 记账，是一种 packet 口径；它不等于该窗口在链路上实际传输的字节。链路计数还可能包含 header、padding 和重传；跨多条链路的字节分别累加得到 byte-hop。比较时注明 B/s、packet/cycle 或 flit/cycle，以及时钟、packet 和 flit 大小。

## 延迟和吞吐都要分对象

<span id="latency-要看分布不只看平均"></span>平均延迟会掩盖少数长等待。按目标分别记录平均值、分位数、最大已完成值和各类别的样本数。P99 是指定样本中的统计量，不是最坏情况保证。

如果只统计窗口内已经完成的请求，缓慢或仍在途的请求会被排除。可以选取窗口内释放的一批请求，跟踪其最终完成；同时报告窗口末未完成数量、等待年龄和超时。若后续 drain 阶段停止了背景注入，排队环境也随之改变，需要在结果中说明。

<span id="throughput-也分层"></span>吞吐也必须带边界：网络可以按目的端到达的 byte/cycle 统计，端点可以按实际消费速率统计，工作负载可以按完成任务数或 token/s 统计。链路繁忙不自动代表任务完成得快。对多播尤其要分开源注入、目的端交付和各链路传输量。

<span id="ai-noc-里特别重要的系统级指标"></span>按问题补充 tile 工作时间、DMA 等待、同步等待或任务完成时间。它们需要相应的计算和端点模型，不能由链路利用率直接推出。

## 怎样观察饱和

<span id="saturation-point-是结构性拐点"></span>在指定流量和资源条件下，逐步增加 offered load，观察成功注入、交付、排队和未完成请求。延迟曲线变陡是线索；若系统持续接纳的服务量不再随需求增长，而相关积压持续增长，更能支持达到服务极限的判断。

要说明积压统计在哪里。对同一对象和同一队列，无丢弃或取消时，期末积压等于期初积压加期间进入量、再减期间离开量；若存在丢弃或取消，也要单独扣除。有限队列可以向上游反压；丢弃、限流和闭环工作负载也可能限制进入系统的流量。此时网络内队列没有持续增长，并不证明全部外部需求得到服务。有限实验只能支持其观察范围内的判断。

<span id="utilization-只是症状不是结论"></span>链路利用率指出资源何时忙，却不能单独解释竞争来源或证明它限制了任务。应联合观察链路方向、队列、端点服务和完成事件。

## 让统计与模型一致

<span id="metric-必须和模型层级绑定"></span>只计算每条边流量的模型可以报告链路负载或容量界，但不能凭空报告逐拍 credit stall。记录模型保留的状态、统计对象、时间窗口和不支持的现象，再比较结果。

稳态实验可设置预热、测量和排空阶段，并报告随机种子及未完成样本；有限工作负载则应保留启动和结束阶段，不能默认把它们丢掉。[BookSim 手册](https://github.com/booksim/booksim2/blob/master/doc/manual.tex)展示了一种预热、采样和排空流程；各工具的具体统计口径仍需核对。

<span id="常见误区"></span><span id="一句话理解"></span><span id="建模启示"></span>先问“统计谁、从哪里到哪里”，再解释平均、尾部和吞吐。更多实验安排见[架构探索与实验设计](./architecture-exploration-loop.md)。
