# 约束解码：语法状态、token 掩码与输出边界

<div class="inference-legacy-anchors" aria-hidden="true"><span id="13-约束解码grammar-fsm-json-constrained-decoding"></span></div>

上级：[本专题导读](README.md)

约束解码在每一步限制允许的 token，使生成过程保持在指定语言的合法前缀集合内。它控制格式和语法，不自动保证事实正确，也不能忽略停止条件。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span><span id="机制-mechanism"></span><span id="mask-状态推进热路径"></span></div>

## 从语法状态得到允许集合

设当前解析状态为 $q$，一个 token 解码后的字节序列为 $b(v)$。只有在消费 $b(v)$ 后仍可扩展为合法完整输出时，token $v$ 才应被允许。

运行时生成 token 掩码，将禁止项的 logits 置为负无穷，再执行约定的采样步骤。选定 token 后推进解析状态。EOS 也需要规则：通常只有可接受的完整状态才允许正常结束。

如果约束无解、所有候选被排除或解析器失败，应报告错误，不能任意解除约束后继续声称输出受约束。

## 正则约束与递归语法的差别

有限状态机可以描述正则语言。一般上下文无关文法允许递归嵌套，需要比有限状态更多的能力，例如下推自动机的栈。

JSON 中任意深度的数组嵌套就是直观例子。若人为规定最大深度，状态空间可以被展开为有限规模，但规模和限制必须写明。不能说任意 CFG 都能无代价地编译成普通 FSM。

JSON Schema 还包含具体实现支持的子集。语法结构、字段类型、跨字段关系和业务约束不能统称为同一保证。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="tokenization-对齐真正的硬骨头"></span></div>

## Token 边界不是语法边界

一个 token 可能同时包含引号、冒号和部分字符串；语法元素也可能跨多个 token。逐字符验证后仅检查 token 首字符是不正确的。

例如当前状态期待 `"count":` 后的整数，候选 token 可能包含 `12,`。解析器需要检查整个字节序列，确认逗号在当前位置合法，并推进到后续字段状态。分词器版本和解码规则必须与掩码生成一致。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="让-mask-变便宜从-ov步-到-o1步"></span><span id="两笔成本又是固定成本摊薄"></span><span id="量化与公式-quantification"></span><span id="1-每步有效时间mask-在不在关键路径"></span><span id="2-编译摊薄"></span><span id="3-mask-应用本身廉价贵的是-mask-计算"></span></div>

## 怎样减少每步开销

可预计算与上下文无关的转移或 token 分类，并缓存重复语法状态的掩码；依赖栈或动态上下文的部分仍需运行时判断。

XGrammar 将可预处理部分与上下文相关部分分开，并使用并行与重叠减少开销。这个设计不意味着任意语法的所有步骤都是常数时间。

总成本包括首次编译、掩码计算、CPU/GPU 传递、掩码应用和同步。掩码应用的 FLOP 很少，也不能因此判定它必然不在关键路径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="与架构建模的接口-modeling-interface"></span></div>

## 与推测、停止和流式输出配合

推测解码暂时前进多个候选位置时，需要对应的解析状态；候选被拒绝后，解析器也必须回滚。只回滚 token 列表而保留错误语法状态，会破坏后续生成。

达到输出上限、被取消或超时时，输出可能只是合法前缀，例如尚未闭合的 JSON 对象。服务应区分“正常完整结束”与“截断”，并保留结束原因。

即使 JSON 可解析且符合支持的 schema，字段内容仍可能错误。业务规则需要后续校验，必要时采用有明确定义的重试流程。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="延伸阅读-references"></span></div>

## 验证与来源

测试应覆盖空串、嵌套、转义、Unicode、跨 token 边界、EOS、长度上限和候选回滚，并由独立解析器检查完整结果。比较性能时分别报告首次使用与缓存命中后的开销。

[XGrammar 原论文](https://arxiv.org/html/2411.15100v1)解释带栈状态与 token 处理。[采样管线](sampling-and-stopping.md)定义掩码与其他处理的顺序；[资源生命周期](../08-serving-lifecycle/request-resource-lifecycle.md)处理取消及失败。
