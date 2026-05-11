# GPU Copy Engine 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[CPU / GPU / NPU 系统中的 DMA 分工](./cpu-gpu-npu-comparison.md)、[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)

## 这页在回答什么问题

GPU 系统里的 copy engine 和通用 DMA 有什么共性，又为什么它经常被看成更高层的数据通路能力。

## 典型系统位置

- 位于 GPU 侧的异步传输引擎
- 负责 host<->device、device<->device、memory staging 等数据搬运
- 与 compute queue 并行运行

## 它通常在解决什么问题

- 尽量让数据传输与 kernel 执行 overlap
- 把大块 buffer 搬运从 compute pipeline 中剥离
- 服务多 stream 并发

## 核心机制

- copy queue / stream
- 异步提交与 completion
- pinned memory / 映射管理
- 多 engine 并行

## 最常见瓶颈

- host-device 链路受限
- stream 间资源争用
- 数据准备和 kernel 边界不同步

## 最值得抄走的判断

GPU copy engine 的价值不在“能拷贝”，而在于它把传输组织成可与 compute 共存的异步流水线。

## 一句话理解

GPU copy engine 是 DMA 向“任务化异步数据通路”演化的一个典型形态。
