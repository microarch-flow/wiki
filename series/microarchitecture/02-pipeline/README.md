# 流水线、时序与时钟域

<span class="micro-legacy-anchor" id="04-时钟与流水"></span>


本章解释寄存器如何定义采样边沿、流水化如何改变路径和事务时序，以及反馈依赖为何限制调度。时钟频率、启动间隔（II）和请求延迟是不同的量。

## 阅读顺序

1. [电路与时序基础](./electrical-timing-foundations.md)：电平、充放电、寄存器与延迟。
2. [时钟同步](./global-clock-synchronization.md)：时钟域、setup 与 hold、PVT 和路径边界。
3. [Pipeline register 插入](./pipeline-register-insertion.md)：前馈切分、延迟、II、面积与功耗。
4. [反馈环的时钟约束](./feedback-loop-clock-constraint.md)：递推依赖、多累加器及全域路径约束。
5. [频率 ≠ 吞吐](./frequency-is-not-throughput.md)：单位时间的有效工作量还受并行度、利用率和资源竞争限制。
6. [停顿与反压](./stalls-and-backpressure.md)：下游不接收时，如何保持数据与控制状态。

同一域要检查所有有效 setup 路径，并单独检查 hold；跨域传输要按接口与 CDC 机制处理。示例数字只是计算假设，不替代时序签核。
