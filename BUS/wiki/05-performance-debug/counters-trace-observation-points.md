# Counters、Trace 与观测点设计

上级：[05 性能与调试](./README.md)

相关：[争用、QoS 与可观测性](./contention-qos-observability.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)

## 这页在回答什么问题

如果你有机会给 SoC 或 bus fabric 预埋观测能力，最该布哪些计数器和 trace 点。

## 第一类：吞吐与等待计数

建议至少有：

- 每个 master 的请求接受次数
- 每个 slave 的服务完成次数
- 仲裁等待周期
- response 等待周期

如果要让这些计数器真正可实现，最好把语义钉死：

- `请求接受次数`：地址通道上 `VALID && READY` 的次数
- `backpressure 周期`：`VALID && !READY` 的周期数
- `completion latency`：从请求被接受到最后一个完成 beat/response 返回的周期数
- `服务完成次数`：对读看最后一个返回 beat，对写看最终 response 返回

## 第二类：缓冲与回压计数

建议关注：

- FIFO occupancy high-watermark
- READY 拉低周期
- outstanding 深度峰值
- bridge 阻塞周期

## 第三类：错误与异常计数

建议区分：

- decode error
- slave error
- timeout
- translation / permission fault

## 第四类：trace 点

不是所有东西都要常开 trace，更合理的是在关键节点布点：

- master request 发出
- slave request 接收
- response 返回
- fault / timeout 触发

## 一句话理解

好的 bus observability 不是“尽量全抓”，而是让你能回答 `谁发了、谁堵了、谁没回、谁报错了`。
