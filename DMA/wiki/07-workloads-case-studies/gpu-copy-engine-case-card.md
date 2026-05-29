# GPU Copy Engine 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[CPU / GPU / NPU 系统中的 DMA 分工](./cpu-gpu-npu-comparison.md)、[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)

## 这页在回答什么问题

GPU 系统里的 copy engine 和通用 DMA 有什么共性，又为什么它经常被看成更高层的数据通路能力；以及为什么它最值得关注的是“传输和 compute 能否并行”，而不是单独一条 copy 多快。

## 典型系统位置

GPU copy engine 位于 GPU 侧的异步传输引擎，负责 host <-> device、device <-> device、memory staging 等数据搬运，并与 compute queue / stream 并行运行。

## 它通常在解决什么问题

它最核心的职责通常包括：

- 尽量让数据传输与 kernel 执行 overlap
- 把大块搬运从 compute pipeline 中剥离
- 支撑多 stream 并发

这意味着 copy engine 的成功标准不是“单独跑 memcpy 很快”，而是“整体程序执行图里的 copy 不把 compute 路径拖住”。

## 核心机制

典型机制包括：

- copy queue / stream
- 异步提交与 completion / event
- pinned memory / host mapping
- 多 engine 并行

这里最容易被低估的是 host-side 准备和依赖边界。GPU copy engine 看起来很像“只要发个异步 memcpy”，但真正决定收益的是数据准备、stream 依赖和 kernel 边界是否真的允许并行。

## 最常见瓶颈

最常见的问题通常包括：

- host-device 链路受限
- stream 间资源争用
- 数据准备和 kernel 边界不同步
- pinned memory / host 侧映射路径成本

因此 GPU copy engine 的分析通常不能只看带宽曲线，还要看 copy 与 compute 的 overlap 成功率。

## 为什么它比普通 DMA 更像执行图组件

在很多 GPU 软件栈里，copy 已经不是“后台搬一下”的附属动作，而是程序依赖图里的显式节点。它的 completion 会决定哪些 kernel 可以继续，哪些 stream 可以推进，哪些 buffer 可以复用。于是 copy engine 更接近一种异步执行资源，而不是单纯 I/O block。

## 常见误解

常见误解：`copy engine 的价值就是提高 memcpy 带宽`。实际上它更大的价值是把 copy 组织成能与 compute 共存的异步流水。

常见误解：`异步 copy 调了就一定有 overlap`。实际上如果数据准备、stream 依赖或 host 路径没对齐，copy 仍然会串行化。

常见误解：`GPU DMA 和 NPU DMA 只是场景不同`。实际上 GPU 更偏 host/device 异步通路，NPU 更偏片上供数节拍。

## 一句话理解

GPU copy engine 是 DMA 向“异步执行图中的数据通路资源”演化的典型形态，它的价值在于 copy 与 compute 能否真正并行。

## 建模启示

这张案例卡最适合显式保留 copy 节点与 compute 节点的 overlap 关系。

```text
GPUCopyProfile {
  copy_bw
  stream_id
  dependency_edges
  overlap_success_rate
}
```

在 `07-workloads-case-studies` 里，这类结构最适合映射到 `Interaction` 与 `Topology`。若只关心单次 copy，可折叠依赖图；若关心端到端程序时间，就必须保留依赖边和 overlap 状态。
