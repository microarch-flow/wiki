# AXI Burst、对齐与边界

上级：[03 片上总线协议族](./README.md)

相关：[位宽、时钟、Burst 与延迟](../02-fundamentals/width-clock-burst-latency.md)、[AXI Narrow Transfer 与 WSTRB](./axi-narrow-transfer-wstrb.md)

## 这页在回答什么问题

为什么 AXI 的 burst、地址对齐和边界限制会显著影响实现复杂度与实际性能。

## Burst 在换什么

burst 的核心价值是把一串相邻 beat 作为一组事务发出，从而：

- 摊薄地址开销
- 提高链路利用率
- 更适合 memory controller 和 cache line 访问

但 burst 一长，副作用也会更明显：

- 占路时间更长
- 被打断更难
- 错误定位更复杂

## 对齐为什么重要

对齐问题会直接影响：

- 需要几次 beat 才能完成
- 是否需要 byte lane 重组
- slave 是否必须做额外拆分

逻辑上一段连续访问，如果起始地址不对齐，硬件里可能被拆成多段子事务。

## 边界为什么会限制 burst

系统通常不会允许一个 burst 随意跨越某些关键边界。  
常见原因包括：

- decode 区间边界
- page 或保护域边界
- downstream memory / bridge 的限制

所以 master 端常常必须先做拆分，再发多个更小的事务。

## 最常见的工程误判

- “burst 越长越高效”
- “地址连续就一定能合成一个 burst”
- “跨界拆分只是协议格式细节”

实际上 burst 拆分往往直接改变：

- latency
- outstanding 占用
- response 组织
- backpressure 形态

## 一句话理解

AXI burst 的本质是用更大的事务粒度换吞吐，但地址对齐和边界规则会决定这笔交易最终值不值得。
