# 流水线、时序与时钟域

<span class="micro-legacy-anchor" id="04-时钟与流水"></span>


在[点积](../00-overview/microarchitecture-decisions.md)的最后一拍，加法器还在工作。此时乘法器能接下一组输入吗？从这个问题进入流水线，再看寄存器采样、反馈依赖和下游停顿怎样影响每一拍。

## 阅读顺序

1. [下一份运算何时开始](./pipeline-register-insertion.md)　看三级流水线何时接收一组输入、何时交出结果。
2. [电路与时序基础](./electrical-timing-foundations.md)：电平、充放电、寄存器与延迟。
3. [时钟同步](./global-clock-synchronization.md)：时钟域、setup 与 hold、PVT 和路径边界。
4. [反馈环的时钟约束](./feedback-loop-clock-constraint.md)：递推依赖、多累加器及全域路径约束。
5. [频率 ≠ 吞吐](./frequency-is-not-throughput.md)：单位时间的有效工作量还受并行度、利用率和资源竞争限制。
6. [停顿与反压](./stalls-and-backpressure.md)：下游不接收时，如何保持数据与控制状态。

同一域要检查所有有效 setup 路径，并单独检查 hold；跨域传输要按接口与 CDC 机制处理。示例数字只是计算假设，不替代时序签核。
