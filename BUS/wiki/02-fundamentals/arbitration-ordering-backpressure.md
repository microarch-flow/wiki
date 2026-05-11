# 仲裁、顺序性与 Backpressure

上级：[02 基础对象与事务语义](./README.md)

相关：[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

为什么很多 BUS 的真实性能问题，最终都不是协议字段本身，而是仲裁、保序和回压策略。

## 仲裁在决定谁先占资源

典型仲裁对象包括：

- address channel
- write data path
- shared slave port
- return path

常见策略包括：

- fixed priority
- round-robin
- weighted round-robin
- QoS 感知仲裁

## 顺序性在决定软件能不能相信结果

不同 BUS 的顺序规则不同，但都要回答：

- 同一个 master 的两个请求是否必须保序
- 读和写之间能否重排
- 不同 ID 的 response 能否乱序返回
- barrier、fence、lock 如何生效

这里的 `barrier / fence / lock` 可以先粗略理解为：  
它们是在 ISA、总线或系统层面约束访问顺序和可见性的机制，用来避免“硬件觉得能重排，软件却以为不能重排”的错位。

如果这层没想清楚，就会出现：

- 看起来“偶发”的软件 bug
- DMA 和 CPU 之间的数据可见性问题
- driver 对完成时机的误判

## Backpressure 是共享系统的必然结果

下游慢时，上游必须知道不能继续推流。  
回压的来源可能是：

- slave 忙
- bridge FIFO 满
- response 未及时取走
- clock domain 适配带来的弹性缓冲耗尽

## 常见误区

- “只要平均带宽够，仲裁不重要”
- “保序只影响 correctness，不影响性能”
- “回压只是波形里的细节”

实际上这三者经常一起决定系统尾延迟和 stall 传播路径。

## 一句话理解

仲裁决定谁先走，顺序性决定结果能不能信，backpressure 决定系统堵了以后会堵到哪里。
