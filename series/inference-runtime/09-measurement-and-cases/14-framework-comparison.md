# 沿请求路径阅读 vLLM 与 SGLang

<div class="inference-legacy-anchors" aria-hidden="true"><span id="14-框架对比vllm-vs-sglang-framework-comparison"></span></div>

上级：[本专题导读](README.md)

沿着同一个请求看两套实现。先找到调度器选中的工作，再看这份计划怎样变成设备输入，最后看采样结果由谁写回请求。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span></div>

## 本文固定的阅读版本

本文按 **vLLM v0.12.0 的 V1 路径**与 **SGLang v0.5.6 的 SRT 路径**走读。选择单卡文本生成，每个请求一条序列。示例走 vLLM 的普通 `EngineCore.step` 与 SGLang 的 `event_loop_normal`，省略推测解码、重叠调度和 PD 交接。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism映射矩阵"></span></div>

## 沿同一请求路径对照

| 职责 | vLLM v0.12.0 | SGLang v0.5.6 |
|---|---|---|
| 输入准备与请求状态 | [InputProcessor](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/engine/input_processor.py#L510) 生成 `EngineCoreRequest` | [TokenizerManager](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/tokenizer_manager.py#L871) 生成 `TokenizedGenerateReqInput` |
| 选择本轮工作 | [V1 Scheduler](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/sched/scheduler.py) | [Scheduler](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/scheduler.py) |
| 缓存分配与复用 | [KVCacheManager](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/kv_cache_manager.py)及其协调层 | [RadixCache](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/mem_cache/radix_cache.py)等缓存实现 |
| 设备模型执行 | [GPUModelRunner](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/worker/gpu_model_runner.py) | [ModelRunner](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/model_executor/model_runner.py) |

表中的模块不一定一一对应为进程。调度器文件也可能通过混入类、连接器或后端委派工作，需要继续沿调用关系阅读。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span></div>

## 用三个问题串起源码

取[批处理算例](../05-batching-and-scheduling/04-dynamic-shape-batching.md#一个两请求执行例子)中 A 第一次 Decode 的起点。A 已处理 8 个提示位置，Prefill 已经选出首个输出 token $y_1$。现在只跟踪 A。本轮要处理位置 8（从 0 编号）的 $y_1$，写入该位置的 KV，再采样出 $y_2$。两条源码路径使用相同的起点来比较职责，各自如何组批由框架决定。

### vLLM V1 的这一次 Decode

1. **选择工作。** `EngineCore.step` 调用 `schedule`。对 A，待处理的位置数是已知 token 数 9 减去已计算位置数 8。若资源允许，`SchedulerOutput.num_scheduled_tokens` 记录 A 本轮处理 1 个 token。A 已在 worker 登记，`scheduled_cached_reqs` 携带已计算位置数以及有变化时的块表信息。[调度函数](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/sched/scheduler.py#L205) · [调度结果定义](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/sched/output.py#L160)
2. **转换成设备输入。** `execute_model` 把计划交给执行器。`GPUModelRunner._prepare_inputs` 根据本轮 token 数和已计算位置确定输入位置，再从 worker 的批状态中取出 token ID，并按块表确定 KV 写入槽位。A 在这一轮送入的是 $y_1$。模型执行后，普通生成路径通过 `sample_tokens` 得到新 token。[EngineCore.step](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/engine/core.py#L331) · [GPU 输入准备](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/worker/gpu_model_runner.py#L1286)
3. **提交结果。** `update_from_output` 把采样结果与被调度的请求对应，将 $y_2$ 加入 A 的输出历史，并检查停止条件。它随后生成引擎输出，供上游处理。[更新请求输出](https://github.com/vllm-project/vllm/blob/v0.12.0/vllm/v1/core/sched/scheduler.py#L1028)

### SGLang SRT 的这一次 Decode

1. **选择工作。** `event_loop_normal` 调用 `get_next_batch_to_run`。若这轮选中运行中的 Decode 批，`prepare_for_decode` 把上轮选出的 $y_1$ 放入本轮的 `input_ids`，为 A 的新位置申请 KV 槽位，更新序列长度。[调度循环](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/scheduler.py#L967) · [Decode 的批准备](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/schedule_batch.py#L1699)
2. **转换成设备输入。** `run_batch` 从 `ScheduleBatch` 得到 `ModelWorkerBatch`。输入附带请求池索引、序列长度以及新 KV 槽位 `out_cache_loc`。调度器调用模型 worker 的 `forward_batch_generation`，结果中含 A 的 $y_2$。[调度器的执行入口](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/scheduler.py#L1952) · [模型 worker 的批输入](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/schedule_batch.py#L1885)
3. **提交结果。** `process_batch_result` 按 Decode 模式进入 `process_batch_result_decode`。普通采样分支把 $y_2$ 加到 A 的 `output_ids`，检查结束条件。若请求结束，处理函数调用 `release_kv_cache`。`stream_output` 根据流式策略决定何时转发输出。[Decode 的结果处理](https://github.com/sgl-project/sglang/blob/v0.5.6/python/sglang/srt/managers/scheduler_output_processor_mixin.py#L314)

两条路径都把 $y_2$ 提交到生成历史。若 A 继续生成，后续执行把 $y_2$ 当作输入时才会写入它的 KV。结果提交与客户端收到文本之间还隔着[解码与输出](../06-sampling-and-decoding/sampling-and-stopping.md#token文本与流式输出)。取消与迟到结果的处理边界见[请求生命周期](../08-serving-lifecycle/request-resource-lifecycle.md)。

## 历史贡献与当前职责分开

PagedAttention 与 RadixAttention 是理解两个项目历史的重要入口，但不构成今天全部功能的互斥分类。所选源码中，两侧都包含调度、模型执行和更广的状态处理；SGLang 的运行时也不能只按前端 DSL 理解。

ONNX Runtime 的 Execution Provider 和 TensorRT 的执行引擎主要解释后端执行层。Triton Inference Server 还提供服务与模型管理机制。比较这些产品前，应先确定比较的是哪一层、哪一种模型和哪条执行路径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与定位-performance-positioning"></span><span id="延伸阅读-references"></span></div>

## 性能比较需要什么证据

固定模型修订、精度、质量目标、硬件、输入与输出长度、到达过程、缓存冷热、并行度和生成参数，再比较延迟、goodput、内存及失败率。

默认配置的差异可以是实际产品体验的一部分，但若要归因到某个机制，就需控制其他变量。没有这样的实验，本文不推荐“某框架普遍更快”。

本例的证据是固定版本源码。对比这两个版本的 GPU 性能还需要按[压测方法](benchmarking-and-profiling.md)实际测量。
