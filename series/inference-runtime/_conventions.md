# 推理运行时写作与建模约定

<div class="inference-legacy-anchors" aria-hidden="true"><span id="写作规范-conventions"></span></div>

本系列遵循仓库的[共同设计规则](https://github.com/microarch-flow/wiki/blob/main/docs/wiki-blog-design-rules.md)。本文件补充推理运行时特有的术语、模型和证据要求。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="1-读者视角贯穿全篇"></span></div>

## 读者与内容范围

面向希望理解推理系统机制的工程读者，以自回归 LLM 为贯穿示例。先解释请求、状态和执行的因果关系，再提供必要的公式与实现接口。通用机制与特定框架行为分开。

不要求读者已经熟悉某个推理框架。模型算法、存储器原理和互连机制有明确主要归属，本系列保留理解当前机制所必需的说明。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-每篇统一结构"></span></div>

## 文章组织

每篇回答一个核心问题，按内容组织章节，不强制使用统一五段模板。重要机制需交代前提、输入、输出、状态和过程，但不必把它们写成同名小节。

专题导读的编号阅读列表决定文章顺序与短标题。正文标题完整说明问题；编号不再编码进全系列的阅读依赖。旧文件名可保留，避免仅为标题变化而移动路径。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="3-术语-terminology"></span></div>

## 术语与身份

术语首次出现时按需要给中文、英文与缩写，后续保持一致。[术语表](glossary.md)维护共用定义；实现特有定义必须注明对象与版本。

系列主例采用一个请求一条生成序列。请求有多个候选输出时，分别记录请求数、生成序列数和本轮输入 token 数。区分软件 KV 块、虚拟地址和硬件物理页，也区分缓存容量、有效载荷和硬件实测流量。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="4-公式-math"></span></div>

## 符号与单位

| 符号 | 含义 | 单位 |
|---|---|---|
| $B_{\rm req}$ | 本轮被选择的请求数 | 个 |
| $N_{\rm tok}$ | 本轮输入 token 数 | token |
| $s_i$ | 序列 i 的可见上下文位置数 | token |
| $L,h_q,h_{kv},d_h$ | 层数、查询头数、KV 头数、头维度 | 计数 |
| $P$ | 参数元素数 | 个 |
| $p_w,p_a,p_{kv}$ | 权重、激活、KV 每元素字节 | byte/元素 |
| $k_{kv}$ | 每位置所有相关层 KV 有效载荷 | byte/token |
| $F,D$ | 工作量、指定边界的数据量 | FLOP、byte |
| $C,BW$ | 指定精度算力、指定路径带宽 | FLOP/s、byte/s |
| $H_{\rm req},H_{\rm tok}$ | 请求命中率、token 加权命中率 | 比例 |

公式使用行内或独立数学排版。每个新符号说明含义、单位与观察边界。FMA 按 2 FLOP 计，除非另有明确说明。GB/TB 为十进制，KiB/GiB 为二进制。

概率分布可局部使用 p、q，但不能与精度字节符号混用。多设备聚合要说明切分、复制、负载均衡和通信条件。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="5-数字纪律-numbers"></span></div>

## 事实、假设与验证

模型结构与硬件规格引用一手来源，注明对象。框架行为引用固定版本源码或注明文档核查日期。论文加速比附带其基线与负载条件，不升级为普遍结论。

构造例子明确标注。参数圆整值不称为精确值。效率系数、分布和流量近似属于模型假设；公式复算通过不等于假设得到实测支持。

区分资源下界、条件时间估计、仿真结果和实测结果。p99 与 goodput 必须来自定义完整的请求集合和统计过程，不能从单步估算直接推出。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="6-交叉引用与状态-linking-status"></span></div>

## 链接与兼容

源码使用可解析的相对链接，专题之间明确主归属。文件移动时同时更新发布映射，保留历史 URL；标题调整时保留旧锚点，并让它落在相关说明或新文入口附近。

维护脚本与历史评审不属于正文导航。系列自检状态、独立技术审阅和目标硬件验收分别记录，不把迁移或构建通过称为性能验收。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="7-语言"></span></div>

## 语言与修订记录

采用简短准确的中文，保持专业术语一致。真实代码使用代码格式，事件关系与公式使用便于阅读的样式。避免未经条件限定的“必然”“无损”“翻倍”。

2026-11-17：按已确认的系列重组方案取消固定五段模板，分离统计与精度符号，并增加资源边界与兼容要求。
