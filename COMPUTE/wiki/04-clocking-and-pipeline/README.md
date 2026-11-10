# 04 · 时钟与流水

本章解释寄存器如何定义采样边沿、流水化如何改变路径和事务时序，以及反馈依赖为何限制调度。时钟频率、启动间隔（II）和请求延迟是不同的量。

1. [时钟同步](./global-clock-synchronization.md)：时钟域、setup 与 hold、PVT 和路径边界。
2. [Pipeline register 插入](./pipeline-register-insertion.md)：前馈切分、延迟、II、面积与功耗。
3. [反馈环的时钟约束](./feedback-loop-clock-constraint.md)：递推依赖、多累加器及全域路径约束。
4. [频率 ≠ 吞吐](./frequency-is-not-throughput.md)：单位时间的有效工作量还受并行度、利用率和资源竞争限制。

同一域要检查所有有效 setup 路径，并单独检查 hold；跨域传输要按接口与 CDC 机制处理。示例数字只是计算假设，不替代时序签核。
