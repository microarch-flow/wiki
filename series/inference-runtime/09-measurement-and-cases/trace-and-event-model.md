# 从请求 Trace 到可校准的事件模型

上级：[本专题导读](README.md)

请求 Trace 描述外部输入，调度器把输入变成事件，成本模型再给事件赋予时间。三者分开，才能知道预测误差来自哪里。

## Trace 至少需要记录什么

对在线生成，一个最小请求记录包含请求标识、到达时间、输入长度、输出长度或停止规则，以及模型身份。前缀复用实验还需要足以重现共享关系的输入标识或 token；只有长度无法推断命中。

生产采集应按实际需要保存数据，敏感文本可以用保留相等关系的受控标识替代。但不能把所有相同长度都当作相同前缀。

请求到达不等于立即开始执行。事件模型应保留等待、准入、执行、输出和结束之间的因果关系。

## 一个可运行的最小模型

本仓库提供 [runtime_model.py](https://github.com/microarch-flow/wiki/blob/main/series/inference-runtime/examples/runtime_model.py)。在仓库根目录运行：

~~~sh
python3 series/inference-runtime/examples/runtime_model.py
~~~

输入是 A、B、C 三条构造请求，输入长度为 8、3、6，输出长度为 4、2、3，到达时间为 0、0、5 ms。本轮 token 预算为 5，优先 Decode，再按到达顺序处理 Prefill；Prefill 完成时产生首 token。

每轮构造耗时为：

$$T_{\rm step}=1+0.1N_{\rm prefill}+0.2N_{\rm decode}
+0.001S_{\rm decode}\quad[\mathrm{ms}]$$

$S_{\rm decode}$ 是本轮 Decode 请求在执行前已有 KV 位置数之和。系数完全为教学假设；公式没有拟合硬件，也没有完整计算 Prefill Attention、内核和通信。

程序输出每轮开始／结束时间、工作清单、token 事件和请求指标。该输入应产生 8 轮、共 9 个输出 token，最终时间为 10.943 ms。这是模型输出，不是推理实测。

## 先验证事件，再讨论性能

最小模型检查以下不变量：每轮工作不超过预算；请求不能早于到达时间执行；全部输入处理后才能输出首 token；输出数量正确；同一请求的 token 时间严格递增。

例如输出长度为 1 的请求，只需完成 Prefill 并返回首 token，不应再安排一个多余 Decode。若没有请求就绪，时钟跳到下一次到达，而不是制造空转迭代。

这个示例没有容量限制、抢占、缓存、推测、取消或多卡。它用来验证调度与统计边界，不足以预测生产 SLO。后续扩展应逐项加入机制，并增加对应的不变量。

## 从教学模型走向可校准模型

成本表至少可以按阶段、查询 token 数、KV 长度、精度、内核及并行配置索引。对未覆盖形状，要明确插值、外推或回退规则。

先用独立微基准估计执行成本，再用端到端 Trace 检查排队和依赖。不要用同一批服务数据同时拟合所有系数，再把拟合误差称为独立验证。

保留一组未参与拟合的负载。分别报告每轮耗时误差、请求延迟误差、内存峰值和 SLO 达标误差；一个平均效率系数可能无法解释长尾。

## 公式复算与模型能力分开

同目录的 [verify_examples.py](https://github.com/microarch-flow/wiki/blob/main/series/inference-runtime/examples/verify_examples.py)复算 KV、传输、分页、采样与统计例子：

~~~sh
python3 series/inference-runtime/examples/verify_examples.py
~~~

复算通过说明算术与示例定义一致，不说明硬件效率假设成立。[条件算例](15-quantitative-estimation.md)给出这种边界的完整示范。[Transformer 推理扩展研究](https://arxiv.org/abs/2211.05102)可作为分析模型的外部参考。
