# 请求调度：准入、选择、抢占与公平性

<div class="inference-legacy-anchors" aria-hidden="true"><span id="08-调度iteration-循环准入与抢占-scheduling"></span></div>

上级：[本专题导读](README.md)

调度器将等待任务和当前资源状态转换为一次可执行计划。它必须同时保证状态合法、预算可满足，并明确不同请求之间的服务顺序。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="iteration-调度循环"></span></div>

## 一轮调度的输入与输出

输入包括等待队列、活跃请求、已处理位置、输出状态、可用缓存块、执行预算、优先级和截止时间。输出是被选择的请求及 token 范围、状态分配变化，以及需要暂停或结束的请求。

一轮可按以下逻辑推进：

~~~text
处理已完成事件与取消
更新可回收块和请求状态
按策略选择已有可运行请求
为本轮新增状态申请预算
用剩余预算接纳或推进 Prefill
提交执行计划
收到完成事件后提交输出与状态进展
~~~

这是教学伪代码，不规定 CPU 必须阻塞等待设备。异步实现可以流水，但提交与完成之间的状态不能混用。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="准入水位admission-watermark"></span></div>

## 准入是资源承诺

只检查“当前空闲块大于零”不够。一次计划可能需要新 KV、尾块写时复制、推测候选和临时工作区。

保守策略可按输出上限预留增长空间，稳定但容量利用可能较低。动态策略只分配当前所需，允许更多并发，却需要明确内存不足时的等待、抢占或拒绝。准入水位是策略参数，不存在适用于所有引擎的固定百分比。

本轮 token 配额限制工作规模，但不能直接保证耗时。成本估计还需考虑上下文、内核和通信。

## 排序策略改变谁承担等待

FCFS 易解释，但长请求可能阻挡短请求。优先短作业需要长度估计，可能伤害长任务；优先 Decode 可减轻运行中请求的间隔，却可能延后新请求；缓存感知排序可省计算，但可能降低公平性。

可以通过等待时间提升优先级、分级队列、每租户配额或保留部分 Prefill 预算限制饥饿。策略应说明服务目标及可观察的失败条件，而不是只报整体吞吐。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="抢占recompute-vs-swap"></span><span id="量化与公式-quantification"></span><span id="1-recompute-vs-swap-的交叉点与序列长度无关"></span></div>

## 抢占后的恢复路径

暂停请求后，可以保留状态等待，也可以释放设备 KV 并在恢复时重算，或将状态迁移到后备存储。不同框架与版本支持的路径不同，不能把历史 swap 行为写成当前所有引擎的默认值。

比较重算与搬运时，先确定恢复起点。若有效前缀仍在缓存中，只需重算后缀；若没有，则计算量可能包含随长度增长的 Attention 项。

假设一个简化模型中重算时间为 $as+bs^2$，单向恢复为 $\alpha+ks/BW$。只有删除二次项和固定项等额外条件后，两边才都正比于 $s$。因此“交叉点与序列长度无关”不是通用结论。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-抖动thrashing边界"></span></div>

## 防止反复抢占与恢复

如果每次接纳都挤出另一个即将恢复的请求，系统可能大量重复工作，却很少完成请求。观察信号包括高抢占率、高重算 token 比例和低有效输出。

可采用减少准入、限制恢复并发、为恢复留预算、改变抢占对象等措施。其代价是部分请求等待更久，应同时报告 goodput 与公平性。

队列也需要上限。持续到达速率超过可完成速率时，单靠重新排序不能使等待保持有界；应使用背压、拒绝或扩容。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span><span id="延伸阅读-references"></span></div>

## 调度正确性与性能验证

先验证不变量：每个请求的输入位置推进正确；未完成的 KV 不被读取；取消后不新增执行；共享状态仍有引用时不被回收。再测延迟、完成率、抢占与内存。

[vLLM 架构文档](https://docs.vllm.ai/en/latest/design/arch_overview/)给出调度、抢占和 Worker 的实现说明；[固定版本源码入口](../09-measurement-and-cases/14-framework-comparison.md)用于避免把不同版本混为一谈。恢复传输见[KV 分层存储](../04-state-and-memory/tiered-kv.md)，生命周期见[取消与资源回收](../08-serving-lifecycle/request-resource-lifecycle.md)。
