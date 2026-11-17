# 数值格式与运算数据通路

<span class="micro-legacy-anchor" id="02-datapath-基础"></span>


本章讨论乘加电路、数据格式和操作数选择。门数代理、综合面积和运行时数据流量是不同的量。

## 阅读顺序

1. [从逻辑门搭出 MAC](./multiply-accumulate-from-gates.md)：部分积与累加。
2. [压缩树与进位结构](./dadda-and-adder-trees.md)：部分积归约和末级加法。
3. [乘法位宽与实现](./quadratic-bitwidth-scaling.md)：`p×q` 结构代理及其边界。
4. [AI 数字格式](./number-formats-for-ai.md)：元素位字段、MX 共享 scale 和块存储。
5. [mux 与数据移动](./mux-and-data-movement-cost.md)：选择网络和示意面积代理。


继续阅读 [并行执行与计算阵列](../04-parallel-execution/README.md)，比较特定边界的数据复用。
