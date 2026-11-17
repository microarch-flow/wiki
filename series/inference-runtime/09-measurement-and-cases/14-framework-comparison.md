# 沿请求路径阅读 vLLM 与 SGLang

<div class="inference-legacy-anchors" aria-hidden="true"><span id="14-框架对比vllm-vs-sglang-framework-comparison"></span></div>

上级：[本专题导读](README.md)

阅读框架时，先追踪一个请求经过哪些模块，再比较具体数据结构与执行策略。只用“vLLM 是分页、SGLang 是前缀树”概括，会遗漏两者的大部分运行时职责。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span></div>

## 本文固定的阅读版本

本文使用 **vLLM v0.12.0 的 V1 路径**与 **SGLang v0.5.6 的 SRT 路径**作为源码阅读样本，核查日期为 2026-11-17。它们不是“当前最新版”声明，也不是同一硬件上的性能比较。

版本不同可能改变进程划分、默认策略和后端选择。本文只将已核对的源码入口映射到系列中的机制，不声称所有配置都经过同一分支。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism映射矩阵"></span></div>

## 沿同一请求路径对照

| 职责 | vLLM v0.12.0 | SGLang v0.5.6 |
|---|---|---|
| 输入准备与请求状态 | API／引擎入口进入 V1 请求处理 | [TokenizerManager](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/tokenizer_manager.py) |
| 选择本轮工作 | [V1 Scheduler](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/sched/scheduler.py) | [Scheduler](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/scheduler.py) |
| 缓存分配与复用 | [KVCacheManager](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/kv_cache_manager.py)及其协调层 | [RadixCache](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/mem_cache/radix_cache.py)等缓存实现 |
| 设备模型执行 | [GPUModelRunner](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/worker/gpu_model_runner.py) | [ModelRunner](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/model_executor/model_runner.py) |

表中的模块不一定一一对应为进程。调度器文件也可能通过混入类、连接器或后端委派工作，需要继续沿调用关系阅读。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span></div>

## 用三个问题串起源码

第一，收到请求后，哪一处记录已计算位置、已输出位置和停止状态？它决定 Prefill、Decode 和推测候选如何区分。

第二，调度结果怎样表示？沿结果对象找到 token 配额、请求身份、块映射与其他元数据，再跟到模型执行器。这样可以检查“调度允许的工作”是否被执行器按同一语义实现。

第三，结果何时提交、缓存何时释放？重点观察取消、抢占、缓存命中和异步完成分支。只读正常 forward 路径无法理解服务完整性。

可以把[最小批处理例子](../05-batching-and-scheduling/04-dynamic-shape-batching.md)中的 A、B 请求代入这条路径，画出队列、状态和执行计划的变化。这个阅读练习不需要先运行大模型。

## 历史贡献与当前职责分开

PagedAttention 与 RadixAttention 是理解两个项目历史的重要入口，但不构成今天全部功能的互斥分类。所选源码中，两侧都包含调度、模型执行和更广的状态处理；SGLang 的运行时也不能只按前端 DSL 理解。

ONNX Runtime 的 Execution Provider 和 TensorRT 的执行引擎主要解释后端执行层。Triton Inference Server 还提供服务与模型管理机制。比较这些产品前，应先确定比较的是哪一层、哪一种模型和哪条执行路径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与定位-performance-positioning"></span><span id="延伸阅读-references"></span></div>

## 性能比较需要什么证据

固定模型修订、精度、质量目标、硬件、输入与输出长度、到达过程、缓存冷热、并行度和生成参数，再比较延迟、goodput、内存及失败率。

默认配置的差异可以是实际产品体验的一部分，但若要归因到某个机制，就需控制其他变量。没有这样的实验，本文不推荐“某框架普遍更快”。

后续可以按[压测方法](benchmarking-and-profiling.md)添加有完整配置的案例。当前验证范围是源码入口与职责对应，没有运行这两个版本的 GPU 性能测试。
