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

沿用[连续批处理的 A、B 算例](../05-batching-and-scheduling/04-dynamic-shape-batching.md#一个两请求执行例子)，再加入 5 ms 到达的 C。A、B 同时在 0 ms 到达。三条请求的输入长度为 8、3、6，输出长度为 4、2、3。每轮预算为 5 个输入 token。先安排 Decode，再按到达顺序处理 Prefill，同一时刻到达时按输入顺序。Prefill 完成时产生首 token。

每轮构造耗时为：

$$T_{\rm step}=1+0.1N_{\rm prefill}+0.2N_{\rm decode}
+0.001S_{\rm decode}\quad[\mathrm{ms}]$$

$N_{\rm prefill}$、$N_{\rm decode}$ 分别是本轮处理的两类输入 token 数。$S_{\rm decode}$ 是本轮 Decode 请求在执行前已有 KV 位置数之和。系数为教学假设，省略了 Prefill Attention 的历史访问成本以及内核与通信的细节。

### 从轮次算到首 token

下表取自模型输出。“A 第 2 个”表示 A 在本轮结束时新增第 2 个输出 token。

| 轮次 | 开始至结束（ms） | 本轮处理的输入 | 轮末输出 |
|---|---|---|---|
| 1 | 0.000–1.500 | A Prefill 5 | 无 |
| 2 | 1.500–3.000 | A Prefill 3，B Prefill 2 | A 第 1 个 |
| 3 | 3.000–4.308 | A Decode 1，B Prefill 1 | A 第 2 个，B 第 1 个 |
| 4 | 4.308–5.720 | A Decode 1，B Decode 1 | A 第 3 个，B 第 2 个 |
| 5 | 5.720–7.330 | A Decode 1，C Prefill 4 | A 第 4 个 |
| 6 | 7.330–8.530 | C Prefill 2 | C 第 1 个 |
| 7 | 8.530–9.736 | C Decode 1 | C 第 2 个 |
| 8 | 9.736–10.943 | C Decode 1 | C 第 3 个 |

例如第 3 轮开始时，A 有 8 个已缓存位置，轮内有 1 个 Decode token 和 1 个 Prefill token。因此该轮耗时 $1+0.1+0.2+0.001\times8=1.308$ ms。B 到轮末才处理完输入，首 token 的时间是 4.308 ms。

C 在第 4 轮执行中到达，直到 5.720 ms 才入批。它先后处理 4 个和 2 个输入 token，在 8.530 ms 产生首 token。模型内的 TTFT 为 $8.530-5.000=3.530$ ms，其中 0.720 ms 在等待入批。这个模型以请求到达为计时起点，以轮末产生 token 为输出时刻，省略了网络和客户端缓冲。服务压测应采用[客户端的计时定义](../01-request-and-metrics/02-metrics-slo.md#在同一条时间线上定义延迟)。

### 只改变每轮预算

~~~sh
python3 series/inference-runtime/examples/runtime_model.py --token-budget 6
~~~

| 模型结果 | 每轮 5 个 token | 每轮 6 个 token |
|---|---:|---:|
| A 的 TTFT（ms） | 3.000 | 3.100 |
| B 的 TTFT（ms） | 4.308 | 3.100 |
| C 的 TTFT（ms） | 3.530 | 3.530 |
| 最后一个 token 的时刻（ms） | 10.943 | 10.943 |

预算为 6 时，两条请求都能在第 2 轮完成 Prefill。前两轮合计处理 11 个输入 token，比预算为 5 时多处理一个。因此 B 提前一轮产生首 token，A 则多等这一输入 token 在模型中增加的 0.100 ms。两组仍各执行 8 轮、输出 9 个 token。只看最后完成时刻会遗漏这次等待时间的重新分配。

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
